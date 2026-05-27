# ============================================================================
# Automated Certification Workflow - PowerShell Script
# ============================================================================
# This script automates the entire certification workflow including:
# - Pre-execution checks
# - Workflow execution
# - Post-execution validation
# - Email notifications
# - Backup management
# - Error handling
# - Logging
#
# Author: IBM BOB
# Date: 2026-05-21
# ============================================================================

param(
    [string]$ConfigFile = "config.yaml",
    [string]$Version = "v2",  # v1 or v2
    [switch]$SendEmails = $false,
    [switch]$CreateBackup = $true,
    [switch]$Verbose = $false
)

# Configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$LogFile = Join-Path $ScriptDir "automation.log"
$ErrorLogFile = Join-Path $ScriptDir "automation_errors.log"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

# ============================================================================
# Logging Functions
# ============================================================================

function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    
    $LogMessage = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - [$Level] - $Message"
    Add-Content -Path $LogFile -Value $LogMessage
    
    switch ($Level) {
        "ERROR" { Write-Host $LogMessage -ForegroundColor Red }
        "WARNING" { Write-Host $LogMessage -ForegroundColor Yellow }
        "SUCCESS" { Write-Host $LogMessage -ForegroundColor Green }
        default { Write-Host $LogMessage }
    }
}

function Write-ErrorLog {
    param([string]$Message)
    Add-Content -Path $ErrorLogFile -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - $Message"
}

# ============================================================================
# Pre-Execution Checks
# ============================================================================

function Test-Prerequisites {
    Write-Log "Checking prerequisites..." "INFO"
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        Write-Log "Python version: $pythonVersion" "SUCCESS"
    }
    catch {
        Write-Log "Python not found. Please install Python 3.11+" "ERROR"
        return $false
    }
    
    # Check required packages
    $requiredPackages = @("pandas", "openpyxl", "pyyaml")
    foreach ($package in $requiredPackages) {
        $installed = pip show $package 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Package $package is installed" "SUCCESS"
        }
        else {
            Write-Log "Package $package is missing. Installing..." "WARNING"
            pip install $package
        }
    }
    
    # Check input files exist
    $fileA = "Active Offshore Cloud List-05212026.xlsx"
    $fileB = "T2G Certification_Financial Services as on 11 May 2026.xlsx"
    
    if (Test-Path $fileA) {
        Write-Log "File A found: $fileA" "SUCCESS"
    }
    else {
        Write-Log "File A not found: $fileA" "ERROR"
        return $false
    }
    
    if (Test-Path $fileB) {
        Write-Log "File B found: $fileB" "SUCCESS"
    }
    else {
        Write-Log "File B not found: $fileB" "ERROR"
        return $false
    }
    
    # Check disk space
    $drive = (Get-Location).Drive
    $freeSpace = (Get-PSDrive $drive.Name).Free / 1GB
    if ($freeSpace -lt 1) {
        Write-Log "Low disk space: $([math]::Round($freeSpace, 2)) GB" "WARNING"
    }
    else {
        Write-Log "Disk space available: $([math]::Round($freeSpace, 2)) GB" "SUCCESS"
    }
    
    return $true
}

# ============================================================================
# Backup Management
# ============================================================================

function New-Backup {
    Write-Log "Creating backup of input files..." "INFO"
    
    $backupDir = Join-Path $ScriptDir "backup\$Timestamp"
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    
    # Backup input files
    $files = Get-ChildItem -Path $ScriptDir -Filter "*.xlsx"
    foreach ($file in $files) {
        Copy-Item -Path $file.FullName -Destination $backupDir
        Write-Log "Backed up: $($file.Name)" "SUCCESS"
    }
    
    # Backup configuration
    if (Test-Path $ConfigFile) {
        Copy-Item -Path $ConfigFile -Destination $backupDir
        Write-Log "Backed up: $ConfigFile" "SUCCESS"
    }
    
    Write-Log "Backup created in: $backupDir" "SUCCESS"
    return $backupDir
}

function Remove-OldBackups {
    param([int]$RetentionDays = 30)
    
    Write-Log "Cleaning up old backups (retention: $RetentionDays days)..." "INFO"
    
    $backupDir = Join-Path $ScriptDir "backup"
    if (Test-Path $backupDir) {
        $cutoffDate = (Get-Date).AddDays(-$RetentionDays)
        $oldBackups = Get-ChildItem -Path $backupDir -Directory | Where-Object { $_.CreationTime -lt $cutoffDate }
        
        foreach ($backup in $oldBackups) {
            Remove-Item -Path $backup.FullName -Recurse -Force
            Write-Log "Removed old backup: $($backup.Name)" "INFO"
        }
    }
}

# ============================================================================
# Workflow Execution
# ============================================================================

function Invoke-Workflow {
    param([string]$Version)
    
    Write-Log "Starting workflow execution (Version: $Version)..." "INFO"
    
    $scriptName = if ($Version -eq "v2") { "certification_workflow_v2.py" } else { "certification_workflow.py" }
    
    try {
        # Execute workflow
        $output = python $scriptName 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Workflow executed successfully" "SUCCESS"
            Write-Log "Output: $output" "INFO"
            return $true
        }
        else {
            Write-Log "Workflow execution failed with exit code: $LASTEXITCODE" "ERROR"
            Write-ErrorLog "Workflow failed: $output"
            return $false
        }
    }
    catch {
        Write-Log "Error executing workflow: $_" "ERROR"
        Write-ErrorLog "Exception: $_"
        return $false
    }
}

# ============================================================================
# Post-Execution Validation
# ============================================================================

function Test-OutputFiles {
    Write-Log "Validating output files..." "INFO"
    
    $outputDir = if ($Version -eq "v2") { "output" } else { "." }
    
    # Check for Excel output
    $excelFiles = Get-ChildItem -Path $outputDir -Filter "*Certification_Consolidated*.xlsx" -ErrorAction SilentlyContinue
    if ($excelFiles.Count -gt 0) {
        $latestExcel = $excelFiles | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        Write-Log "Excel output found: $($latestExcel.Name)" "SUCCESS"
        Write-Log "File size: $([math]::Round($latestExcel.Length / 1KB, 2)) KB" "INFO"
    }
    else {
        Write-Log "Excel output not found" "ERROR"
        return $false
    }
    
    # Check for notifications
    $notificationFiles = Get-ChildItem -Path $outputDir -Filter "*Certification_Notifications*.txt" -ErrorAction SilentlyContinue
    if ($notificationFiles.Count -gt 0) {
        $latestNotif = $notificationFiles | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        Write-Log "Notifications file found: $($latestNotif.Name)" "SUCCESS"
        Write-Log "File size: $([math]::Round($latestNotif.Length / 1KB, 2)) KB" "INFO"
    }
    else {
        Write-Log "Notifications file not found" "ERROR"
        return $false
    }
    
    # Check metrics (v2 only)
    if ($Version -eq "v2") {
        $metricsFile = Join-Path $outputDir "workflow_metrics.json"
        if (Test-Path $metricsFile) {
            $metrics = Get-Content $metricsFile | ConvertFrom-Json
            Write-Log "Metrics file found" "SUCCESS"
            Write-Log "Matched records: $($metrics.matched_records)" "INFO"
            Write-Log "Unique emails: $($metrics.unique_emails)" "INFO"
            Write-Log "Notifications generated: $($metrics.notifications_generated)" "INFO"
        }
    }
    
    return $true
}

# ============================================================================
# Email Notification
# ============================================================================

function Send-CompletionEmail {
    param(
        [bool]$Success,
        [string]$BackupPath
    )
    
    if (-not $SendEmails) {
        Write-Log "Email notifications disabled" "INFO"
        return
    }
    
    Write-Log "Sending completion email..." "INFO"
    
    # This would integrate with your email system
    # For now, just log the intent
    $status = if ($Success) { "SUCCESS" } else { "FAILED" }
    Write-Log "Email notification: Workflow $status" "INFO"
}

# ============================================================================
# Reporting
# ============================================================================

function New-ExecutionReport {
    param(
        [bool]$Success,
        [string]$BackupPath,
        [datetime]$StartTime,
        [datetime]$EndTime
    )
    
    $reportFile = Join-Path $ScriptDir "execution_report_$Timestamp.txt"
    
    $report = @"
================================================================================
CERTIFICATION WORKFLOW EXECUTION REPORT
================================================================================
Execution Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Version: $Version
Status: $(if ($Success) { 'SUCCESS' } else { 'FAILED' })
Duration: $([math]::Round(($EndTime - $StartTime).TotalSeconds, 2)) seconds

CONFIGURATION
--------------------------------------------------------------------------------
Config File: $ConfigFile
Send Emails: $SendEmails
Create Backup: $CreateBackup

BACKUP
--------------------------------------------------------------------------------
Backup Location: $BackupPath

OUTPUT FILES
--------------------------------------------------------------------------------
"@
    
    # Add output file details
    $outputDir = if ($Version -eq "v2") { "output" } else { "." }
    $outputFiles = Get-ChildItem -Path $outputDir -Filter "*Certification*" -ErrorAction SilentlyContinue
    foreach ($file in $outputFiles) {
        $report += "`n$($file.Name) - $([math]::Round($file.Length / 1KB, 2)) KB"
    }
    
    $report += @"

LOGS
--------------------------------------------------------------------------------
Automation Log: $LogFile
Error Log: $ErrorLogFile
Workflow Log: certification_workflow.log

NEXT STEPS
--------------------------------------------------------------------------------
1. Review output files in: $outputDir
2. Verify data quality in Excel file
3. Review notification messages
4. Check logs for any warnings
5. Send notifications to employees (if not automated)

================================================================================
"@
    
    $report | Out-File -FilePath $reportFile -Encoding UTF8
    Write-Log "Execution report created: $reportFile" "SUCCESS"
    
    return $reportFile
}

# ============================================================================
# Main Execution
# ============================================================================

function Main {
    Write-Log "========================================" "INFO"
    Write-Log "AUTOMATED CERTIFICATION WORKFLOW" "INFO"
    Write-Log "========================================" "INFO"
    
    $startTime = Get-Date
    $success = $false
    $backupPath = ""
    
    try {
        # Step 1: Pre-execution checks
        Write-Log "STEP 1: Pre-execution checks" "INFO"
        if (-not (Test-Prerequisites)) {
            throw "Prerequisites check failed"
        }
        
        # Step 2: Create backup
        if ($CreateBackup) {
            Write-Log "STEP 2: Creating backup" "INFO"
            $backupPath = New-Backup
        }
        
        # Step 3: Execute workflow
        Write-Log "STEP 3: Executing workflow" "INFO"
        $success = Invoke-Workflow -Version $Version
        
        if (-not $success) {
            throw "Workflow execution failed"
        }
        
        # Step 4: Validate output
        Write-Log "STEP 4: Validating output" "INFO"
        if (-not (Test-OutputFiles)) {
            throw "Output validation failed"
        }
        
        # Step 5: Send notifications
        Write-Log "STEP 5: Sending notifications" "INFO"
        Send-CompletionEmail -Success $success -BackupPath $backupPath
        
        # Step 6: Cleanup
        Write-Log "STEP 6: Cleanup" "INFO"
        Remove-OldBackups -RetentionDays 30
        
        Write-Log "========================================" "SUCCESS"
        Write-Log "WORKFLOW COMPLETED SUCCESSFULLY" "SUCCESS"
        Write-Log "========================================" "SUCCESS"
    }
    catch {
        Write-Log "========================================" "ERROR"
        Write-Log "WORKFLOW FAILED: $_" "ERROR"
        Write-Log "========================================" "ERROR"
        Write-ErrorLog "Fatal error: $_"
    }
    finally {
        $endTime = Get-Date
        
        # Generate report
        $reportFile = New-ExecutionReport -Success $success -BackupPath $backupPath -StartTime $startTime -EndTime $endTime
        
        Write-Log "Execution time: $([math]::Round(($endTime - $startTime).TotalSeconds, 2)) seconds" "INFO"
        Write-Log "Report generated: $reportFile" "INFO"
    }
    
    return $success
}

# ============================================================================
# Execute
# ============================================================================

$result = Main

if ($result) {
    exit 0
}
else {
    exit 1
}

# Made with Bob
