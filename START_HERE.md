# 🚀 IBM Certification Workflow - Quick Start

## Launch the GUI Application

```bash
cd C:/Users/KAPILPEMMARAJU/Downloads/CertificationsWestpac
python certification_gui.py
```

## What You'll See

A graphical interface with:
- **Workflow Selection** - Choose which emails to send
- **Test Mode** - Safe testing with your email
- **Draft Mode** - Review before sending
- **Send Button** - Start the workflow

## First Time? Start Here!

### Step 1: Test with Your Email
1. Launch: `python certification_gui.py`
2. Select: **📊 Certification Status Notifications**
3. Check: **🧪 Test Mode**
4. Enter: Your email in **Test Email** field
5. Set: **Email Limit** = 3
6. Check: **📝 Draft Mode**
7. Click: **📧 Send Emails**

### Step 2: Check Outlook
1. Open Microsoft Outlook
2. Go to **Drafts** folder
3. You'll see 3 email drafts
4. All addressed to YOUR email
5. Review content and formatting

### Step 3: Production Run
Once satisfied with tests:
1. Uncheck **Test Mode** (or keep for safety)
2. Keep **Draft Mode** checked
3. Click **📧 Send Emails**
4. Review all drafts in Outlook
5. Send manually

## Two Workflows Available

### 1. Certification Status Notifications
- For employees WHO HAVE certifications
- Sends list of their current certifications
- 126 employees, 614 certifications

### 2. Certification Completion Reminders  
- For employees WHO NEED certifications
- Sends reminder to complete certifications
- CC's their manager
- Finds "Not Certified" and "No badge" status

## Safety Features

✅ **Test Mode** - Send to your email only
✅ **Draft Mode** - Review before sending  
✅ **Email Limiting** - Test with few emails
✅ **Confirmation Dialog** - Explicit approval needed

## Need Help?

- **Full Guide:** See `GUI_GUIDE.md`
- **Test Mode:** See `TEST_MODE_GUIDE.md`
- **Configuration:** See `CONFIGURATION_GUIDE.md`

## Quick Commands

```bash
# Launch GUI
python certification_gui.py

# Test command-line (alternative)
python test_workflow.py --test-email your.email@ibm.com --limit 3

# Run status workflow directly
python certification_workflow_outlook.py

# Run reminder workflow directly
python certification_reminder_workflow.py
```

## Files You Need

- ✅ `Active Offshore Cloud List-05212026.xlsx` (File A)
- ✅ `T2G Certification_Financial Services as on 11 May 2026.xlsx` (File B)
  - Worksheet: "T2G Certification data-11 May"
  - Worksheet: "HC Certification status-11 May"

## Output Location

All output files saved to: `output/` directory
- Consolidated spreadsheets
- Notification messages
- Tracking reports
- Metrics

## Outlook Drafts

Email drafts created in: **Outlook > Drafts** folder

---

**🎯 Remember:** Always test first, review drafts, send carefully!

**📧 Questions?** Check the log files or documentation guides.