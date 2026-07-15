[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9a-fA-F-]{36}$')]
    [string] $WorkspaceId,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $AccessToken,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $ExpectedRemoteCommit,

    [switch] $Execute,

    [switch] $AllowIncomingOverride,

    [ValidateRange(30, 3600)]
    [int] $TimeoutSeconds = 900
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$FabricApiBase = 'https://api.fabric.microsoft.com/v1'

function Invoke-FabricRequest {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet('GET', 'POST')]
        [string] $Method,

        [Parameter(Mandatory = $true)]
        [string] $Uri,

        [object] $Body
    )

    $headers = @{
        Authorization = "Bearer $AccessToken"
        Accept = 'application/json'
    }

    if ($null -ne $Body) {
        $json = $Body | ConvertTo-Json -Depth 10 -Compress
        return Invoke-WebRequest -Method $Method -Uri $Uri -Headers $headers -ContentType 'application/json' -Body $json -UseBasicParsing
    }

    return Invoke-WebRequest -Method $Method -Uri $Uri -Headers $headers -UseBasicParsing
}

function Get-ResponseHeader {
    param(
        [Parameter(Mandatory = $true)]
        [object] $Response,

        [Parameter(Mandatory = $true)]
        [string] $Name
    )

    $value = $Response.Headers[$Name]
    if ($null -eq $value) {
        return $null
    }
    return [string] $value
}

function Convert-ResponseContent {
    param([Parameter(Mandatory = $true)][object] $Response)

    if ([string]::IsNullOrWhiteSpace([string] $Response.Content)) {
        return $null
    }
    return $Response.Content | ConvertFrom-Json
}

function Wait-FabricOperation {
    param(
        [Parameter(Mandatory = $true)]
        [string] $OperationUri,

        [Parameter(Mandatory = $true)]
        [int] $Timeout
    )

    $deadline = [DateTime]::UtcNow.AddSeconds($Timeout)
    do {
        $response = Invoke-FabricRequest -Method 'GET' -Uri $OperationUri
        $body = Convert-ResponseContent -Response $response
        $state = $null
        if ($null -ne $body) {
            if ($null -ne $body.status) {
                $state = [string] $body.status
            }
            elseif ($null -ne $body.state) {
                $state = [string] $body.state
            }
        }

        if ($response.StatusCode -eq 200 -and $state -in @('Succeeded', 'Completed')) {
            return [pscustomobject]@{ State = 'succeeded'; Response = $response; Body = $body }
        }
        if ($state -in @('Failed', 'Cancelled', 'Canceled')) {
            throw "Fabric operation ended in state '$state'. Inspect the Fabric operation result before retrying."
        }
        if ([DateTime]::UtcNow -ge $deadline) {
            throw "Timed out waiting for Fabric operation after $Timeout seconds. Do not retry blindly; inspect the operation first."
        }

        $retryAfter = Get-ResponseHeader -Response $response -Name 'Retry-After'
        $delay = 15
        if ($retryAfter -match '^[0-9]+$') {
            $delay = [Math]::Max(1, [int] $retryAfter)
        }
        Start-Sleep -Seconds $delay
    } while ($true)
}

function Get-FabricGitStatus {
    $uri = "$FabricApiBase/workspaces/$WorkspaceId/git/status"

    for ($attempt = 0; $attempt -lt 3; $attempt++) {
        $response = Invoke-FabricRequest -Method 'GET' -Uri $uri
        if ($response.StatusCode -eq 200) {
            return Convert-ResponseContent -Response $response
        }
        if ($response.StatusCode -eq 202) {
            $location = Get-ResponseHeader -Response $response -Name 'Location'
            if ([string]::IsNullOrWhiteSpace($location)) {
                throw 'Fabric Git status returned 202 without a Location header.'
            }
            Wait-FabricOperation -OperationUri $location -Timeout $TimeoutSeconds | Out-Null
            continue
        }
        throw "Unexpected Fabric Git status response: HTTP $($response.StatusCode)."
    }

    throw 'Fabric Git status did not return a completed result after polling.'
}

$status = Get-FabricGitStatus
if ($null -eq $status -or [string]::IsNullOrWhiteSpace([string] $status.remoteCommitHash)) {
    throw 'Fabric Git status did not contain a remote commit hash.'
}
if ([string]::IsNullOrWhiteSpace([string] $status.workspaceHead)) {
    throw 'Fabric Git status did not contain a workspace head. Initialize the connection through an approved setup process, not this release helper.'
}
if ([string] $status.remoteCommitHash -ne $ExpectedRemoteCommit) {
    throw "Remote commit mismatch. Expected '$ExpectedRemoteCommit' but Fabric reports '$($status.remoteCommitHash)'."
}

$changes = @()
if ($null -ne $status.changes) {
    $changes = @($status.changes)
}
$conflicts = @($changes | Where-Object { [string] $_.conflictType -eq 'Conflict' })
if ($conflicts.Count -gt 0) {
    throw "Fabric Git status contains $($conflicts.Count) conflict(s). Reconcile the source of truth before synchronization."
}

$result = [ordered]@{
    workspaceId = $WorkspaceId
    expectedRemoteCommit = $ExpectedRemoteCommit
    remoteCommitHash = [string] $status.remoteCommitHash
    workspaceHead = [string] $status.workspaceHead
    changeCount = $changes.Count
    mode = 'planned'
    operationId = $null
    operationStatus = 'planned'
}

if (-not $Execute) {
    $result | ConvertTo-Json -Depth 6
    return
}
if (-not $AllowIncomingOverride) {
    throw 'Execution requires -AllowIncomingOverride because Fabric needs explicit consent to apply incoming Git changes.'
}
if (-not $PSCmdlet.ShouldProcess("Fabric workspace $WorkspaceId", "Update from commit $ExpectedRemoteCommit")) {
    $result | ConvertTo-Json -Depth 6
    return
}

$body = @{
    workspaceHead = [string] $status.workspaceHead
    remoteCommitHash = [string] $status.remoteCommitHash
    options = @{
        allowOverrideItems = $true
    }
}
$updateUri = "$FabricApiBase/workspaces/$WorkspaceId/git/updateFromGit"
$updateResponse = Invoke-FabricRequest -Method 'POST' -Uri $updateUri -Body $body
$result.mode = 'executed'
$result.operationId = Get-ResponseHeader -Response $updateResponse -Name 'x-ms-operation-id'

if ($updateResponse.StatusCode -eq 202) {
    $location = Get-ResponseHeader -Response $updateResponse -Name 'Location'
    if ([string]::IsNullOrWhiteSpace($location)) {
        throw 'Fabric Update From Git returned 202 without a Location header.'
    }
    $operation = Wait-FabricOperation -OperationUri $location -Timeout $TimeoutSeconds
    $result.operationStatus = [string] $operation.State
}
elseif ($updateResponse.StatusCode -eq 200) {
    $result.operationStatus = 'succeeded'
}
else {
    throw "Unexpected Fabric Update From Git response: HTTP $($updateResponse.StatusCode)."
}

$result | ConvertTo-Json -Depth 6
