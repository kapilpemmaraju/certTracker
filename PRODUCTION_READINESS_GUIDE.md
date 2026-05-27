# 🚀 Production Readiness Guide

## Overview
This guide explains how to configure the IBM Certifications Tracker for production use and what settings need to be changed from test mode to production mode.

---

## 📋 Quick Checklist

Before going to production, ensure:
- [ ] Test mode is disabled in GUI
- [ ] Draft mode is disabled (or keep enabled for review)
- [ ] Email limit is set to 0 (no limit)
- [ ] Test email is cleared
- [ ] File paths are correct
- [ ] Backup is enabled
- [ ] Logging is configured
- [ ] All workflows tested successfully

---

## ⚙️ Configuration File: `config.yaml`

### 🧪 Test Mode Settings (Lines 119-123)

**Current Configuration (TEST MODE):**
```yaml
test_mode:
  enabled: true                          # ⚠️ CHANGE TO false FOR PRODUCTION
  test_recipient: "your.email@ibm.com"   # ⚠️ Not used in production
  limit_emails: 3                        # ⚠️ CHANGE TO 0 FOR PRODUCTION
  use_draft_mode: true                   # ⚠️ CHANGE TO false FOR PRODUCTION
```

**Production Configuration:**
```yaml
test_mode:
  enabled: false                         # ✅ Disabled for production
  test_recipient: ""                     # ✅ Not used
  limit_emails: 0                        # ✅ No limit
  use_draft_mode: false                  # ✅ Send emails directly
```

---

## 🎯 GUI Settings

### Test Mode (In Application)

**For Testing:**
1. ✅ **Enable Test Mode** checkbox
2. 📧 **Test Email**: Enter your email (e.g., `kapilpemmaraju@in.ibm.com`)
3. 📊 **Email Limit**: Set to 3-5 for testing
4. 📝 **Enable Draft Mode**: Keep checked to review emails

**For Production:**
1. ❌ **Disable Test Mode** checkbox
2. 📧 **Test Email**: Leave empty (not used)
3. 📊 **Email Limit**: Set to 0 (no limit)
4. 📝 **Draft Mode**: 
   - Keep **ENABLED** if you want to review emails before sending
   - **DISABLE** for fully automated sending

---

## 📁 File Paths Configuration (Lines 7-22)

### Current Settings:
```yaml
files:
  file_a:
    path: "Active Offshore Cloud List-05212026.xlsx"
    email_column: "EMP_INTRANETID"
    
  file_b:
    path: "T2G Certification_Financial Services as on 11 May 2026.xlsx"
    worksheet: "T2G Certification data-11 May"
    hc_worksheet: "HC Certification status-11 May"
    email_column: "Internet Email"
    client_column: "Global_Client_Name"
```

### ⚠️ Update for Production:
- Update file paths if files are in different location
- Update worksheet names if they change monthly
- Verify column names match your Excel files

---

## 🔐 Email Configuration (Lines 98-135)

### Current Settings:
```yaml
email:
  enabled: false                         # ⚠️ Not used (using Outlook COM)
  
  # Rate limiting
  rate_limit:
    enabled: true
    emails_per_minute: 30                # ✅ Good for production
    delay_between_emails: 2              # ✅ 2 seconds delay
```

**Note:** The system uses **Outlook Win32 COM** interface, not SMTP. The email configuration section is not actively used but kept for reference.

---

## 📊 Logging Configuration (Lines 137-153)

### Current Settings:
```yaml
logging:
  level: "INFO"                          # ✅ Good for production
  
  file:
    enabled: true                        # ✅ Keep enabled
    path: "certification_workflow.log"
    max_size_mb: 10                      # ✅ Rotate at 10MB
    backup_count: 5                      # ✅ Keep 5 backups
```

**For Production:**
- Keep logging **ENABLED**
- Set level to **INFO** (not DEBUG)
- Monitor log files regularly
- Archive old logs periodically

---

## 💾 Backup Configuration (Lines 28-32)

### Current Settings:
```yaml
backup:
  enabled: true                          # ✅ Keep enabled
  directory: "./backup"
  retention_days: 30                     # ✅ Keep 30 days
```

**For Production:**
- Keep backup **ENABLED**
- Ensure backup directory has sufficient space
- Review retention policy (30 days recommended)

---

## 🎯 Processing Configuration (Lines 34-71)

### Target Client:
```yaml
processing:
  target_client: "WESTPAC BANKING CORPORATION"  # ✅ Correct
  case_sensitive: false                         # ✅ Good
```

**For Production:**
- Verify target client name matches Excel data exactly
- Keep case_sensitive as **false** for flexibility

---

## 📈 Performance Configuration (Lines 155-171)

### Current Settings:
```yaml
performance:
  batch_size: 1000                       # ✅ Good for production
  chunk_size: 10000                      # ✅ For large files
  
  parallel:
    enabled: false                       # ⚠️ Can enable for better performance
    max_workers: 4
```

**For Production:**
- Consider enabling **parallel processing** for large datasets
- Adjust **batch_size** based on system resources

---

## 🔍 Validation Configuration (Lines 173-188)

### Current Settings:
```yaml
validation:
  check_file_exists: true                # ✅ Keep enabled
  check_required_columns: true           # ✅ Keep enabled
  validate_email_format: true            # ✅ Keep enabled
```

**For Production:**
- Keep all validation **ENABLED**
- Helps catch errors early

---

## 🚨 Feature Flags (Lines 268-276)

### Current Settings:
```yaml
features:
  enable_email_sending: false            # ⚠️ Not used (Outlook COM used instead)
  enable_backup: true                    # ✅ Keep enabled
  enable_validation: true                # ✅ Keep enabled
  enable_monitoring: true                # ✅ Keep enabled
  enable_audit_trail: true               # ✅ Keep enabled
```

**For Production:**
- Keep **backup**, **validation**, **monitoring**, and **audit_trail** enabled
- These features help maintain system reliability

---

## 📝 Step-by-Step Production Deployment

### 1. **Test Phase** (Current State)
```bash
# Launch GUI
python certification_gui.py

# Settings:
✅ Test Mode: ENABLED
✅ Test Email: your.email@ibm.com
✅ Email Limit: 3
✅ Draft Mode: ENABLED
```

### 2. **Pre-Production Phase**
```bash
# Settings:
✅ Test Mode: ENABLED
✅ Test Email: your.email@ibm.com
✅ Email Limit: 10-20
✅ Draft Mode: ENABLED (review all emails)
```

### 3. **Production Phase**
```bash
# Settings:
❌ Test Mode: DISABLED
📧 Test Email: (empty)
📊 Email Limit: 0
📝 Draft Mode: ENABLED (recommended) or DISABLED (fully automated)
```

---

## 🎯 Workflow-Specific Settings

### 📊 Workflow 1: Status Notifications
- **Purpose**: Send certification status to employees WITH certifications
- **Source**: "T2G Certification data-11 May" worksheet
- **Email**: Direct to employee
- **CC**: None

### ⚠️ Workflow 2: Completion Reminders
- **Purpose**: Remind employees WITHOUT certifications
- **Source**: "HC Certification status-11 May" worksheet
- **Filter**: "All T2G Certified status" = "Not Certified"
- **Email**: To employee
- **CC**: Manager (GLOBAL_MGR column)

### 🎯 Workflow 3: Industry Badge Reminders
- **Purpose**: Remind employees with "No Badge"
- **Source**: "HC Certification status-11 May" worksheet
- **Filter**: "Industry Badge Met Ind Cred Lvl?" = "No Badge"
- **Email**: To employee
- **CC**: Manager (GLOBAL_MGR column)

---

## 🔒 Security Considerations

### Email Security:
- ✅ Uses **Outlook Win32 COM** (no password storage)
- ✅ Emails sent from your Outlook account
- ✅ No SMTP credentials needed
- ✅ Respects Outlook security settings

### Data Security:
- ✅ Excel files stored locally
- ✅ No data sent to external servers
- ✅ Logs contain no sensitive data
- ✅ Backup files encrypted by Windows

---

## 📊 Monitoring & Maintenance

### Daily Tasks:
1. Check log files for errors
2. Verify email drafts (if draft mode enabled)
3. Review output spreadsheets

### Weekly Tasks:
1. Archive old log files
2. Clean up backup directory
3. Update Excel files with latest data

### Monthly Tasks:
1. Update worksheet names in config.yaml
2. Verify column names haven't changed
3. Review and update file paths

---

## 🆘 Troubleshooting

### Issue: Emails not sending
**Solution:**
1. Check if Outlook is running
2. Verify Draft Mode setting
3. Check Test Mode is disabled for production

### Issue: No employees found
**Solution:**
1. Verify worksheet names in config.yaml
2. Check column names match Excel files
3. Verify target client name is correct

### Issue: Column not found errors
**Solution:**
1. Open Excel files and verify column names
2. Update config.yaml with exact column names
3. Check for extra spaces in column names

---

## 📞 Support

For issues or questions:
1. Check log files: `certification_workflow.log`
2. Review error messages in GUI console
3. Verify config.yaml settings
4. Contact IBM BOB support team

---

## ✅ Production Readiness Checklist

Before going live:

### Configuration:
- [ ] config.yaml reviewed and updated
- [ ] File paths verified
- [ ] Worksheet names confirmed
- [ ] Column names validated
- [ ] Target client name correct

### Testing:
- [ ] All 3 workflows tested with test mode
- [ ] Email drafts reviewed and approved
- [ ] Output spreadsheets verified
- [ ] Manager CC functionality tested
- [ ] Error handling tested

### Security:
- [ ] Outlook configured and working
- [ ] No sensitive data in logs
- [ ] Backup directory secured
- [ ] Access controls in place

### Monitoring:
- [ ] Logging enabled and working
- [ ] Log rotation configured
- [ ] Backup enabled
- [ ] Audit trail enabled

### Documentation:
- [ ] Team trained on GUI usage
- [ ] Production procedures documented
- [ ] Troubleshooting guide reviewed
- [ ] Support contacts identified

---

## 🎉 Ready for Production!

Once all checklist items are complete:
1. Disable Test Mode in GUI
2. Set Email Limit to 0
3. Choose Draft Mode preference
4. Run workflows
5. Monitor logs and results

**Good luck with your production deployment!** 🚀

---

*Last Updated: 2026-05-22*  
*Version: 2.0.0*  
*Author: IBM BOB*

# Made with Bob