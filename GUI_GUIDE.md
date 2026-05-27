# IBM Certification Workflow GUI Guide

## Overview
The GUI provides a user-friendly interface to manage both certification workflows:
1. **Certification Status Notifications** - For employees who HAVE certifications
2. **Certification Completion Reminders** - For employees who NEED certifications

## Quick Start

### Launch the GUI
```bash
cd C:/Users/KAPILPEMMARAJU/Downloads/CertificationsWestpac
python certification_gui.py
```

## GUI Features

### 1. Workflow Selection
Choose which workflow to run:
- **📊 Certification Status Notifications**
  - Sends notifications about existing certifications
  - Uses "T2G Certification data-11 May" worksheet
  - Notifies 126 employees with 614 certifications
  
- **⚠️ Certification Completion Reminders**
  - Sends reminders to complete certifications
  - Uses "HC Certification status-11 May" worksheet
  - Finds employees with "Not Certified" or "No badge" status
  - CC's manager on each email

### 2. Configuration Options

#### Test Mode (Recommended for First Run)
- ✅ **Enable Test Mode** - Checkbox to enable testing
- **Test Email** - Enter your email address (e.g., `your.email@ibm.com`)
  - All emails will be sent to this address instead of actual recipients
  - Leave blank to use actual recipient emails
- **Email Limit** - Number of emails to send (default: 3)
  - Set to 0 for no limit
  - Useful for testing without sending to everyone

#### Draft Mode (Highly Recommended)
- ✅ **Draft Mode** - Creates email drafts instead of sending
- Allows manual review before sending
- Drafts appear in Outlook Drafts folder

### 3. Action Buttons

- **📧 Send Emails** - Starts the selected workflow
- **🔄 Clear Log** - Clears the progress log
- **❌ Exit** - Closes the application

### 4. Progress & Log
- **Progress Bar** - Shows workflow is running
- **Log Area** - Displays real-time progress and results
- **Status Bar** - Shows current status

## Usage Examples

### Example 1: Test Certification Status Notifications
1. Launch GUI: `python certification_gui.py`
2. Select: **📊 Send Certification Status Notifications**
3. Enable: **🧪 Test Mode**
4. Enter: **Test Email** = `your.email@ibm.com`
5. Set: **Email Limit** = `3`
6. Enable: **📝 Draft Mode**
7. Click: **📧 Send Emails**
8. Review: Check Outlook Drafts folder for 3 drafts

### Example 2: Test Certification Reminders
1. Launch GUI: `python certification_gui.py`
2. Select: **⚠️ Send Certification Completion Reminders**
3. Enable: **🧪 Test Mode**
4. Enter: **Test Email** = `your.email@ibm.com`
5. Set: **Email Limit** = `5`
6. Enable: **📝 Draft Mode**
7. Click: **📧 Send Emails**
8. Review: Check Outlook Drafts folder for 5 reminder drafts

### Example 3: Production Run (After Testing)
1. Launch GUI: `python certification_gui.py`
2. Select desired workflow
3. **Disable Test Mode** (uncheck)
4. Keep **Draft Mode enabled** (recommended)
5. Click: **📧 Send Emails**
6. Confirm the action
7. Review all drafts in Outlook
8. Send manually or in batches

## Workflow Details

### Certification Status Notifications
**Purpose:** Inform employees about their existing certifications

**Process:**
1. Loads File A (Active Offshore Cloud List)
2. Loads File B worksheet "T2G Certification data-11 May"
3. Filters for Westpac Banking Corporation
4. Matches employees with certifications
5. Sends notification with certification details

**Email Content:**
- Lists all certifications
- Shows vendor, award date, expiry date
- Professional formatting

### Certification Completion Reminders
**Purpose:** Remind employees to complete required certifications

**Process:**
1. Loads File A (Active Offshore Cloud List)
2. Loads File B worksheet "HC Certification status-11 May"
3. Filters for Westpac Banking Corporation
4. Finds employees with:
   - "All T2G Certified status" = "Not Certified" OR
   - "Industry badge Met Ind Cred Lvl?" = "No badge"
5. Sends reminder with manager CC'd

**Email Content:**
- Shows current certification status
- Lists required actions
- Explains importance
- CC's manager (GLOBAL_MGR)

## Safety Features

### 1. Test Mode Protection
- Redirects all emails to test address
- Limits number of emails sent
- Prevents accidental mass emails

### 2. Draft Mode Protection
- Creates drafts instead of sending
- Allows manual review
- Must manually send from Outlook

### 3. Confirmation Dialog
- Shows summary before running
- Requires explicit confirmation
- Displays all settings

### 4. Real-time Logging
- Shows progress in GUI
- Logs saved to `certification_gui.log`
- Easy troubleshooting

## Best Practices

### First Time Use
1. ✅ Enable Test Mode
2. ✅ Enter your test email
3. ✅ Set Email Limit to 3
4. ✅ Enable Draft Mode
5. ✅ Review drafts in Outlook
6. ✅ Verify content and formatting

### Before Production
1. ✅ Test both workflows
2. ✅ Verify Excel files are current
3. ✅ Check Outlook is running
4. ✅ Review test email content
5. ✅ Confirm recipient lists
6. ✅ Keep Draft Mode enabled

### Production Run
1. ✅ Disable Test Mode (or keep for safety)
2. ✅ Keep Draft Mode enabled
3. ✅ Review confirmation dialog
4. ✅ Monitor progress log
5. ✅ Review all drafts in Outlook
6. ✅ Send in batches if needed

## Troubleshooting

### GUI Won't Start
**Problem:** Python error or missing dependencies
**Solution:** 
```bash
pip install pandas openpyxl pyyaml pywin32
python certification_gui.py
```

### No Drafts Created
**Problem:** Outlook not running or COM error
**Solution:**
1. Open Microsoft Outlook
2. Ensure it's your default email client
3. Restart the GUI
4. Try again

### Wrong Worksheet Error
**Problem:** Worksheet name doesn't match
**Solution:**
1. Open File B in Excel
2. Check exact worksheet name
3. Update `config.yaml`:
   ```yaml
   files:
     file_b:
       hc_worksheet: "HC Certification status-11 May"
   ```

### Test Emails Not Redirected
**Problem:** Test mode not working
**Solution:**
1. Ensure Test Mode is checked
2. Enter valid test email address
3. Check log for "TEST MODE ENABLED" message

### Manager Not CC'd
**Problem:** GLOBAL_MGR column missing or empty
**Solution:**
1. Verify GLOBAL_MGR column exists in File B
2. Check it contains email addresses
3. Review log for errors

## Output Files

### Generated Files
- **Consolidated Spreadsheet:** `output/WESTPAC_BANKING_CORPORATION_*.xlsx`
- **Notification Messages:** `output/WESTPAC_BANKING_CORPORATION_*.txt`
- **GUI Log:** `certification_gui.log`
- **Workflow Metrics:** `output/workflow_metrics.json`

### Outlook Drafts
- Located in: **Outlook > Drafts** folder
- Review before sending
- Can edit if needed
- Send manually or in batches

## Keyboard Shortcuts

- **Alt+S** - Send Emails (when button focused)
- **Alt+C** - Clear Log (when button focused)
- **Alt+X** - Exit (when button focused)

## Tips & Tricks

### Batch Sending
1. Create all drafts first
2. Review in Outlook
3. Select multiple drafts
4. Right-click > Send

### Testing Strategy
1. Start with limit=1
2. Verify single email
3. Increase to 3-5
4. Test both workflows
5. Run production

### Error Recovery
1. Check log for errors
2. Fix issues in Excel files
3. Clear log
4. Try again

### Performance
- Large files may take 1-2 minutes
- Progress bar shows activity
- Don't close GUI while running
- Check log for progress

## Support

### Log Files
- **GUI Log:** `certification_gui.log`
- **Workflow Log:** `certification_workflow.log`
- **Test Log:** `test_workflow.log`

### Common Issues
1. **Outlook COM Error** - Restart Outlook
2. **File Not Found** - Check file paths in config.yaml
3. **Column Not Found** - Verify Excel column names
4. **No Employees Found** - Check filter criteria

### Getting Help
1. Check log files for errors
2. Review Excel file structure
3. Verify config.yaml settings
4. Test with small email limit first

---

## Quick Reference

### Test Mode Settings
```
✅ Test Mode: Enabled
Test Email: your.email@ibm.com
Email Limit: 3
✅ Draft Mode: Enabled
```

### Production Settings
```
❌ Test Mode: Disabled
✅ Draft Mode: Enabled (recommended)
```

### File Requirements
- **File A:** Active Offshore Cloud List-05212026.xlsx
- **File B:** T2G Certification_Financial Services as on 11 May 2026.xlsx
  - Worksheet 1: "T2G Certification data-11 May" (Status workflow)
  - Worksheet 2: "HC Certification status-11 May" (Reminder workflow)

---

**Remember:** Always test first, review drafts, and send carefully!