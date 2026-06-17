<# TESSERA OBSERVER v0.2.6 :: read-only human dashboard #>
param([string]$Root = "$env:USERPROFILE\OneDrive\Desktop\Tessera", [int]$RefreshMs = 1000)
$ErrorActionPreference = "Stop"
$Root = (Resolve-Path $Root).Path
Set-Location $Root
[System.IO.Directory]::SetCurrentDirectory($Root)
$Live = Join-Path $Root "reports\operator_shell\live"
$StatusPath = Join-Path $Live "status.json"
$EventsPath = Join-Path $Live "events.jsonl"
New-Item -ItemType Directory -Force -Path $Live | Out-Null
$Phases = @("REHYDRATE","LOOPBOOK","CHECK","RUN","VALIDATE","LEDGER","PUSH","ROOT","FAIL")
function Sym($S) { switch ($S) { "OK" {"[OK]"} "RUN" {"[RUN]"} "FAIL" {"[FAIL]"} "SKIP" {"[SKIP]"} default {"[...]"} } }
while ($true) {
    $Status = $null
    if (Test-Path $StatusPath) { try { $Status = Get-Content -Raw -Encoding UTF8 $StatusPath | ConvertFrom-Json } catch {} }
    $Events = @()
    if (Test-Path $EventsPath) { try { $Events = @(Get-Content -Encoding UTF8 $EventsPath -Tail 16 | ForEach-Object { $_ | ConvertFrom-Json }) } catch {} }
    Clear-Host
    Write-Host "+------------------------------------------------------------------+"
    Write-Host "| TESSERA LOOPBOOK OBSERVER v0.2.6                                |"
    Write-Host "+------------------------------------------------------------------+"
    Write-Host "| read-only human interface :: worker console runs the code         |"
    Write-Host "+------------------------------------------------------------------+"
    Write-Host "root: $Root"
    Write-Host "time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    Write-Host ""
    if ($Status) { Write-Host ("current: {0,-10} {1,-7} {2}" -f $Status.phase, (Sym $Status.state), $Status.detail) }
    if (-not $Status) { Write-Host "current: waiting for worker..." }
    Write-Host ""
    $Latest = @{}
    foreach ($E in $Events) { $Latest[$E.phase] = $E }
    Write-Host "PHASE BOARD"
    Write-Host "-----------"
    foreach ($P in $Phases) {
        if ($Latest.ContainsKey($P)) { $E=$Latest[$P]; Write-Host ("{0,-10} {1,-7} {2}" -f $P, (Sym $E.state), $E.detail) }
        if (-not $Latest.ContainsKey($P)) { Write-Host ("{0,-10} [...]" -f $P) }
    }
    Write-Host ""
    Write-Host "RECENT EVENTS"
    Write-Host "-------------"
    foreach ($E in $Events) { Write-Host ("{0} | {1,-10} {2,-7} {3}" -f $E.timestamp, $E.phase, (Sym $E.state), $E.detail) }
    Write-Host ""
    if (Test-Path "outputs\runs\latest\certificates\transfer_certificate.json") {
        try {
            $Cert = Get-Content -Raw -Encoding UTF8 "outputs\runs\latest\certificates\transfer_certificate.json" | ConvertFrom-Json
            Write-Host "LATEST CERTIFICATE"
            Write-Host "------------------"
            Write-Host ("claim_ceiling:    {0}" -f $Cert.claim_ceiling)
            Write-Host ("certificate_hash: {0}" -f $Cert.certificate_hash)
        } catch {}
    }
    Write-Host ""
    Write-Host "controls: Ctrl+C closes observer. Worker continues in its own window."
    Start-Sleep -Milliseconds $RefreshMs
}