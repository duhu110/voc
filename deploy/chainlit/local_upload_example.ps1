param(
    [string]$Server = "root@your-server",
    [string]$RemoteRoot = "/home/voc"
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$ManifestPath = Join-Path $PSScriptRoot "UPLOAD_FILES.txt"

Get-Content $ManifestPath | ForEach-Object {
    $RelativePath = $_.Trim()
    if (-not $RelativePath) {
        return
    }

    $LocalPath = Join-Path $RepoRoot $RelativePath
    if (-not (Test-Path $LocalPath)) {
        throw "Missing local path: $LocalPath"
    }

    $RemotePath = "$Server`:$RemoteRoot/$RelativePath"
    $RemoteDir = Split-Path $RelativePath -Parent
    if ($RemoteDir) {
        ssh $Server "mkdir -p '$RemoteRoot/$RemoteDir'"
    }
    scp $LocalPath $RemotePath
}

Write-Host "Upload complete."
