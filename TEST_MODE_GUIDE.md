# Test Mode Guide for Certification Workflow

## Overview
This guide explains how to safely test the certification workflow without sending emails to all employees.

## Test Mode Features

### 1. **Draft Mode** (Default)
- Creates email drafts in Outlook instead of sending
- Allows manual review before sending
- **Recommended for all testing**

### 2. **Email Limiting**
- Send only to first N employees
- Prevents mass email sending during tests
- Default: 3 emails

### 3. **Test Recipient Override**
- Redirect all emails to a single test address
- Perfect for testing email content and formatting
- Your actual employees won't receive test emails

## Quick Start - Test Workflow

### Option 1: Simple Test (Recommended)
```bash
# Creates 3 email drafts in Outlook
python test_workflow.py
```

### Option 2: Test with Your Email
```bash
# All 3 test emails will be sent to your address
python test_workflow.py --test-email your.email@ibm.com
```

### Option 3: Test More Emails
```bash
# Creates 10 email drafts
python test_workflow.py --limit 10
```

### Option 4: Actually Send (Use with Caution!)
```bash
# Sends 3 emails to actual recipients
python test_workflow.py --send-mode
```

## Configuration File Test Mode

You can also configure test mode in `config.yaml`:

```yaml
email:
  test_mode:
    enabled: true              # Enable test mode
    test_recipient: "your.email@ibm.com"  # Your test email
    limit_emails: 3            # Number of emails to send
    use_draft_mode: true       # Create drafts instead of sending
```

## Testing Workflow

### Step 1: Initial Test (3 Drafts)
```bash
python test_workflow.py
```
**What happens:**
- Processes all Excel data
- Creates 3 email drafts in Outlook
- No emails sent
- No notification history recorded

**Check:**
1. Open Outlook
2. Go to Drafts folder
3. Review the 3 email drafts
4. Verify content, formatting, and recipient info

### Step 2: Test with Your Email
```bash
python test_workflow.py --test-email your.email@ibm.com --limit 5
```
**What happens:**
- Creates 5 email drafts
- All addressed to your email
- Contains actual employee certification data

**Check:**
1. Review drafts in Outlook
2. Send one draft to yourself
3. Verify email arrives correctly
4. Check formatting in your inbox

### Step 3: Production Run
Once satisfied with tests:
```bash
python certification_workflow_outlook.py
```
**What happens:**
- Processes all employees
- Creates drafts for all 126 employees
- Records notification history
- Prevents future duplicates

## Test Scenarios

### Scenario 1: Test Email Content
**Goal:** Verify email formatting and content
```bash
python test_workflow.py --test-email your.email@ibm.com --limit 1
```
Review the single draft to ensure:
- Subject line is correct
- Greeting uses proper name
- Certifications are listed correctly
- Footer is professional

### Scenario 2: Test Multiple Recipients
**Goal:** Verify different employee data
```bash
python test_workflow.py --limit 5
```
Review 5 different drafts to ensure:
- Each has correct employee name
- Certifications match the employee
- No data mixing between employees

### Scenario 3: Test Actual Sending
**Goal:** Verify email delivery (send to yourself only!)
```bash
python test_workflow.py --test-email your.email@ibm.com --limit 1 --send-mode
```
**⚠️ WARNING:** This actually sends an email!

## Safety Features

### 1. Draft Mode Protection
- Default behavior creates drafts
- Must explicitly use `--send-mode` to send
- Prevents accidental mass emails

### 2. Email Limiting
- Default limit: 3 emails
- Prevents testing with all 126 employees
- Configurable via `--limit` parameter

### 3. Test Recipient Override
- Redirects all emails to test address
- Original recipients never contacted
- Perfect for content testing

### 4. No History Recording in Test Mode
- Test emails don't affect notification history
- Can test multiple times
- Production run will still send to everyone

## Common Test Commands

```bash
# Quick test - 3 drafts
python test_workflow.py

# Test with your email - 3 drafts to you
python test_workflow.py --test-email your.email@ibm.com

# Test more emails - 10 drafts
python test_workflow.py --limit 10

# Test single email to yourself - actually send
python test_workflow.py --test-email your.email@ibm.com --limit 1 --send-mode

# No limit - all employees (drafts only)
python test_workflow.py --limit 0

# Production run - all employees, all drafts
python certification_workflow_outlook.py
```

## Troubleshooting

### Issue: No drafts created
**Solution:** Check Outlook is running and accessible

### Issue: Wrong email content
**Solution:** Verify Excel files are up to date

### Issue: Test emails sent to actual recipients
**Solution:** Always use `--test-email` parameter for testing

### Issue: Too many test emails
**Solution:** Use `--limit` parameter to control quantity

## Best Practices

1. **Always start with draft mode**
   - Review before sending
   - Catch errors early

2. **Test with your own email first**
   - Verify delivery and formatting
   - Check spam folder

3. **Limit test emails**
   - Start with 1-3 emails
   - Increase gradually

4. **Review test reports**
   - Check `output/Test_Report_*.txt`
   - Verify metrics

5. **Clear test drafts**
   - Delete test drafts from Outlook
   - Keep Drafts folder clean

## Production Checklist

Before running production workflow:

- [ ] Tested with draft mode
- [ ] Reviewed email content
- [ ] Verified recipient information
- [ ] Checked Excel files are current
- [ ] Tested with your own email
- [ ] Reviewed test reports
- [ ] Cleared test drafts from Outlook
- [ ] Confirmed Outlook is running
- [ ] Ready to create 126 drafts

## Support

For issues or questions:
1. Check test reports in `output/` directory
2. Review logs in `test_workflow.log`
3. Verify configuration in `config.yaml`
4. Consult main documentation files

---

**Remember:** Test mode is your safety net. Use it liberally before production runs!