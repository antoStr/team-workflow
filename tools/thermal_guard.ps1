# Thermal Guard - Script di monitoraggio continuo temperature hardware
# Zero consumo di token - Esecuzione locale continua
param(
    [int]$IntervalSeconds = 1,
    [float]$WarnTemp = 85.0,
    [float]$CriticalTemp = 93.0,
    [string]$LogFile = "thermal_guard.log",
    [string]$StatusFile = "thermal_status.json",
    [string]$AlertFile = "THERMAL_ALERT.json"
)

$Host.UI.RawUI.WindowTitle = "Thermal Guard - Hardware Temperature Monitor"
Write-Host "[Thermal Guard] Avvio monitoraggio sensori ogni $IntervalSeconds secondo/i..." -ForegroundColor Cyan
Write-Host "[Thermal Guard] Soglia Attenzione: $WarnTemp C | Soglia Critica: $CriticalTemp C" -ForegroundColor Yellow

$maxCpu = 0.0
$maxGpu = 0.0
$lastLogTime = [DateTime]::MinValue
$lastAlertPopup = [DateTime]::MinValue

# Verifica disponibilità nvidia-smi
$hasNvidia = $false
try {
    $null = Get-Command "nvidia-smi" -ErrorAction Stop
    $hasNvidia = $true
    Write-Host "[Thermal Guard] GPU NVIDIA rilevata e supportata." -ForegroundColor Green
} catch {
    Write-Host "[Thermal Guard] nvidia-smi non trovato, monitoraggio solo CPU/ThermalZone." -ForegroundColor Yellow
}

function Get-CpuTemp {
    try {
        $tz = Get-CimInstance Win32_PerfFormattedData_Counters_ThermalZoneInformation -ErrorAction Stop
        if ($tz -and $tz.HighPrecisionTemperature) {
            $c = ($tz.HighPrecisionTemperature / 10.0) - 273.15
            return [math]::Round($c, 1)
        }
    } catch {
    }
    return $null
}

function Get-GpuTemp {
    if (-not $hasNvidia) { return $null }
    try {
        $out = & nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits 2>$null
        if ($out) {
            return [float]$out.Trim()
        }
    } catch {
    }
    return $null
}

while ($true) {
    $now = Get-Date
    $cpu = Get-CpuTemp
    $gpu = Get-GpuTemp

    if ($cpu -gt $maxCpu) { $maxCpu = $cpu }
    if ($gpu -gt $maxGpu) { $maxGpu = $gpu }

    $status = "OK"
    $isWarn = ($cpu -ge $WarnTemp) -or ($gpu -ge $WarnTemp)
    $isCrit = ($cpu -ge $CriticalTemp) -or ($gpu -ge $CriticalTemp)

    if ($isCrit) {
        $status = "CRITICAL"
    } elseif ($isWarn) {
        $status = "WARNING"
    }

    # Oggetto stato JSON live
    $statusObj = [PSCustomObject]@{
        Timestamp = $now.ToString("yyyy-MM-dd HH:mm:ss")
        Status = $status
        CPU_Temp_C = $cpu
        GPU_Temp_C = $gpu
        Max_CPU_C = $maxCpu
        Max_GPU_C = $maxGpu
        WarnThreshold_C = $WarnTemp
        CritThreshold_C = $CriticalTemp
    }
    $statusObj | ConvertTo-Json | Set-Content -Path $StatusFile -Encoding UTF8

    # Stampa a video
    $color = "Green"
    if ($status -eq "WARNING") { $color = "Yellow" }
    if ($status -eq "CRITICAL") { $color = "Red" }

    $display = "[$($now.ToString('HH:mm:ss'))] CPU: $cpu C (Max: $maxCpu C) | GPU: $gpu C (Max: $maxGpu C) -> [$status]"
    Write-Host $display -ForegroundColor $color

    # Gestione Allarmi
    if ($isCrit) {
        $alertMsg = "PERICOLO: Temperatura CRITICA rilevata! CPU: $cpu C | GPU: $gpu C a $($now.ToString('HH:mm:ss'))"
        Write-Warning $alertMsg
        
        # Scrivi file allarme
        $statusObj | ConvertTo-Json | Set-Content -Path $AlertFile -Encoding UTF8
        "[$($now.ToString('s'))] ALLERTA CRITICA: CPU=$cpu GPU=$gpu" | Add-Content -Path $LogFile -Encoding UTF8
        
        # Segnale acustico
        try { [console]::Beep(2000, 400) } catch {}

        # Popup asincrono (non blocca il ciclo di monitoraggio)
        if (($now - $lastAlertPopup).TotalSeconds -ge 60) {
            $lastAlertPopup = $now
            try {
                $popupScript = "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('$alertMsg`n`nPremere OK per confermare la presa visione.', 'ALLARME TERMICO CRITICO', [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)"
                Start-Process powershell -ArgumentList "-NoProfile -Command $popupScript" -WindowStyle Hidden
            } catch {}
        }
    } elseif ($isWarn) {
        if (($now - $lastLogTime).TotalSeconds -ge 10) {
            "[$($now.ToString('s'))] ATTENZIONE: Temperature elevate: CPU=$cpu GPU=$gpu" | Add-Content -Path $LogFile -Encoding UTF8
            $lastLogTime = $now
            try { [console]::Beep(1000, 200) } catch {}
        }
    } else {
        # Log periodico ogni 60 secondi in stato normale
        if (($now - $lastLogTime).TotalSeconds -ge 60) {
            "[$($now.ToString('s'))] REGOLARE: CPU=$cpu GPU=$gpu (MaxCPU=$maxCpu MaxGPU=$maxGpu)" | Add-Content -Path $LogFile -Encoding UTF8
            $lastLogTime = $now
        }
    }

    Start-Sleep -Seconds $IntervalSeconds
}
