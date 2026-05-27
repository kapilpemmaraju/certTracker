# Quick Start Guide - Certification Workflow

## 🚀 Getting Started in 5 Minutes

### Prerequisites
- Python 3.11 or higher
- Required packages: `pandas`, `openpyxl`

### Installation

```bash
# Install required packages
pip install pandas openpyxl
```

### Running the Workflow

#### Option 1: Default Configuration (Recommended)

```bash
# Navigate to the directory
cd C:/Users/KAPILPEMMARAJU/Downloads/CertificationsWestpac

# Run the workflow
python certification_workflow.py
```

#### Option 2: Custom Configuration

```python
from certification_workflow import CertificationWorkflow

# Initialize with custom paths
workflow = CertificationWorkflow(
    file_a_path="path/to/your/active_cloud_list.xlsx",
    file_b_path="path/to/your/certification_data.xlsx",
    output_dir="path/to/output"
)

# Run the workflow
results = workflow.run()

# Check results
if results['success']:
    print(f"✅ Success! Generated {results['notifications_generated']} notifications")
    print(f"📊 Output: {results['output_spreadsheet']}")
    print(f"📧 Notifications: {results['notifications_file']}")
else:
    print("❌ Workflow failed. Check logs for details.")
```

## 📋 What You'll Get

After running the workflow, you'll find these files in the output directory:

1. **`Westpac_Certification_Consolidated_[timestamp].xlsx`**
   - Consolidated spreadsheet with all matched certifications
   - 614 records for 126 employees
   - Columns: Email, Name, Vendor, Title, Award Date, Expiry Date, etc.

2. **`Westpac_Certification_Notifications_[timestamp].txt`**
   - 126 personalized notification messages
   - Ready to send via email
   - Formatted with all certification details

3. **`certification_workflow.log`**
   - Detailed execution log
   - Useful for troubleshooting

## 📊 Expected Results

```
Status: SUCCESS
File A records: 225
File B total records: 38,336
Westpac records: 1,244
Matched records: 614
Unique emails: 126
Notifications generated: 126
```

## 🔧 Customization

### Change Target Client

Edit `certification_workflow.py`:

```python
self.target_client = 'YOUR_CLIENT_NAME'  # Line 42
```

### Change Column Names

Edit `certification_workflow.py`:

```python
self.file_a_email_col = 'YOUR_COLUMN_NAME'  # Line 39
self.file_b_email_col = 'YOUR_COLUMN_NAME'  # Line 40
```

### Change Worksheet Name

Edit `certification_workflow.py`:

```python
worksheet_name = 'YOUR_WORKSHEET_NAME'  # Line 130
```

## 📧 Email Configuration (Optional)

To send emails automatically:

```python
smtp_config = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': 'your-email@example.com',
    'sender_password': 'your-app-password',
    'test_mode': True,  # Set to False for production
    'test_recipient': 'test@example.com'
}

results = workflow.run(send_emails=True, smtp_config=smtp_config)
```

### Gmail Setup

1. Enable 2-factor authentication
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Use the App Password in `sender_password`

### Office 365 Setup

```python
smtp_config = {
    'smtp_server': 'smtp.office365.com',
    'smtp_port': 587,
    'sender_email': 'your-email@company.com',
    'sender_password': 'your-password',
    'test_mode': True,
    'test_recipient': 'test@company.com'
}
```

## 🐛 Troubleshooting

### Issue: "Module not found"
```bash
pip install pandas openpyxl
```

### Issue: "File not found"
- Check file paths are correct
- Use absolute paths if relative paths don't work
- Ensure files are not open in Excel

### Issue: "Column not found"
- Verify column names match exactly (case-sensitive)
- Check for extra spaces in column names
- Open Excel files to confirm column names

### Issue: "No matches found"
- Verify email addresses exist in both files
- Check client name spelling
- Review the log file for details

## 📖 Next Steps

1. ✅ Run the workflow with default settings
2. 📊 Review the output spreadsheet
3. 📧 Check the notification messages
4. 🔧 Customize for your needs
5. 📅 Schedule for regular execution

## 💡 Tips

- **Test First**: Run with a small dataset to verify configuration
- **Check Logs**: Always review `certification_workflow.log` for details
- **Backup Data**: Keep copies of original files
- **Test Emails**: Use `test_mode=True` before sending to all recipients
- **Schedule**: Use Windows Task Scheduler or cron for automation

## 📞 Need Help?

1. Check `README.md` for detailed documentation
2. Review `certification_workflow.log` for error details
3. Verify input file formats match expected structure
4. Contact IBM BOB for assistance

---

**Ready to go!** Run `python certification_workflow.py` to start processing your certification data.