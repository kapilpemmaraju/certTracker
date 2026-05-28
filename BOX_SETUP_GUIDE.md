# IBM Box Integration Setup Guide

## Overview

This guide explains how to configure and use IBM Box integration with the Certification Workflow. With Box integration enabled, the workflow can:

- **Download input files** from Box folders automatically
- **Upload output files** to Box folders
- **Manage files** centrally in the cloud
- **Enable collaboration** across teams

---

## Prerequisites

### 1. Install Required Package

```powershell
pip install boxsdk[jwt]
```

### 2. IBM Box Account Requirements

- Access to IBM Box (box.ibm.com)
- Permissions to create Box applications
- Admin access or developer token for your Box account

---

## Box Application Setup

### Step 1: Create a Box Application

1. Go to [IBM Box Developer Console](https://ibm.account.box.com/developers/console)
2. Click **"Create New App"**
3. Select **"Custom App"**
4. Choose **"Server Authentication (with JWT)"**
5. Name your app (e.g., "Certification Workflow")
6. Click **"Create App"**

### Step 2: Configure Application Settings

1. In your app settings, go to **"Configuration"** tab
2. Under **"Application Scopes"**, enable:
   - ✅ Read all files and folders stored in Box
   - ✅ Write all files and folders stored in Box
   - ✅ Manage users
   - ✅ Manage enterprise properties

3. Under **"Advanced Features"**, enable:
   - ✅ Generate user access tokens

4. Click **"Save Changes"**

### Step 3: Generate Key Pair

1. Scroll to **"Add and Manage Public Keys"**
2. Click **"Generate a Public/Private Keypair"**
3. A JSON configuration file will be downloaded automatically
4. **IMPORTANT**: Save this file securely - it contains your private key
5. Rename the file to `box_config.json`

### Step 4: Authorize Application

1. Go to **"Authorization"** tab
2. Click **"Review and Submit"** to submit for admin approval
3. Contact your Box admin to approve the application
4. OR if you're an admin, go to Admin Console → Apps → Custom Apps → Authorize

---

## Configuration

### Option 1: Using Configuration File (Recommended)

1. **Save the Box config file**:
   ```
   C:/Users/KAPILPEMMARAJU/Downloads/CertificationsWestpac/box_config.json
   ```

2. **Set environment variable**:
   ```powershell
   $env:BOX_CONFIG_FILE = "C:/Users/KAPILPEMMARAJU/Downloads/CertificationsWestpac/box_config.json"
   ```

3. **Update config.yaml**:
   ```yaml
   box:
     enabled: true
     jwt:
       config_file: "${BOX_CONFIG_FILE}"
   ```

### Option 2: Using Individual Credentials

1. **Extract credentials from box_config.json**:
   - `clientID` → BOX_CLIENT_ID
   - `clientSecret` → BOX_CLIENT_SECRET
   - `enterpriseID` → BOX_ENTERPRISE_ID
   - `publicKeyID` → BOX_JWT_KEY_ID
   - `privateKey` → Save to file (e.g., box_private_key.pem)
   - `passphrase` → BOX_RSA_PASSPHRASE

2. **Set environment variables**:
   ```powershell
   $env:BOX_CLIENT_ID = "your_client_id"
   $env:BOX_CLIENT_SECRET = "your_client_secret"
   $env:BOX_ENTERPRISE_ID = "your_enterprise_id"
   $env:BOX_JWT_KEY_ID = "your_jwt_key_id"
   $env:BOX_RSA_KEY_FILE = "path/to/box_private_key.pem"
   $env:BOX_RSA_PASSPHRASE = "your_passphrase"
   ```

---

## Box Folder Setup

### Step 1: Create Folders in Box

1. Log in to [IBM Box](https://ibm.account.box.com)
2. Create the following folder structure:

```
Certification Workflow/
├── Input/          (for input files)
├── Output/         (for output files)
└── Backup/         (optional - for backups)
```

### Step 2: Get Folder IDs

1. Navigate to each folder in Box
2. The folder ID is in the URL:
   ```
   https://ibm.account.box.com/folder/123456789
                                          ↑
                                    Folder ID
   ```
3. Note down the folder IDs

### Step 3: Configure Folder IDs

Set environment variables:

```powershell
$env:BOX_INPUT_FOLDER_ID = "123456789"
$env:BOX_OUTPUT_FOLDER_ID = "987654321"
$env:BOX_BACKUP_FOLDER_ID = "456789123"
```

Or update `config.yaml`:

```yaml
box:
  folders:
    input_folder_id: "123456789"
    output_folder_id: "987654321"
    backup_folder_id: "456789123"
```

---

## Usage

### Running with Box Integration

1. **Enable Box in config.yaml**:
   ```yaml
   box:
     enabled: true
   ```

2. **Upload input files to Box**:
   - Upload `Active Offshore Cloud List.xlsx` to Input folder
   - Upload `T2G Certification_Financial Services.xlsx` to Input folder

3. **Run the workflow**:
   ```powershell
   python certification_workflow_box.py
   ```

4. **Check output in Box**:
   - Output files will be uploaded to the Output folder
   - Check the Output folder in Box for results

### Running without Box (Local Mode)

1. **Disable Box in config.yaml**:
   ```yaml
   box:
     enabled: false
   ```

2. **Run the workflow**:
   ```powershell
   python certification_workflow_box.py
   ```

3. **Files will be read/written locally** as before

---

## Testing Box Connection

Test your Box connection before running the full workflow:

```python
from box_integration import BoxIntegration

# Test connection
box = BoxIntegration(config_file="box_config.json")

# List folder contents
folder_id = "123456789"
contents = box.list_folder_contents(folder_id)
for item in contents:
    print(f"{item['type']}: {item['name']}")

# Get folder info
info = box.get_folder_info(folder_id)
print(f"Folder: {info['name']}")
print(f"Items: {info['item_count']}")
```

---

## File Naming Conventions

The workflow identifies files by name patterns:

### Input Files

Configure patterns in `config.yaml`:

```yaml
files:
  file_a:
    box_file_name: "Active Offshore Cloud List"
  file_b:
    box_file_name: "T2G Certification_Financial Services"
```

Files matching these patterns will be automatically identified.

### Output Files

Output files are automatically named with timestamps:
- `Westpac_Certification_Consolidated_YYYYMMDD_HHMMSS.xlsx`
- `Westpac_Certification_Notifications_YYYYMMDD_HHMMSS.txt`

---

## Troubleshooting

### Error: "boxsdk not installed"

**Solution**: Install the package
```powershell
pip install boxsdk[jwt]
```

### Error: "Box API error: 401 Unauthorized"

**Possible causes**:
1. Application not authorized by admin
2. Invalid credentials
3. Expired JWT token

**Solution**:
- Verify application is authorized in Box Admin Console
- Check credentials in box_config.json
- Regenerate keypair if needed

### Error: "Folder ID not found"

**Solution**:
- Verify folder IDs are correct
- Check folder permissions
- Ensure service account has access to folders

### Error: "Could not identify input files"

**Solution**:
- Check file naming patterns in config.yaml
- Verify files exist in Box input folder
- Check file_patterns configuration

### Files not uploading to Box

**Solution**:
- Check output folder ID is correct
- Verify write permissions
- Check Box storage quota

---

## Security Best Practices

### 1. Protect Configuration Files

```powershell
# Set restrictive permissions on box_config.json
icacls box_config.json /inheritance:r /grant:r "$env:USERNAME:(R)"
```

### 2. Use Environment Variables

Never hardcode credentials in config.yaml:
```yaml
# ✅ Good
jwt:
  config_file: "${BOX_CONFIG_FILE}"

# ❌ Bad
jwt:
  config_file: "C:/path/to/box_config.json"
```

### 3. Rotate Keys Regularly

- Regenerate keypairs every 90 days
- Update box_config.json
- Test connection after rotation

### 4. Limit Application Scope

Only enable required permissions in Box application settings.

### 5. Monitor Access Logs

Regularly review Box access logs for unusual activity.

---

## Advanced Configuration

### Custom Retry Logic

```yaml
box:
  retry:
    max_attempts: 5
    delay_seconds: 10
    exponential_backoff: true
```

### File Cleanup

```yaml
box:
  cleanup_temp_files: true  # Delete local copies after upload
```

### File Patterns

```yaml
box:
  input_file_patterns:
    - "*.xlsx"
    - "*.xls"
    - "*.csv"
```

---

## Integration with Existing Workflows

### GUI Integration

The Box integration works seamlessly with the GUI:

```python
from certification_gui import CertificationGUI
from config_loader import ConfigLoader

config = ConfigLoader("config.yaml")
gui = CertificationGUI(config, use_box=True)
gui.run()
```

### Scheduled Automation

Use Windows Task Scheduler with Box integration:

```powershell
# Create scheduled task
$action = New-ScheduledTaskAction -Execute "python" -Argument "certification_workflow_box.py"
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 9am
Register-ScheduledTask -TaskName "CertificationWorkflow" -Action $action -Trigger $trigger
```

---

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review Box SDK documentation: https://github.com/box/box-python-sdk
3. Contact your Box administrator
4. Review workflow logs: `certification_workflow.log`

---

## Appendix: Complete Configuration Example

```yaml
# config.yaml with Box integration

box:
  enabled: true
  auth_method: "jwt"
  
  jwt:
    config_file: "${BOX_CONFIG_FILE}"
  
  folders:
    input_folder_id: "${BOX_INPUT_FOLDER_ID}"
    output_folder_id: "${BOX_OUTPUT_FOLDER_ID}"
    backup_folder_id: "${BOX_BACKUP_FOLDER_ID}"
  
  input_file_patterns:
    - "*.xlsx"
    - "*.xls"
  
  cleanup_temp_files: true
  
  retry:
    max_attempts: 3
    delay_seconds: 5
    exponential_backoff: true

files:
  file_a:
    box_file_name: "Active Offshore Cloud List"
    email_column: "EMP_INTRANETID"
  
  file_b:
    box_file_name: "T2G Certification_Financial Services"
    worksheet: "T2G Certification data-11 May"
    email_column: "Internet Email"
    client_column: "Global_Client_Name"
  
  output:
    directory: "./output"
    create_if_missing: true

processing:
  target_client: "WESTPAC BANKING CORPORATION"
```

---

**Made with Bob** 🤖