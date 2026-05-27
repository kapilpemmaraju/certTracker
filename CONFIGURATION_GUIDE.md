# Configuration Guide - Scalable Certification Workflow

## 📋 Overview

The enhanced certification workflow (v2.0) is fully configuration-driven, making it scalable, maintainable, and loosely coupled. All settings are controlled through the `config.yaml` file.

## 🏗️ Architecture Benefits

### Loose Coupling
- **Configuration separated from code**: Change behavior without modifying code
- **Dependency injection**: Configuration injected into workflow at runtime
- **Environment-specific configs**: Different configs for dev, test, prod

### Scalability
- **Batch processing**: Configurable batch sizes for large datasets
- **Parallel processing**: Enable multi-threading for performance
- **Memory optimization**: Chunk processing for large files
- **Caching**: Reduce redundant operations

### Maintainability
- **Single source of truth**: All settings in one place
- **Version control**: Track configuration changes
- **Documentation**: Self-documenting configuration
- **Validation**: Built-in configuration validation

## 📁 Configuration File Structure

```yaml
config.yaml
├── files                    # File paths and locations
├── processing              # Data processing rules
├── notifications           # Notification templates
├── email                   # Email configuration
├── logging                 # Logging settings
├── performance             # Performance tuning
├── validation              # Data validation rules
├── output                  # Output format settings
├── monitoring              # Metrics and monitoring
├── scheduling              # Automation scheduling
├── advanced                # Advanced features
└── features                # Feature flags
```

## 🔧 Key Configuration Sections

### 1. File Paths Configuration

```yaml
files:
  file_a:
    path: "Active Offshore Cloud List-05212026.xlsx"
    email_column: "EMP_INTRANETID"
  
  file_b:
    path: "T2G Certification_Financial Services as on 11 May 2026.xlsx"
    worksheet: "T2G Certification data-11 May"
    email_column: "Internet Email"
    client_column: "Global_Client_Name"
  
  output:
    directory: "./output"
    create_if_missing: true
```

**Benefits:**
- ✅ Change file paths without code modification
- ✅ Support multiple environments (dev, test, prod)
- ✅ Automatic output directory creation
- ✅ Flexible column name mapping

### 2. Processing Configuration

```yaml
processing:
  target_client: "WESTPAC BANKING CORPORATION"
  case_sensitive: false
  
  email_matching:
    case_sensitive: false
    trim_whitespace: true
    validate_format: true
  
  required_fields:
    - "Internet Email"
    - "Vendor"
    - "Credential Title"
    - "Credential Award Date"
    - "Credential Expiry Date"
```

**Benefits:**
- ✅ Easy client switching
- ✅ Configurable field extraction
- ✅ Flexible matching rules
- ✅ Data quality controls

### 3. Environment Variables

Use environment variables for sensitive data:

```yaml
email:
  smtp:
    server: "${SMTP_SERVER}"
    port: "${SMTP_PORT}"
  
  auth:
    username: "${SENDER_EMAIL}"
    password: "${SENDER_PASSWORD}"
```

**Syntax:**
- `${VAR_NAME}` - Required variable
- `${VAR_NAME:default}` - Variable with default value

**Example:**
```yaml
output:
  directory: "${OUTPUT_DIR:./output}"  # Defaults to ./output
```

### 4. Feature Flags

Enable/disable features without code changes:

```yaml
features:
  enable_email_sending: false
  enable_backup: true
  enable_validation: true
  enable_monitoring: true
  enable_parallel_processing: false
  enable_caching: true
```

**Benefits:**
- ✅ Safe feature rollout
- ✅ A/B testing
- ✅ Quick feature toggle
- ✅ Environment-specific features

## 🚀 Usage Examples

### Example 1: Change Target Client

```yaml
# config.yaml
processing:
  target_client: "COMMONWEALTH BANK"  # Changed from Westpac
```

Run workflow - no code changes needed!

### Example 2: Multiple Environments

**Development (config-dev.yaml):**
```yaml
files:
  output:
    directory: "./output-dev"

logging:
  level: "DEBUG"

features:
  enable_email_sending: false
```

**Production (config-prod.yaml):**
```yaml
files:
  output:
    directory: "/mnt/shared/certification-output"

logging:
  level: "INFO"

features:
  enable_email_sending: true
```

**Usage:**
```python
# Load specific config
config = ConfigLoader("config-prod.yaml")
workflow = CertificationWorkflowV2(config)
```

### Example 3: Custom Output Formats

```yaml
output:
  spreadsheet:
    enabled: true
    format: "xlsx"
    freeze_header: true
    auto_filter: true
  
  csv_export:
    enabled: true
    delimiter: ","
  
  json_export:
    enabled: true
    pretty_print: true
```

### Example 4: Performance Tuning

```yaml
performance:
  batch_size: 1000
  chunk_size: 10000
  
  parallel:
    enabled: true
    max_workers: 4
  
  cache:
    enabled: true
    ttl: 3600
```

## 📊 Configuration Validation

The workflow validates configuration on startup:

```python
from config_loader import ConfigLoader

config = ConfigLoader("config.yaml")

if config.validate():
    print("✅ Configuration is valid")
else:
    print("❌ Configuration validation failed")
```

**Validation Checks:**
- Required keys present
- File paths exist (if enabled)
- Valid data types
- Valid port numbers
- Valid email formats

## 🔄 Dynamic Configuration

### Reading Configuration Values

```python
# Get single value
target_client = config.get('processing.target_client')

# Get with default
batch_size = config.get('performance.batch_size', 1000)

# Get file path
file_a_path = config.get_file_path('files.file_a.path', base_dir)
```

### Updating Configuration

```python
# Set value
config.set('processing.target_client', 'NEW CLIENT')

# Save changes
config.save('config-modified.yaml')
```

### Reloading Configuration

```python
# Reload from file
config.reload()
```

## 🎯 Best Practices

### 1. Environment Variables for Secrets

**❌ Don't:**
```yaml
email:
  auth:
    password: "mypassword123"  # Never hardcode passwords!
```

**✅ Do:**
```yaml
email:
  auth:
    password: "${SENDER_PASSWORD}"  # Use environment variable
```

### 2. Version Control

**Include in Git:**
- `config.yaml` (with placeholders)
- `config-template.yaml`
- `config-dev.yaml`

**Exclude from Git (.gitignore):**
```
config-prod.yaml
config-local.yaml
*.secret.yaml
```

### 3. Configuration Profiles

Create profile-specific configs:

```
config.yaml              # Base configuration
config-dev.yaml          # Development overrides
config-test.yaml         # Testing overrides
config-prod.yaml         # Production overrides
```

### 4. Documentation

Document all configuration options:

```yaml
processing:
  # Target client name to filter (case-insensitive by default)
  # Example: "WESTPAC BANKING CORPORATION"
  target_client: "WESTPAC BANKING CORPORATION"
  
  # Enable case-sensitive client matching
  # Default: false
  case_sensitive: false
```

## 🔍 Configuration Schema

### Required Fields

```yaml
files.file_a.path: string
files.file_a.email_column: string
files.file_b.path: string
files.file_b.email_column: string
files.file_b.client_column: string
processing.target_client: string
```

### Optional Fields (with defaults)

```yaml
files.output.directory: string (default: "./output")
processing.case_sensitive: boolean (default: false)
processing.missing_data_placeholder: string (default: "Not Available")
logging.level: string (default: "INFO")
features.enable_email_sending: boolean (default: false)
```

## 📝 Configuration Templates

### Minimal Configuration

```yaml
# Minimal config - only required fields
files:
  file_a:
    path: "employees.xlsx"
    email_column: "Email"
  
  file_b:
    path: "certifications.xlsx"
    email_column: "Email"
    client_column: "Client"

processing:
  target_client: "CLIENT NAME"
```

### Full Configuration

See `config.yaml` for complete example with all options.

## 🛠️ Troubleshooting

### Issue: Configuration file not found

```
FileNotFoundError: Configuration file not found: config.yaml
```

**Solution:**
- Ensure `config.yaml` exists in the working directory
- Use absolute path: `ConfigLoader("/full/path/to/config.yaml")`

### Issue: Environment variable not set

```
Configuration value is empty: ${SMTP_SERVER}
```

**Solution:**
```bash
# Set environment variable
export SMTP_SERVER="smtp.gmail.com"

# Or use default value in config
smtp:
  server: "${SMTP_SERVER:smtp.gmail.com}"
```

### Issue: Invalid YAML syntax

```
yaml.scanner.ScannerError: mapping values are not allowed here
```

**Solution:**
- Check YAML indentation (use spaces, not tabs)
- Validate YAML syntax: https://www.yamllint.com/
- Use quotes for strings with special characters

## 📚 Advanced Topics

### 1. Configuration Inheritance

```python
# Load base config
base_config = ConfigLoader("config.yaml")

# Override with environment-specific config
prod_config = ConfigLoader("config-prod.yaml")

# Merge configurations
merged = {**base_config.get_all(), **prod_config.get_all()}
```

### 2. Configuration Encryption

For sensitive configurations:

```python
from cryptography.fernet import Fernet

# Encrypt configuration
key = Fernet.generate_key()
cipher = Fernet(key)
encrypted = cipher.encrypt(config_data.encode())

# Decrypt configuration
decrypted = cipher.decrypt(encrypted).decode()
```

### 3. Remote Configuration

Load configuration from remote source:

```python
import requests

# Fetch from API
response = requests.get("https://config-server/api/config")
config_data = response.json()

# Load into ConfigLoader
config = ConfigLoader()
config.config = config_data
```

## 🎓 Summary

The configuration-driven architecture provides:

✅ **Loose Coupling**: Configuration separated from code
✅ **Scalability**: Easy to scale and optimize
✅ **Flexibility**: Change behavior without code changes
✅ **Maintainability**: Single source of truth
✅ **Security**: Environment variables for secrets
✅ **Testability**: Easy to test with different configs
✅ **Documentation**: Self-documenting configuration

---

**Next Steps:**
1. Review `config.yaml` for all available options
2. Create environment-specific configurations
3. Set up environment variables for secrets
4. Test with different configurations
5. Document custom configuration changes

For more information, see:
- `README.md` - Complete documentation
- `QUICK_START.md` - Getting started guide
- `EMAIL_SETUP_GUIDE.md` - Email configuration