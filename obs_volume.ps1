$obsWebSocketURL = "ws://localhost:4455"
$password = "r0ckXpA5w9uj8Z5f"

function Set-OBS-Volume {
    param ([int]$volume)
    $json = @{
        "request-type" = "SetVolume"
        "source" = "Desktop Audio"
        "volume" = $volume / 100.0
    } | ConvertTo-Json
    Invoke-WebRequest -Uri $obsWebSocketURL -Method POST -Body $json
}

while ($true) {
    $volume = (Get-AudioDevice -Playback).Volume
    Set-OBS-Volume -volume $volume
    Start-Sleep -Seconds 1
}
