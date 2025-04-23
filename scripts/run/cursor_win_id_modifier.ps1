# Set output encoding to UTF-8
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Color definitions
$RED = "`e[31m"
$GREEN = "`e[32m"
$YELLOW = "`e[33m"
$BLUE = "`e[34m"
$NC = "`e[0m"

# Configuration file paths
$STORAGE_FILE = "${env:APPDATA}\Cursor\User\globalStorage\storage.json"
$BACKUP_DIR = "${env:APPDATA}\Cursor\User\globalStorage\backups"
$MACHINE_ID_FILE = "${env:APPDATA}\Cursor\machineid"

# Check administrator privileges
function Test-Administrator {
    $user = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($user)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-Administrator)) {
    Write-Host "${RED}[ERROR]${NC} Please run this script as administrator"
    Write-Host "Right-click the script and select 'Run as administrator'"
    Read-Host "Press Enter to exit"
    exit 1
}

# Display Logo
Clear-Host
Write-Host @"

    ██████╗██╗   ██╗██████╗ ███████╗ ██████╗ ██████╗ 
   ██╔════╝██║   ██║██╔══██╗██╔════╝██╔═══██╗██╔══██╗
   ██║     ██║   ██║██████╔╝███████╗██║   ██║██████╔╝
   ██║     ██║   ██║██╔══██╗╚════██║██║   ██║██╔══██╗
   ╚██████╗╚██████╔╝██║  ██║███████║╚██████╔╝██║  ██║
    ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝

"@
Write-Host "${BLUE}================================${NC}"
Write-Host "${GREEN}   Cursor Device ID Modifier Tool   ${NC}"
Write-Host "${YELLOW}  Follow WeChat Official Account [JianBingGuoZiJuanAI] ${NC}"
Write-Host "${YELLOW}  Share more Cursor tips and AI knowledge (Script is free, join our community for more tips)  ${NC}"
Write-Host "${YELLOW}  [IMPORTANT] This tool is free, if it helps you, please follow [JianBingGuoZiJuanAI]  ${NC}"
Write-Host "${BLUE}================================${NC}"
Write-Host ""

# Get and display Cursor version
function Get-CursorVersion {
    try {
        # Main detection path
        $packagePath = "${env:LOCALAPPDATA}\Programs\cursor\resources\app\package.json"
        
        if (Test-Path $packagePath) {
            $packageJson = Get-Content $packagePath -Raw | ConvertFrom-Json
            if ($packageJson.version) {
                Write-Host "${GREEN}[INFO]${NC} Current installed Cursor version: v$($packageJson.version)"
                return $packageJson.version
            }
        }

        # Alternative path detection
        $altPath = "${env:LOCALAPPDATA}\cursor\resources\app\package.json"
        if (Test-Path $altPath) {
            $packageJson = Get-Content $altPath -Raw | ConvertFrom-Json
            if ($packageJson.version) {
                Write-Host "${GREEN}[INFO]${NC} Current installed Cursor version: v$($packageJson.version)"
                return $packageJson.version
            }
        }

        Write-Host "${YELLOW}[WARNING]${NC} Unable to detect Cursor version"
        Write-Host "${YELLOW}[TIP]${NC} Please ensure Cursor is properly installed"
        return $null
    }
    catch {
        Write-Host "${RED}[ERROR]${NC} Failed to get Cursor version: $_"
        return $null
    }
}

# Get and display version information
$cursorVersion = Get-CursorVersion
Write-Host ""

# Version check
if ($cursorVersion) {
    # Split version into components
    $versionParts = $cursorVersion -split '\.'
    $majorVersion = [int]$versionParts[0]
    $minorVersion = [int]$versionParts[1]
    
    # Check if version is supported (0.49.x or higher)
    if ($majorVersion -eq 0 -and $minorVersion -ge 49) {
        Write-Host "${GREEN}[INFO]${NC} Cursor version v$cursorVersion is supported"
    } else {
        Write-Host "${YELLOW}[WARNING]${NC} Current Cursor version v$cursorVersion may not be fully supported"
        Write-Host "${YELLOW}[INFO]${NC} Recommended version: 0.49.x or higher"
        Write-Host ""
        $continue = Read-Host "Do you want to continue anyway? (Y/N)"
        if ($continue -ne "Y" -and $continue -ne "y") {
            Write-Host "${YELLOW}[INFO]${NC} Operation cancelled by user"
            exit 0
        }
    }
} else {
    Write-Host "${YELLOW}[WARNING]${NC} Unable to detect Cursor version, continuing anyway..."
}

Write-Host ""

# Check and close Cursor processes
Write-Host "${GREEN}[INFO]${NC} Checking Cursor processes..."

function Get-ProcessDetails {
    param($processName)
    Write-Host "${BLUE}[DEBUG]${NC} Getting process details for ${processName}:"
    Get-WmiObject Win32_Process -Filter "name='$processName'" | 
        Select-Object ProcessId, ExecutablePath, CommandLine | 
        Format-List
}

# Define maximum retries and wait time
$MAX_RETRIES = 5
$WAIT_TIME = 1

# Handle process termination
function Close-CursorProcess {
    param($processName)
    
    $process = Get-Process -Name $processName -ErrorAction SilentlyContinue
    if ($process) {
        Write-Host "${YELLOW}[WARNING]${NC} Found running $processName"
        Get-ProcessDetails $processName
        
        Write-Host "${YELLOW}[WARNING]${NC} Attempting to close $processName..."
        Stop-Process -Name $processName -Force
        
        $retryCount = 0
        while ($retryCount -lt $MAX_RETRIES) {
            $process = Get-Process -Name $processName -ErrorAction SilentlyContinue
            if (-not $process) { break }
            
            $retryCount++
            if ($retryCount -ge $MAX_RETRIES) {
                Write-Host "${RED}[ERROR]${NC} Unable to close $processName after $MAX_RETRIES attempts"
                Get-ProcessDetails $processName
                Write-Host "${RED}[ERROR]${NC} Please close the process manually and try again"
                Read-Host "Press Enter to exit"
                exit 1
            }
            Write-Host "${YELLOW}[WARNING]${NC} Waiting for process to close, attempt $retryCount/$MAX_RETRIES..."
            Start-Sleep -Seconds $WAIT_TIME
        }
        Write-Host "${GREEN}[INFO]${NC} $processName successfully closed"
    }
}

# Close all Cursor processes
Close-CursorProcess "Cursor"
Close-CursorProcess "cursor"

# Create backup directory
if (-not (Test-Path $BACKUP_DIR)) {
    New-Item -ItemType Directory -Path $BACKUP_DIR | Out-Null
}

# Backup existing configuration
if (Test-Path $STORAGE_FILE) {
    Write-Host "${GREEN}[INFO]${NC} Backing up configuration file..."
    $backupName = "storage.json.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Copy-Item $STORAGE_FILE "$BACKUP_DIR\$backupName"
}

# Generate new IDs
Write-Host "${GREEN}[INFO]${NC} Generating new IDs..."

# Add random hex generation function
function Get-RandomHex {
    param (
        [int]$length
    )
    
    $bytes = New-Object byte[] ($length)
    $rng = [System.Security.Cryptography.RNGCryptoServiceProvider]::new()
    $rng.GetBytes($bytes)
    $hexString = [System.BitConverter]::ToString($bytes) -replace '-',''
    $rng.Dispose()
    return $hexString
}

# Improved ID generation function
function New-StandardMachineId {
    $bytes = New-Object byte[] 32  # 32 bytes will give us 64 hex characters
    $rng = [System.Security.Cryptography.RNGCryptoServiceProvider]::new()
    $rng.GetBytes($bytes)
    $hexString = [System.BitConverter]::ToString($bytes) -replace '-',''
    $rng.Dispose()
    return $hexString.ToLower()  # ensure lowercase to match original format
}

# Generate IDs using new functions
$MAC_MACHINE_ID = New-StandardMachineId
$UUID = [System.Guid]::NewGuid().ToString()
# Convert auth0|user_ to hex bytes
$prefixBytes = [System.Text.Encoding]::UTF8.GetBytes("auth0|user_")
$prefixHex = -join ($prefixBytes | ForEach-Object { '{0:x2}' -f $_ })
# Calculate remaining length needed after prefix
$remainingLength = 64 - $prefixHex.Length
# Generate remaining hex characters
$randomPart = -join ((1..($remainingLength/2)) | ForEach-Object { '{0:x2}' -f (Get-Random -Minimum 0 -Maximum 256) })
$MACHINE_ID = "$prefixHex$randomPart"
$SQM_ID = "{" + [System.Guid]::NewGuid().ToString().ToUpper() + "}"

# Add administrator privilege check before Update-MachineGuid
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "${RED}[ERROR]${NC} Please run this script with administrator privileges"
    Start-Process powershell "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

function Update-MachineGuid {
    try {
        # Check if registry path exists, create if not
        $registryPath = "HKLM:\SOFTWARE\Microsoft\Cryptography"
        if (-not (Test-Path $registryPath)) {
            Write-Host "${YELLOW}[WARNING]${NC} Registry path does not exist: $registryPath, creating..."
            New-Item -Path $registryPath -Force | Out-Null
            Write-Host "${GREEN}[INFO]${NC} Registry path created successfully"
        }

        # Get current MachineGuid, use empty string as default if not exists
        $originalGuid = ""
        try {
            $currentGuid = Get-ItemProperty -Path $registryPath -Name MachineGuid -ErrorAction SilentlyContinue
            if ($currentGuid) {
                $originalGuid = $currentGuid.MachineGuid
                Write-Host "${GREEN}[INFO]${NC} Current registry value:"
                Write-Host "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Cryptography" 
                Write-Host "    MachineGuid    REG_SZ    $originalGuid"
            } else {
                Write-Host "${YELLOW}[WARNING]${NC} MachineGuid value does not exist, will create new"
            }
        } catch {
            Write-Host "${YELLOW}[WARNING]${NC} Failed to get MachineGuid: $($_.Exception.Message)"
        }

        # Create backup directory (if not exists)
        if (-not (Test-Path $BACKUP_DIR)) {
            New-Item -ItemType Directory -Path $BACKUP_DIR -Force | Out-Null
        }

        # Create backup file (only if original value exists)
        if ($originalGuid) {
            $backupFile = "$BACKUP_DIR\MachineGuid_$(Get-Date -Format 'yyyyMMdd_HHmmss').reg"
            $backupResult = Start-Process "reg.exe" -ArgumentList "export", "`"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Cryptography`"", "`"$backupFile`"" -NoNewWindow -Wait -PassThru
            
            if ($backupResult.ExitCode -eq 0) {
                Write-Host "${GREEN}[INFO]${NC} Registry key backed up to: $backupFile"
            } else {
                Write-Host "${YELLOW}[WARNING]${NC} Backup creation failed, continuing..."
            }
        }

        # Generate new GUID
        $newGuid = [System.Guid]::NewGuid().ToString()

        # Update or create registry value
        Set-ItemProperty -Path $registryPath -Name MachineGuid -Value $newGuid -Force -ErrorAction Stop
        
        # Verify update
        $verifyGuid = Get-ItemProperty -Path $registryPath -Name MachineGuid -ErrorAction Stop
        if ($verifyGuid.MachineGuid -eq $newGuid) {
            Write-Host "${GREEN}[INFO]${NC} Registry value updated successfully:"
            Write-Host "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Cryptography"
            Write-Host "    MachineGuid    REG_SZ    $newGuid"
            return $true
        } else {
            Write-Host "${RED}[ERROR]${NC} Registry value verification failed"
            return $false
        }
    }
    catch {
        Write-Host "${RED}[ERROR]${NC} Failed to update MachineGuid: $($_.Exception.Message)"
        return $false
    }
}

# Update storage.json with new IDs
try {
    Write-Host "${GREEN}[INFO]${NC} Updating configuration..."
    
    # Check if storage.json exists
    if (Test-Path $STORAGE_FILE) {
        $storageContent = Get-Content $STORAGE_FILE -Raw | ConvertFrom-Json
        
        # Create backup of existing files
        $backupFiles = Get-ChildItem -Path $BACKUP_DIR -Filter "storage.json.backup_*"
        if ($backupFiles) {
            foreach ($file in $backupFiles) {
                Write-Host "${GREEN}[INFO]${NC} Found backup: $($file.Name)"
            }
        }
        
        # Create new configuration object with existing and new values
        $newConfig = @{}
        
        # Copy existing properties (excluding ALL telemetry values)
        $storageContent.PSObject.Properties | ForEach-Object {
            if (-not ($_.Name -eq 'telemetry.machineId' -or 
                     $_.Name -eq 'telemetry.sqmId' -or 
                     $_.Name -eq 'telemetry.devDeviceId' -or 
                     $_.Name -eq 'telemetry.macMachineId')) {
                $newConfig[$_.Name] = $_.Value
            }
        }
        
        # Generate new UUID for devDeviceId
        $UUID = [System.Guid]::NewGuid().ToString()
        
        # Add new telemetry values
        $newConfig['telemetry.machineId'] = $MACHINE_ID
        $newConfig['telemetry.sqmId'] = $SQM_ID
        $newConfig['telemetry.devDeviceId'] = $UUID
        $newConfig['telemetry.macMachineId'] = $MAC_MACHINE_ID
        
        # Save updated configuration
        $newConfig | ConvertTo-Json -Depth 10 | Set-Content $STORAGE_FILE -Force
        Write-Host "${GREEN}[INFO]${NC} Configuration updated successfully"
    } else {
        Write-Host "${YELLOW}[WARNING]${NC} storage.json not found, creating new configuration..."
        
        # Create new configuration object
        $newConfig = @{
            'telemetry.machineId' = $MACHINE_ID
            'telemetry.sqmId' = $SQM_ID
            'telemetry.devDeviceId' = $UUID
            'telemetry.macMachineId' = $MAC_MACHINE_ID
        }
        
        # Save new configuration
        $newConfig | ConvertTo-Json -Depth 10 | Set-Content $STORAGE_FILE -Force
        Write-Host "${GREEN}[INFO]${NC} New configuration created successfully"
    }
    
    Write-Host "${GREEN}[INFO]${NC} Please restart Cursor to apply new configuration"
    
    # Ask about auto-update settings
    Write-Host ""
    Write-Host "Would you like to disable auto-update?"
    Write-Host "0) No - Keep default settings (press Enter)"
    Write-Host "1) Yes - Disable auto-update"
    
    $choice = Read-Host "Enter your choice"
    
    if ($choice -eq "1") {
        try {
            $settingsPath = "${env:APPDATA}\Cursor\User\settings.json"
            
            if (Test-Path $settingsPath) {
                $settingsContent = Get-Content $settingsPath -Raw | ConvertFrom-Json
            } else {
                $settingsContent = @{}
            }
            
            # Update update settings
            $settingsContent | Add-Member -NotePropertyName "update.mode" -NotePropertyValue "none" -Force
            $settingsContent | Add-Member -NotePropertyName "update.channel" -NotePropertyValue "none" -Force
            
            # Save settings
            $settingsContent | ConvertTo-Json -Depth 10 | Set-Content $settingsPath -Force
            Write-Host "${GREEN}[INFO]${NC} Auto-update disabled successfully"
        }
        catch {
            Write-Host "${RED}[ERROR]${NC} Failed to update settings: $($_.Exception.Message)"
        }
    }
    
    Write-Host ""
    Write-Host "${GREEN}[SUCCESS]${NC} Configuration updated successfully!"
    Write-Host "${YELLOW}[IMPORTANT]${NC} Please restart Cursor to apply changes"
    Write-Host ""
    Write-Host "New IDs:"
    Write-Host "Machine ID: $MACHINE_ID"
    Write-Host "SQM ID: $SQM_ID"
    Write-Host "UUID: $UUID"
    Write-Host "Mac Machine ID: $MAC_MACHINE_ID"
    
}
catch {
    Write-Host "${RED}[ERROR]${NC} Failed to update configuration: $($_.Exception.Message)"
    exit 1
}

# Update MachineGuid in registry
$guidUpdateResult = Update-MachineGuid
if (-not $guidUpdateResult) {
    Write-Host "${YELLOW}[WARNING]${NC} Unable to detect version, continuing anyway..."
}

# Update Cursor machine ID
function Update-CursorMachineId {
    try {
        # Check if file exists
        if (Test-Path $MACHINE_ID_FILE) {
            Write-Host "${GREEN}[INFO]${NC} Current Cursor machine ID file found"
            
            # Read current value for logging
            $originalId = Get-Content $MACHINE_ID_FILE -ErrorAction SilentlyContinue
            if ($originalId) {
                Write-Host "${GREEN}[INFO]${NC} Current machine ID value:"
                Write-Host "    $originalId"
            }

            # Create backup with timestamp
            $backupFile = "$BACKUP_DIR\machineid.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
            Copy-Item $MACHINE_ID_FILE $backupFile
            Write-Host "${GREEN}[INFO]${NC} Machine ID file backed up to: $backupFile"
        } else {
            Write-Host "${YELLOW}[WARNING]${NC} Cursor machine ID file not found, will create new"
            
            # Ensure the Cursor directory exists
            $cursorDir = "${env:APPDATA}\Cursor"
            if (-not (Test-Path $cursorDir)) {
                New-Item -ItemType Directory -Path $cursorDir -Force | Out-Null
            }
        }

        # Generate new UUID in the correct format
        $newId = [System.Guid]::NewGuid().ToString().ToLower()

        # Save new machine ID
        $newId | Set-Content -Path $MACHINE_ID_FILE -Force
        
        # Verify the update
        $verifyId = Get-Content $MACHINE_ID_FILE -ErrorAction Stop
        if ($verifyId -eq $newId) {
            Write-Host "${GREEN}[INFO]${NC} Machine ID updated successfully:"
            Write-Host "    $newId"
            return $true
        } else {
            Write-Host "${RED}[ERROR]${NC} Machine ID verification failed"
            return $false
        }
    }
    catch {
        Write-Host "${RED}[ERROR]${NC} Failed to update Cursor machine ID: $($_.Exception.Message)"
        return $false
    }
}

Write-Host ""
Write-Host "${GREEN}[INFO]${NC} Updating Cursor machine ID..."
$machineIdResult = Update-CursorMachineId
if (-not $machineIdResult) {
    Write-Host "${YELLOW}[WARNING]${NC} Unable to update Cursor machine ID, continuing anyway..."
}

Write-Host ""
Write-Host "${GREEN}[SUCCESS]${NC} All operations completed!"
Write-Host "${YELLOW}[IMPORTANT]${NC} Please restart Cursor to apply all changes"
Write-Host ""
Read-Host "Press Enter to exit" 