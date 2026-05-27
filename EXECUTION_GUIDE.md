# Execution Guide - Step-by-Step Deployment & Execution

## 🚀 Quick Start - Execute Right Now!

### Option 1: Execute Version 1.0 (Simplest - Recommended for First Time)

```bash
# Open PowerShell or Command Prompt
# Navigate to the directory
cd C:\Users\KAPILPEMMARAJU\Downloads\CertificationsWestpac

# Run the workflow
python certification_workflow.py
```

**That's it!** The workflow will:
1. Load both Excel files
2. Filter for Westpac Banking Corporation
3. Match email addresses
4. Generate consolidated spreadsheet
5. Create notification messages
6. Save everything to the same directory

**Output files will be created:**
- `Westpac_Certification_Consolidated_[timestamp].xlsx`
- `Westpac_Certification_Notifications_[timestamp].txt`
- `certification_workflow.log`

### Option 2: Execute Version 2.0 (Configuration-Driven)

```bash
# Navigate to the directory
cd C:\Users\KAPILPEMMARAJU\Downloads\CertificationsWestpac

# Run the configuration-driven workflow
python certification_workflow_v2.py
```

**Output files will be in the `output` subdirectory:**
- `output/WESTPAC_BANKING_CORPORATION_Certification_Consolidated_[timestamp].xlsx`
- `output/WESTPAC_BANKING_CORPORATION_Certification_Notifications_[timestamp].txt`
- `output/workflow_metrics.json`

## 📋 Detailed Deployment Steps

### Step 1: Verify Prerequisites

```bash
# Check Python is installed
python --version
# Should show: Python 3.11 or higher

# Check required packages
python -c "import pandas; import openpyxl; print('✅ All packages installed')"
```

**If packages are missing:**
```bash
pip install pandas openpyxl pyyaml
```

### Step 2: Verify Files Are Present

```bash
# Navigate to directory
cd C:\Users\KAPILPEMMARAJU\Downloads\CertificationsWestpac

# List files
dir

# You should see:
# - certification_workflow.py
# - certification_workflow_v2.py
# - config.yaml
# - config_loader.py
# - Active Offshore Cloud List-05212026.xlsx
# - T2G Certification_Financial Services as on 11 May 2026.xlsx
```

### Step 3: Choose Your Version

#### For Version 1.0 (Simple):
```bash
python certification_workflow.py
```

#### For Version 2.0 (Configurable):
```bash
python certification_workflow_v2.py
```

### Step 4: Monitor Execution

You'll see output like:
```
2026-05-21 22:15:22,682 - INFO - Workflow initialized
2026-05-21 22:15:22,682 - INFO - STARTING CERTIFICATION WORKFLOW
2026-05-21 22:15:22,682 - INFO - STEP 1: Loading File A
2026-05-21 22:15:22,686 - INFO - File A loaded: 225 rows
...
2026-05-21 22:15:38,333 - INFO - WORKFLOW COMPLETED SUCCESSFULLY
```

### Step 5: Check Output Files

```bash
# For Version 1.0 - files in current directory
dir Westpac_Certification_*.xlsx
dir Westpac_Certification_*.txt

# For Version 2.0 - files in output directory
dir output\*.xlsx
dir output\*.txt
dir output\*.json
```

### Step 6: Review Results

**Open the Excel file:**
```bash
# Open with Excel
start output\WESTPAC_BANKING_CORPORATION_Certification_Consolidated_*.xlsx
```

**View notifications:**
```bash
# Open with Notepad
notepad output\WESTPAC_BANKING_CORPORATION_Certification_Notifications_*.txt
```

**Check logs:**
```bash
# View log file
notepad certification_workflow.log
```

## 🔧 Configuration Changes (Version 2.0 Only)

### Change Target Client

1. Open `config.yaml` in a text editor
2. Find the line:
   ```yaml
   target_client: "WESTPAC BANKING CORPORATION"
   ```
3. Change to your desired client:
   ```yaml
   target_client: "COMMONWEALTH BANK"
   ```
4. Save and run again:
   ```bash
   python certification_workflow_v2.py
   ```

### Change Output Directory

1. Open `config.yaml`
2. Find:
   ```yaml
   files:
     output:
       directory: "./output"
   ```
3. Change to your desired path:
   ```yaml
   files:
     output:
       directory: "C:/MyOutputFolder"
   ```
4. Save and run

### Change Input Files

1. Open `config.yaml`
2. Update file paths:
   ```yaml
   files:
     file_a:
       path: "path/to/your/employee_list.xlsx"
     file_b:
       path: "path/to/your/certification_data.xlsx"
   ```
3. Save and run

## 📅 Schedule Automatic Execution

### Windows Task Scheduler

1. **Open Task Scheduler**
   - Press `Win + R`
   - Type `taskschd.msc`
   - Press Enter

2. **Create New Task**
   - Click "Create Basic Task"
   - Name: "Certification Workflow"
   - Description: "Daily certification processing"

3. **Set Trigger**
   - Choose "Daily"
   - Set time (e.g., 9:00 AM)
   - Click Next

4. **Set Action**
   - Choose "Start a program"
   - Program: `python`
   - Arguments: `certification_workflow_v2.py`
   - Start in: `C:\Users\KAPILPEMMARAJU\Downloads\CertificationsWestpac`

5. **Finish**
   - Review settings
   - Click Finish

### PowerShell Script for Scheduling

Create `run_workflow.ps1`:
```powershell
# Navigate to directory
Set-Location "C:\Users\KAPILPEMMARAJU\Downloads\CertificationsWestpac"

# Run workflow
python certification_workflow_v2.py

# Check if successful
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Workflow completed successfully"
} else {
    Write-Host "❌ Workflow failed"
}
```

Run it:
```powershell
powershell -ExecutionPolicy Bypass -File run_workflow.ps1
```

## 🔄 Running with Different Data

### Update Input Files

1. **Copy new files to the directory:**
   ```bash
   copy "C:\path\to\new\employee_list.xlsx" "C:\Users\KAPILPEMMARAJU\Downloads\CertificationsWestpac\Active Offshore Cloud List-05212026.xlsx"
   ```

2. **Or update config.yaml (V2.0):**
   ```yaml
   files:
     file_a:
       path: "C:/path/to/new/employee_list.xlsx"
   ```

3. **Run the workflow:**
   ```bash
   python certification_workflow_v2.py
   ```

## 📧 Enable Email Sending

### Step 1: Set Environment Variables

**PowerShell:**
```powershell
$env:SMTP_SERVER = "smtp.gmail.com"
$env:SMTP_PORT = "587"
$env:SENDER_EMAIL = "your-email@gmail.com"
$env:SENDER_PASSWORD = "your-app-password"
$env:TEST_EMAIL = "test@example.com"
```

**Command Prompt:**
```cmd
set SMTP_SERVER=smtp.gmail.com
set SMTP_PORT=587
set SENDER_EMAIL=your-email@gmail.com
set SENDER_PASSWORD=your-app-password
set TEST_EMAIL=test@example.com
```

### Step 2: Enable Email in Config

Edit `config.yaml`:
```yaml
email:
  enabled: true
  test_mode: true  # Set to false for production
```

### Step 3: Run Workflow

```bash
python certification_workflow_v2.py
```

## 🐛 Troubleshooting

### Issue: "Python is not recognized"

**Solution:**
```bash
# Use full path to Python
C:\Users\KAPILPEMMARAJU\AppData\Local\Microsoft\WindowsApps\python.exe certification_workflow.py
```

### Issue: "No module named 'pandas'"

**Solution:**
```bash
pip install pandas openpyxl pyyaml
```

### Issue: "File not found"

**Solution:**
```bash
# Check you're in the right directory
cd C:\Users\KAPILPEMMARAJU\Downloads\CertificationsWestpac

# List files to verify
dir *.xlsx
```

### Issue: "Permission denied"

**Solution:**
```bash
# Close Excel if files are open
# Run PowerShell as Administrator
# Or change output directory in config.yaml
```

### Issue: No output files created

**Solution:**
```bash
# Check the log file
notepad certification_workflow.log

# Look for error messages
# Verify input files exist
dir *.xlsx
```

## 📊 Verify Execution Success

### Check Console Output

Look for:
```
====================================================================================================
WORKFLOW COMPLETED SUCCESSFULLY
====================================================================================================
Status: SUCCESS
File A records: 225
Matched records: 614
Notifications generated: 126
```

### Check Output Files

**Version 1.0:**
```bash
dir Westpac_Certification_Consolidated_*.xlsx
dir Westpac_Certification_Notifications_*.txt
```

**Version 2.0:**
```bash
dir output\*.xlsx
dir output\*.txt
dir output\workflow_metrics.json
```

### Check Log File

```bash
notepad certification_workflow.log
```

Look for "WORKFLOW COMPLETED SUCCESSFULLY"

### Verify Data Quality

1. **Open Excel file**
   - Should have 614 rows (for Westpac)
   - Columns: Email, Name, Vendor, Title, Dates, etc.

2. **Open notifications file**
   - Should have 126 notification messages
   - Each with certification details

3. **Check metrics (V2.0)**
   ```bash
   notepad output\workflow_metrics.json
   ```
   - Should show match rate, record counts, etc.

## 🎯 Quick Reference Commands

### Execute Workflow
```bash
# Version 1.0 (Simple)
python certification_workflow.py

# Version 2.0 (Configurable)
python certification_workflow_v2.py
```

### View Output
```bash
# Open Excel output
start output\*.xlsx

# View notifications
notepad output\*.txt

# Check logs
notepad certification_workflow.log
```

### Check Status
```bash
# View last 20 lines of log
Get-Content certification_workflow.log -Tail 20

# Check if output files exist
Test-Path output\*.xlsx
```

### Clean Up Old Files
```bash
# Delete old output files (be careful!)
Remove-Item output\*_20260520_*.xlsx
Remove-Item output\*_20260520_*.txt
```

## 📞 Need Help?

1. **Check log file first:**
   ```bash
   notepad certification_workflow.log
   ```

2. **Verify prerequisites:**
   ```bash
   python --version
   pip list | findstr pandas
   ```

3. **Test with sample data:**
   - Use a small subset of data first
   - Verify output is correct
   - Then run with full dataset

4. **Review documentation:**
   - `README.md` - Technical details
   - `QUICK_START.md` - Quick start guide
   - `DEPLOYMENT_NOTES.md` - Deployment info

## ✅ Success Checklist

- [ ] Python 3.11+ installed
- [ ] Required packages installed (pandas, openpyxl, pyyaml)
- [ ] Input Excel files present
- [ ] Navigated to correct directory
- [ ] Executed workflow command
- [ ] Saw "WORKFLOW COMPLETED SUCCESSFULLY"
- [ ] Output files created
- [ ] Verified data in Excel file
- [ ] Checked notification messages
- [ ] Reviewed log file

**You're ready to go! Just run the command and check the output files.** 🚀