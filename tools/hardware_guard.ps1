# Hardware & Thermal Guard - Remote-Safe Telemetry Daemon
# Zero Token Consumption - Continuous Local Monitoring with Optimized I/O
param(
    [int]$IntervalSeconds = 2,
    [float]$WarnTempCpu = 85.0,
    [float]$CritTempCpu = 93.0,
    [float]$WarnTempGpu = 80.0,
    [float]$CritTempGpu = 88.0,
    [float]$WarnRamPercent = 90.0,
    [float]$CritRamPercent = 96.0,
    [switch]$Silent = $true,  # No acoustic beeps by default (safe for unattended/remote)
    [string]$StatusFile = "hardware_status.json",
    [string]$ThermalStatusFile = "thermal_status.json",
    [string]$AlertFile = "HARDWARE_ALERT.json",
    [string]$LogFile = "hardware_guard.log"
)

$Host.UI.RawUI.WindowTitle = "Hardware Guard - Remote Unattended Monitor"
Write-Host "[Hardware Guard] Avvio monitoraggio hardware globale ogni $IntervalSeconds s..." -ForegroundColor Cyan
Write-Host "[Hardware Guard] Modalita Silenziosa: $Silent (Nessun segnale acustico)" -ForegroundColor Green

$maxCpu = 0.0
$maxGpu = 0.0
$lastWriteTime = [DateTime]::MinValue
$lastLogTime = [DateTime]::MinValue
$lastCpuTemp = 0.0
$lastGpuTemp = 0.0
$lastStatus = "OK"

# Inizializza contatore CPU .NET ad altissime prestazioni (zero carico WMI)
$cpuCounter = $null
try {
    $cpuCounter = New-Object System.Diagnostics.PerformanceCounter("Processor", "% Processor Time", "_Total")
    $null = $cpuCounter.NextValue()
} catch {}

# Verifica disponibilità nvidia-smi
$hasNvidia = $false
try {
    $null = Get-Command "nvidia-smi" -ErrorAction Stop
    $hasNvidia = $true
} catch {}

function Rotate-LogFile([string]$path, [long]$maxBytes = 5MB) {
    if (Test-Path $path) {
        $item = Get-Item $path -ErrorAction SilentlyContinue
        if ($item -and $item.Length -gt $maxBytes) {
            $bak = "$path.old"
            Move-Item -Path $path -Destination $bak -Force -ErrorAction SilentlyContinue
        }
    }
}

function Get-CpuTemp {
    try {
        $tzList = Get-CimInstance Win32_PerfFormattedData_Counters_ThermalZoneInformation -ErrorAction Stop
        if ($tzList) {
            $temps = @()
            foreach ($tz in $tzList) {
                if ($tz.HighPrecisionTemperature) {
                    $temps += (($tz.HighPrecisionTemperature / 10.0) - 273.15)
                }
            }
            if ($temps.Count -gt 0) {
                $maxT = ($temps | Measure-Object -Maximum).Maximum
                return [math]::Round($maxT, 1)
            }
        }
    } catch {}
    return $null
}

function Get-GpuData {
    if (-not $hasNvidia) { return $null }
    try {
        $raw = & nvidia-smi --query-gpu=temperature.gpu,utilization.gpu,utilization.memory,memory.used,memory.total,name --format=csv,noheader,nounits 2>$null
        if ($raw) {
            $parts = $raw.Split(',').ForEach({ $_.Trim() })
            if ($parts.Count -ge 5) {
                return [PSCustomObject]@{
                    Temp = [float]$parts[0]
                    GpuUtil = [float]$parts[1]
                    MemUtil = [float]$parts[2]
                    MemUsedMB = [float]$parts[3]
                    MemTotalMB = [float]$parts[4]
                    Name = if ($parts.Count -ge 6) { $parts[5] } else { "NVIDIA GPU" }
                }
            }
        }
    } catch {}
    return $null
}

function Get-MemoryData {
    try {
        $os = Get-CimInstance Win32_OperatingSystem -ErrorAction Stop
        $totalGB = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
        $freeGB = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
        $usedGB = [math]::Round($totalGB - $freeGB, 2)
        $percent = [math]::Round(($usedGB / $totalGB) * 100, 1)
        return [PSCustomObject]@{
            TotalGB = $totalGB
            UsedGB = $usedGB
            FreeGB = $freeGB
            PercentUsed = $percent
        }
    } catch {}
    return $null
}

function Get-DiskData {
    try {
        $disks = Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Free -gt 0 }
        $list = @()
        foreach ($d in $disks) {
            $freeGB = [math]::Round($d.Free / 1GB, 2)
            $usedGB = [math]::Round($d.Used / 1GB, 2)
            $totalGB = [math]::Round(($d.Free + $d.Used) / 1GB, 2)
            $percent = if ($totalGB -gt 0) { [math]::Round(($usedGB / $totalGB) * 100, 1) } else { 0 }
            $list += [PSCustomObject]@{
                Drive = $d.Name
                FreeGB = $freeGB
                UsedGB = $usedGB
                TotalGB = $totalGB
                PercentUsed = $percent
            }
        }
        return $list
    } catch {}
    return @()
}

function Get-CpuLoad {
    if ($cpuCounter) {
        try {
            return [math]::Round($cpuCounter.NextValue(), 1)
        } catch {}
    }
    return $null
}

while ($true) {
    $now = Get-Date
    $cpuTemp = Get-CpuTemp
    $gpuData = Get-GpuData
    $gpuTemp = if ($gpuData) { $gpuData.Temp } else { $null }
    $mem = Get-MemoryData
    $disks = Get-DiskData
    $cpuLoad = Get-CpuLoad

    if ($cpuTemp -and $cpuTemp -gt $maxCpu) { $maxCpu = $cpuTemp }
    if ($gpuTemp -and $gpuTemp -gt $maxGpu) { $maxGpu = $gpuTemp }

    $status = "OK"
    $alerts = @()

    if ($cpuTemp -and $cpuTemp -ge $CritTempCpu) {
        $status = "CRITICAL"
        $alerts += "CPU Temperatura Critica: $cpuTemp C (Soglia: $CritTempCpu C)"
    } elseif ($cpuTemp -and $cpuTemp -ge $WarnTempCpu) {
        if ($status -ne "CRITICAL") { $status = "WARNING" }
        $alerts += "CPU Temperatura Elevata: $cpuTemp C (Soglia: $WarnTempCpu C)"
    }

    if ($gpuTemp -and $gpuTemp -ge $CritTempGpu) {
        $status = "CRITICAL"
        $alerts += "GPU Temperatura Critica: $gpuTemp C (Soglia: $CritTempGpu C)"
    } elseif ($gpuTemp -and $gpuTemp -ge $WarnTempGpu) {
        if ($status -ne "CRITICAL") { $status = "WARNING" }
        $alerts += "GPU Temperatura Elevata: $gpuTemp C (Soglia: $WarnTempGpu C)"
    }

    if ($mem -and $mem.PercentUsed -ge $CritRamPercent) {
        $status = "CRITICAL"
        $alerts += "RAM Saturata: $($mem.PercentUsed)% utilizzata"
    } elseif ($mem -and $mem.PercentUsed -ge $WarnRamPercent) {
        if ($status -ne "CRITICAL") { $status = "WARNING" }
        $alerts += "RAM Elevata: $($mem.PercentUsed)% utilizzata"
    }

    # Verifica se è necessario scrivere su disco (riduzione usura SSD / delta threshold)
    $shouldWrite = ($status -ne $lastStatus) -or ($alerts.Count -gt 0) -or `
                   (($now - $lastWriteTime).TotalSeconds -ge 10) -or `
                   ([math]::Abs($cpuTemp - $lastCpuTemp) -ge 1.0) -or `
                   ([math]::Abs($gpuTemp - $lastGpuTemp) -ge 1.0)

    if ($shouldWrite) {
        $systemState = [PSCustomObject]@{
            Timestamp = $now.ToString("yyyy-MM-dd HH:mm:ss")
            Status = $status
            Alerts = $alerts
            CPU = [PSCustomObject]@{
                Temp_C = $cpuTemp
                Max_Temp_C = $maxCpu
                LoadPercent = $cpuLoad
                WarnTemp_C = $WarnTempCpu
                CritTemp_C = $CritTempCpu
            }
            GPU = if ($gpuData) {
                [PSCustomObject]@{
                    Name = $gpuData.Name
                    Temp_C = $gpuData.Temp
                    Max_Temp_C = $maxGpu
                    UtilPercent = $gpuData.GpuUtil
                    MemUtilPercent = $gpuData.MemUtil
                    MemUsedMB = $gpuData.MemUsedMB
                    MemTotalMB = $gpuData.MemTotalMB
                    WarnTemp_C = $WarnTempGpu
                    CritTemp_C = $CritTempGpu
                }
            } else { $null }
            RAM = $mem
            Disks = $disks
            SilentMode = [bool]$Silent
        }

        $systemState | ConvertTo-Json -Depth 5 | Set-Content -Path $StatusFile -Encoding UTF8

        # Salva thermal_status.json retrocompatibile
        $legacyThermal = [PSCustomObject]@{
            Timestamp = $now.ToString("yyyy-MM-dd HH:mm:ss")
            Status = $status
            CPU_Temp_C = $cpuTemp
            GPU_Temp_C = $gpuTemp
            Max_CPU_C = $maxCpu
            Max_GPU_C = $maxGpu
            WarnThreshold_C = $WarnTempCpu
            CritThreshold_C = $CritTempCpu
        }
        $legacyThermal | ConvertTo-Json | Set-Content -Path $ThermalStatusFile -Encoding UTF8

        $lastWriteTime = $now
        $lastCpuTemp = $cpuTemp
        $lastGpuTemp = $gpuTemp
        $lastStatus = $status
    }

    # Gestione Allarmi e rotazione log
    if ($alerts.Count -gt 0) {
        $alertObj = [PSCustomObject]@{
            Timestamp = $now.ToString("yyyy-MM-dd HH:mm:ss")
            Severity = $status
            Messages = $alerts
            State = $systemState
        }
        $alertObj | ConvertTo-Json -Depth 5 | Set-Content -Path $AlertFile -Encoding UTF8

        Rotate-LogFile -path $LogFile -maxBytes 5MB
        "[$($now.ToString('s'))] [$status] $($alerts -join ' | ')" | Add-Content -Path $LogFile -Encoding UTF8

        if (-not $Silent) {
            try { [console]::Beep(1500, 300) } catch {}
        }
    } else {
        if (Test-Path $AlertFile) {
            Remove-Item $AlertFile -ErrorAction SilentlyContinue
        }
    }

    Start-Sleep -Seconds $IntervalSeconds
}
