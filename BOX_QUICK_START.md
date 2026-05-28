# IBM Box Integration - Quick Start Guide

## 🚀 Get Started in 5 Minutes

This guide will help you quickly set up and run the certification workflow with IBM Box integration.

---

## Step 1: Install Dependencies (2 minutes)

```powershell
# Navigate to the project directory
cd C:\Users\KAPILPEMMARAJU\Downloads\CertificationsWestpac

# Install required packages
pip install -r requirements_box.txt
```

---

## Step 2: Set Up Box Application (One-time setup)

### Option A: Use Existing Box Config File

If you already have a `box_config.json` file:

```powershell
# Set environment variable
$env:BOX_CONFIG_FILE = "C:\Users\KAPILPEMMARAJU\Downloads\CertificationsWestpac\box_config.json"
```

### Option B: Create New Box Application

Follow the detailed instructions in [BOX_SETUP_GUIDE.md](BOX_SETUP_GUIDE.md) to:
1. Create a Box application
2. Generate JWT credentials
3. Download box_config.json

---

## Step 3: Configure Box Folders (2 minutes)

### 3.1 Create Folders in Box

1. Log in to [IBM Box](https://ibm.account.box.com)
2. Create folders:
   - `Certification Workflow/Input`
   - `Certification Workflow/Output`

### 3.2 Get Folder IDs

1. Open each folder in Box
2. Copy the folder ID from the URL:
   ```
   https://ibm.account.box.com/folder/123456789
                                          ↑
                                    This is the ID
   ```

### 3.3 Set Environment Variables

```powershell
# Set folder IDs
$env:BOX_INPUT_FOLDER_ID = "385042546847
$env:BOX_OUTPUT_FOLDER_ID = "385044451149
```

---

## Step 4: Enable Box Integration (30 seconds)

Edit `config.yaml` and set:

```yaml
box:
  enabled: true  # Change from false to true
```

---

## Step 5: Upload Input Files to Box (1 minute)

Upload these files to your Box Input folder:
- `Active Offshore Cloud List-05212026.xlsx`
- `T2G Certification_Financial Services as on 11 May 2026.xlsx`

---

## Step 6: Run the Workflow (30 seconds)

```powershell
# Run with Box integration
python certification_workflow_box.py
```

The workflow will:
1. ✅ Download files from Box Input folder
2. ✅ Process certification data
3. ✅ Upload results to Box Output folder
4. ✅ Clean up temporary files

---

## Step 7: Check Results

1. Go to your Box Output folder
2. Find the generated files:
   - `Westpac_Certification_Consolidated_YYYYMMDD_HHMMSS.xlsx`
   - `Westpac_Certification_Notifications_YYYYMMDD_HHMMSS.txt`

---

## 🎯 Quick Test

Test your Box connection before running the full workflow:

```python
from box_integration import BoxIntegration

# Initialize Box client
box = BoxIntegration(config_file="box_config.json")

# Test: List input folder contents
folder_id = "YOUR_INPUT_FOLDER_ID"
contents = box.list_folder_contents(folder_id)

print("Files in Box folder:")
for item in contents:
    print(f"  - {item['name']} ({item['type']})")
```

---

## 🔄 Switch Between Box and Local Mode

### Use Box (Cloud Storage)
```yaml
# config.yaml
box:
  enabled: true
```

### Use Local Files
```yaml
# config.yaml
box:
  enabled: false
```

---

## 📋 Environment Variables Checklist

Make sure these are set:

```powershell
# Check if variables are set
echo $env:BOX_CONFIG_FILE
echo $env:BOX_INPUT_FOLDER_ID
echo $env:BOX_OUTPUT_FOLDER_ID
```

If any are empty, set them:

```powershell
$env:BOX_CONFIG_FILE = "path\to\box_config.json"
$env:BOX_INPUT_FOLDER_ID = "123456789"
$env:BOX_OUTPUT_FOLDER_ID = "987654321"
```

---

## 🔧 Troubleshooting

### "boxsdk not installed"
```powershell
pip install boxsdk[jwt]
```

### "Box API error: 401 Unauthorized"
- Check if Box application is authorized by admin
- Verify box_config.json is correct
- Ensure BOX_CONFIG_FILE environment variable is set

### "Folder ID not found"
- Verify folder IDs are correct
- Check folder permissions in Box
- Ensure service account has access

### "Could not identify input files"
- Check file names match patterns in config.yaml
- Verify files are in the Box Input folder
- Check file extensions (.xlsx, .xls)

---

## 💡 Pro Tips

### 1. Persistent Environment Variables

Add to your PowerShell profile for permanent setup:

```powershell
# Edit profile
notepad $PROFILE

# Add these lines:
$env:BOX_CONFIG_FILE = "C:\path\to\box_config.json"
$env:BOX_INPUT_FOLDER_ID = "123456789"
$env:BOX_OUTPUT_FOLDER_ID = "987654321"
```

### 2. Batch Processing

Process multiple files at once by uploading them all to the Input folder.

### 3. Automated Scheduling

Use Windows Task Scheduler to run automatically:

```powershell
# Create scheduled task (runs every Monday at 9 AM)
$action = New-ScheduledTaskAction -Execute "python" `
    -Argument "C:\Users\KAPILPEMMARAJU\Downloads\CertificationsWestpac\certification_workflow_box.py" `
    -WorkingDirectory "C:\Users\KAPILPEMMARAJU\Downloads\CertificationsWestpac"

$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 9am

Register-ScheduledTask -TaskName "CertificationWorkflowBox" `
    -Action $action -Trigger $trigger -Description "Automated certification workflow with Box"
```

### 4. Monitor Logs

Check the log file for details:

```powershell
Get-Content certification_workflow.log -Tail 50
```

---

## 📚 Next Steps

- **Full Documentation**: See [BOX_SETUP_GUIDE.md](BOX_SETUP_GUIDE.md)
- **Configuration Options**: Review [config.yaml](config.yaml)
- **GUI Mode**: Use `certification_gui.py` for interactive mode
- **Email Integration**: See [EMAIL_SETUP_GUIDE.md](EMAIL_SETUP_GUIDE.md)

---

## 🆘 Need Help?

1. Check [BOX_SETUP_GUIDE.md](BOX_SETUP_GUIDE.md) for detailed troubleshooting
2. Review workflow logs: `certification_workflow.log`
3. Test Box connection with the quick test script above
4. Verify all environment variables are set correctly

---

## 📊 Workflow Summary

```
┌─────────────────────────────────────────────────────────────┐
│                    Box Integration Workflow                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Download files from Box Input folder                    │
│     ↓                                                        │
│  2. Process certification data                              │
│     ↓                                                        │
│  3. Generate consolidated reports                           │
│     ↓                                                        │
│  4. Upload results to Box Output folder                     │
│     ↓                                                        │
│  5. Clean up temporary files                                │
│     ↓                                                        │
│  6. ✅ Done! Check Box Output folder for results            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

**Made with Bob** 🤖

*Last updated: 2026-05-28*