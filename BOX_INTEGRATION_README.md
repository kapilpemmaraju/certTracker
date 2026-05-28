# IBM Box Integration for Certification Workflow

## 📦 Overview

The certification workflow now supports **IBM Box integration**, enabling cloud-based file management for input and output files. This enhancement allows teams to:

- ✅ **Centralize file storage** in IBM Box
- ✅ **Automate file downloads** from Box folders
- ✅ **Upload results automatically** to Box
- ✅ **Enable team collaboration** through shared folders
- ✅ **Maintain audit trails** with Box version history
- ✅ **Scale operations** without local storage constraints

---

## 🎯 Key Features

### 1. Automatic File Download
- Downloads input files from configured Box folders
- Supports file pattern matching (*.xlsx, *.xls)
- Identifies files by name patterns
- Handles multiple files in a single folder

### 2. Automatic File Upload
- Uploads output files to Box folders
- Preserves file naming with timestamps
- Supports multiple output files
- Maintains folder organization

### 3. Flexible Configuration
- Enable/disable Box integration via config
- Fallback to local file operations
- Environment variable support
- Multiple authentication methods

### 4. Error Handling & Retry
- Automatic retry on failures
- Exponential backoff support
- Detailed error logging
- Graceful degradation

### 5. Temporary File Management
- Automatic cleanup of downloaded files
- Configurable retention policies
- Secure temporary storage

---

## 📁 New Files Added

### Core Integration Files

1. **`box_integration.py`** (428 lines)
   - Box SDK wrapper with JWT authentication
   - File download/upload operations
   - Folder management utilities
   - Error handling and retry logic

2. **`certification_workflow_box.py`** (476 lines)
   - Enhanced workflow with Box support
   - Extends original CertificationWorkflow class
   - Automatic file download/upload
   - Seamless local/cloud switching

### Configuration Files

3. **`config.yaml`** (Updated)
   - Added Box configuration section
   - Folder ID configuration
   - Authentication settings
   - File pattern matching

4. **`requirements_box.txt`** (24 lines)
   - Box SDK dependencies
   - JWT authentication libraries
   - All required packages

### Documentation

5. **`BOX_SETUP_GUIDE.md`** (449 lines)
   - Complete setup instructions
   - Box application creation
   - Authentication configuration
   - Troubleshooting guide

6. **`BOX_QUICK_START.md`** (267 lines)
   - 5-minute quick start guide
   - Step-by-step instructions
   - Common use cases
   - Pro tips and tricks

7. **`BOX_INTEGRATION_README.md`** (This file)
   - Overview and architecture
   - Usage examples
   - Migration guide

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Certification Workflow                        │
│                     with Box Integration                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │     Configuration (config.yaml)         │
        │  - Box enabled: true/false              │
        │  - Folder IDs                           │
        │  - Authentication                       │
        └─────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Box Enabled?   │
                    └─────────────────┘
                       │           │
                  Yes  │           │  No
                       ▼           ▼
        ┌──────────────────┐   ┌──────────────────┐
        │  Box Integration │   │  Local Files     │
        │  - Download      │   │  - Read from     │
        │  - Process       │   │    local paths   │
        │  - Upload        │   │  - Write to      │
        │  - Cleanup       │   │    local paths   │
        └──────────────────┘   └──────────────────┘
                       │           │
                       └─────┬─────┘
                             ▼
                ┌─────────────────────────┐
                │  Process Certification  │
                │  Data & Generate        │
                │  Notifications          │
                └─────────────────────────┘
                             ▼
                    ┌────────────────┐
                    │  Output Files  │
                    │  - Excel       │
                    │  - Text        │
                    └────────────────┘
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```powershell
pip install -r requirements_box.txt
```

### 2. Configure Box

```powershell
# Set environment variables
$env:BOX_CONFIG_FILE = "path\to\box_config.json"
$env:BOX_INPUT_FOLDER_ID = "123456789"
$env:BOX_OUTPUT_FOLDER_ID = "987654321"
```

### 3. Enable Box Integration

Edit `config.yaml`:
```yaml
box:
  enabled: true
```

### 4. Run Workflow

```powershell
python certification_workflow_box.py
```

**See [BOX_QUICK_START.md](BOX_QUICK_START.md) for detailed instructions.**

---

## 💻 Usage Examples

### Example 1: Basic Usage with Box

```python
from config_loader import ConfigLoader
from certification_workflow_box import CertificationWorkflowBox

# Load configuration
config = ConfigLoader("config.yaml")

# Create workflow with Box integration
workflow = CertificationWorkflowBox(config, use_box=True)

# Run workflow
results = workflow.run()

print(f"Files downloaded: {results['box_files_downloaded']}")
print(f"Files uploaded: {results['box_files_uploaded']}")
```

### Example 2: Programmatic Box Operations

```python
from box_integration import BoxIntegration

# Initialize Box client
box = BoxIntegration(config_file="box_config.json")

# Download specific file
file_path = box.download_file(
    file_id="123456789",
    output_path="./downloads/file.xlsx"
)

# Upload file
file_id = box.upload_file(
    file_path="./output/report.xlsx",
    folder_id="987654321"
)

# List folder contents
contents = box.list_folder_contents("123456789")
for item in contents:
    print(f"{item['type']}: {item['name']}")
```

### Example 3: Switching Between Box and Local

```python
from config_loader import ConfigLoader
from certification_workflow_box import CertificationWorkflowBox

config = ConfigLoader("config.yaml")

# Use Box
workflow_box = CertificationWorkflowBox(config, use_box=True)
results_box = workflow_box.run()

# Use local files
workflow_local = CertificationWorkflowBox(config, use_box=False)
results_local = workflow_local.run()
```

### Example 4: Batch Processing from Box

```python
from box_integration import BoxIntegration

box = BoxIntegration(config_file="box_config.json")

# Download all Excel files from folder
files = box.download_files_from_folder(
    folder_id="123456789",
    file_patterns=["*.xlsx", "*.xls"]
)

print(f"Downloaded {len(files)} files:")
for file in files:
    print(f"  - {file.name}")
```

---

## 🔧 Configuration Reference

### Box Configuration Section

```yaml
box:
  # Enable/disable Box integration
  enabled: true
  
  # Authentication
  jwt:
    config_file: "${BOX_CONFIG_FILE}"
  
  # Folder IDs
  folders:
    input_folder_id: "${BOX_INPUT_FOLDER_ID}"
    output_folder_id: "${BOX_OUTPUT_FOLDER_ID}"
  
  # File patterns
  input_file_patterns:
    - "*.xlsx"
    - "*.xls"
  
  # Cleanup
  cleanup_temp_files: true
  
  # Retry logic
  retry:
    max_attempts: 3
    delay_seconds: 5
    exponential_backoff: true
```

### File Configuration

```yaml
files:
  file_a:
    # Local path (used when Box disabled)
    path: "Active Offshore Cloud List.xlsx"
    # Box file name pattern
    box_file_name: "Active Offshore Cloud List"
    email_column: "EMP_INTRANETID"
  
  file_b:
    path: "T2G Certification_Financial Services.xlsx"
    box_file_name: "T2G Certification"
    email_column: "Internet Email"
```

---

## 🔐 Security Best Practices

### 1. Protect Credentials

```powershell
# Never commit box_config.json to version control
# Add to .gitignore
echo "box_config.json" >> .gitignore
echo "*.pem" >> .gitignore
```

### 2. Use Environment Variables

```yaml
# ✅ Good - uses environment variables
jwt:
  config_file: "${BOX_CONFIG_FILE}"

# ❌ Bad - hardcoded path
jwt:
  config_file: "C:/secrets/box_config.json"
```

### 3. Restrict File Permissions

```powershell
# Windows: Restrict access to config file
icacls box_config.json /inheritance:r /grant:r "$env:USERNAME:(R)"
```

### 4. Rotate Keys Regularly

- Regenerate JWT keypairs every 90 days
- Update box_config.json
- Test connection after rotation

### 5. Monitor Access

- Review Box access logs regularly
- Set up alerts for unusual activity
- Use Box Shield for advanced security

---

## 📊 Comparison: Box vs Local

| Feature | Box Integration | Local Files |
|---------|----------------|-------------|
| **Storage** | Cloud (unlimited) | Local disk |
| **Collaboration** | ✅ Multiple users | ❌ Single user |
| **Access** | Anywhere | Local machine only |
| **Backup** | ✅ Automatic | Manual |
| **Version Control** | ✅ Built-in | Manual |
| **Audit Trail** | ✅ Complete | Limited |
| **Setup Complexity** | Medium | Low |
| **Dependencies** | Box SDK | None |
| **Internet Required** | Yes | No |
| **Cost** | Box subscription | Free |

---

## 🔄 Migration Guide

### From Local to Box

1. **Install dependencies**:
   ```powershell
   pip install -r requirements_box.txt
   ```

2. **Set up Box application** (one-time):
   - Follow [BOX_SETUP_GUIDE.md](BOX_SETUP_GUIDE.md)
   - Download box_config.json

3. **Create Box folders**:
   - Input folder for source files
   - Output folder for results

4. **Update configuration**:
   ```yaml
   box:
     enabled: true
   ```

5. **Upload existing files to Box**:
   - Move input files to Box Input folder
   - Keep local copies as backup

6. **Test the workflow**:
   ```powershell
   python certification_workflow_box.py
   ```

7. **Verify results in Box Output folder**

### From Box to Local

Simply disable Box in config:

```yaml
box:
  enabled: false
```

The workflow will automatically use local file paths.

---

## 🐛 Troubleshooting

### Common Issues

#### 1. "boxsdk not installed"

**Solution**:
```powershell
pip install boxsdk[jwt]
```

#### 2. "Box API error: 401 Unauthorized"

**Causes**:
- Application not authorized
- Invalid credentials
- Expired token

**Solution**:
- Check Box Admin Console → Apps → Authorize
- Verify box_config.json is correct
- Regenerate keypair if needed

#### 3. "Folder ID not found"

**Solution**:
- Verify folder IDs in Box URL
- Check folder permissions
- Ensure service account has access

#### 4. "Could not identify input files"

**Solution**:
- Check file naming patterns in config.yaml
- Verify files exist in Box folder
- Check file extensions match patterns

#### 5. Files not uploading

**Solution**:
- Verify output folder ID
- Check write permissions
- Ensure sufficient Box storage

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check logs:
```powershell
Get-Content certification_workflow.log -Tail 100
```

---

## 📈 Performance Considerations

### File Size Limits

- Box API: 50 GB per file
- Recommended: < 100 MB for optimal performance
- Large files: Use chunked upload (handled automatically)

### Rate Limits

- Box API: 10 requests/second per user
- Workflow implements automatic retry with backoff
- Configure in config.yaml:
  ```yaml
  box:
    retry:
      max_attempts: 3
      delay_seconds: 5
  ```

### Network Considerations

- Download speed depends on internet connection
- Typical: 2-5 MB/s for Box downloads
- Use local mode for offline processing

---

## 🔮 Future Enhancements

Potential improvements for future versions:

- [ ] OAuth 2.0 authentication support
- [ ] Parallel file downloads/uploads
- [ ] Box webhook integration for real-time processing
- [ ] Box metadata tagging
- [ ] Box retention policies
- [ ] Box collaboration management
- [ ] Progress bars for large file transfers
- [ ] Resume interrupted downloads
- [ ] Differential sync (only changed files)

---

## 📚 Additional Resources

### Documentation
- [BOX_SETUP_GUIDE.md](BOX_SETUP_GUIDE.md) - Complete setup instructions
- [BOX_QUICK_START.md](BOX_QUICK_START.md) - Quick start guide
- [config.yaml](config.yaml) - Configuration reference

### External Links
- [Box Developer Documentation](https://developer.box.com/)
- [Box Python SDK](https://github.com/box/box-python-sdk)
- [Box JWT Authentication](https://developer.box.com/guides/authentication/jwt/)
- [IBM Box Portal](https://ibm.account.box.com)

### Support
- Check workflow logs: `certification_workflow.log`
- Review Box API status: https://status.box.com/
- Contact Box support for API issues

---

## 📝 Version History

### Version 1.0.0 (2026-05-28)
- ✅ Initial Box integration
- ✅ JWT authentication support
- ✅ Automatic file download/upload
- ✅ Configurable folder management
- ✅ Error handling and retry logic
- ✅ Comprehensive documentation

---

## 🤝 Contributing

To contribute improvements:

1. Test changes with both Box and local modes
2. Update documentation
3. Add error handling
4. Follow existing code style
5. Update version history

---

## 📄 License

This integration is part of the IBM Certification Workflow project.

---

## 👥 Credits

**Developed by**: IBM BOB (Autonomous AI Agent)  
**Date**: 2026-05-28  
**Version**: 1.0.0

---

**Made with Bob** 🤖

*For questions or support, refer to the troubleshooting section or contact your Box administrator.*