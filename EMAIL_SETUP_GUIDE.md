# Email Setup Guide - Certification Workflow

## 📧 Email Integration Overview

This guide explains how to configure the certification workflow to automatically send email notifications to employees about their certification status.

## 🔐 Security Best Practices

**IMPORTANT**: Never hardcode passwords in your scripts!

### Recommended Approaches:

1. **Environment Variables** (Recommended)
2. **Configuration File** (with restricted permissions)
3. **Azure Key Vault / AWS Secrets Manager** (Enterprise)
4. **Interactive Input** (Development/Testing)

## 🚀 Quick Setup

### Option 1: Using Environment Variables (Recommended)

#### Step 1: Set Environment Variables

**Windows PowerShell:**
```powershell
$env:SMTP_SERVER = "smtp.gmail.com"
$env:SMTP_PORT = "587"
$env:SENDER_EMAIL = "your-email@example.com"
$env:SENDER_PASSWORD = "your-app-password"
```

**Windows Command Prompt:**
```cmd
set SMTP_SERVER=smtp.gmail.com
set SMTP_PORT=587
set SENDER_EMAIL=your-email@example.com
set SENDER_PASSWORD=your-app-password
```

**Linux/Mac:**
```bash
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SENDER_EMAIL="your-email@example.com"
export SENDER_PASSWORD="your-app-password"
```

#### Step 2: Update Workflow Script

Add this to `certification_workflow.py` in the `main()` function:

```python
import os

# Get SMTP configuration from environment variables
smtp_config = {
    'smtp_server': os.getenv('SMTP_SERVER'),
    'smtp_port': int(os.getenv('SMTP_PORT', 587)),
    'sender_email': os.getenv('SENDER_EMAIL'),
    'sender_password': os.getenv('SENDER_PASSWORD'),
    'test_mode': True,  # Set to False for production
    'test_recipient': os.getenv('TEST_EMAIL', 'test@example.com')
}

# Run with email sending
results = workflow.run(send_emails=True, smtp_config=smtp_config)
```

### Option 2: Using Configuration File

#### Step 1: Create `email_config.json`

```json
{
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your-email@example.com",
    "sender_password": "your-app-password",
    "test_mode": true,
    "test_recipient": "test@example.com"
}
```

**IMPORTANT**: Add `email_config.json` to `.gitignore`!

#### Step 2: Update Workflow Script

```python
import json

# Load SMTP configuration from file
with open('email_config.json', 'r') as f:
    smtp_config = json.load(f)

# Run with email sending
results = workflow.run(send_emails=True, smtp_config=smtp_config)
```

## 📮 Email Provider Setup

### Gmail Configuration

#### Prerequisites:
1. Gmail account with 2-Factor Authentication enabled
2. App Password generated

#### Steps:

1. **Enable 2-Factor Authentication**
   - Go to: https://myaccount.google.com/security
   - Enable 2-Step Verification

2. **Generate App Password**
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer" (or appropriate device)
   - Click "Generate"
   - Copy the 16-character password

3. **Configuration**
   ```python
   smtp_config = {
       'smtp_server': 'smtp.gmail.com',
       'smtp_port': 587,
       'sender_email': 'your-email@gmail.com',
       'sender_password': 'xxxx xxxx xxxx xxxx',  # App Password
       'test_mode': True,
       'test_recipient': 'test@gmail.com'
   }
   ```

#### Troubleshooting Gmail:
- Error "Username and Password not accepted": Use App Password, not regular password
- Error "Less secure app access": Enable 2FA and use App Password
- Rate limiting: Gmail has sending limits (500 emails/day for free accounts)

### Office 365 / Outlook Configuration

#### Prerequisites:
1. Office 365 account
2. SMTP authentication enabled

#### Configuration:
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

#### Troubleshooting Office 365:
- Error "Authentication failed": Check if SMTP AUTH is enabled in admin center
- Modern Authentication: May require OAuth2 (contact IT admin)
- Conditional Access: May block SMTP (contact IT admin)

### IBM Mail Configuration

#### Configuration:
```python
smtp_config = {
    'smtp_server': 'smtp.ibm.com',  # Or your IBM mail server
    'smtp_port': 587,
    'sender_email': 'your-email@ibm.com',
    'sender_password': 'your-password',
    'test_mode': True,
    'test_recipient': 'test@ibm.com'
}
```

**Note**: Contact IBM IT for specific SMTP server details and authentication requirements.

### Other Providers

| Provider | SMTP Server | Port | Notes |
|----------|-------------|------|-------|
| Yahoo | smtp.mail.yahoo.com | 587 | Requires App Password |
| Outlook.com | smtp-mail.outlook.com | 587 | Personal accounts |
| SendGrid | smtp.sendgrid.net | 587 | API key as password |
| Amazon SES | email-smtp.region.amazonaws.com | 587 | Requires SMTP credentials |

## 🧪 Testing Email Configuration

### Test Script

Create `test_email.py`:

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_email_config(smtp_server, smtp_port, sender_email, sender_password, test_recipient):
    """Test email configuration."""
    try:
        # Create test message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = test_recipient
        msg['Subject'] = 'Test Email - Certification Workflow'
        
        body = """
        This is a test email from the IBM Certification Workflow.
        
        If you received this email, your SMTP configuration is working correctly!
        
        Best regards,
        IBM BOB
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        print(f"Connecting to {smtp_server}:{smtp_port}...")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            print("Starting TLS...")
            server.starttls()
            print("Logging in...")
            server.login(sender_email, sender_password)
            print("Sending email...")
            server.send_message(msg)
        
        print(f"✅ Test email sent successfully to {test_recipient}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending test email: {e}")
        return False

# Test configuration
if __name__ == "__main__":
    test_email_config(
        smtp_server='smtp.gmail.com',
        smtp_port=587,
        sender_email='your-email@gmail.com',
        sender_password='your-app-password',
        test_recipient='test@example.com'
    )
```

Run the test:
```bash
python test_email.py
```

## 🔒 Security Considerations

### 1. Password Protection

**DO NOT:**
- ❌ Hardcode passwords in scripts
- ❌ Commit passwords to version control
- ❌ Share passwords in plain text
- ❌ Use personal passwords for automation

**DO:**
- ✅ Use environment variables
- ✅ Use App Passwords (not account passwords)
- ✅ Use secrets management services
- ✅ Rotate passwords regularly
- ✅ Use service accounts for automation

### 2. Access Control

- Limit who can run the email workflow
- Use service accounts with minimal permissions
- Log all email sending activities
- Monitor for unusual activity

### 3. Data Protection

- Encrypt sensitive data in transit (TLS)
- Don't include sensitive data in email bodies
- Use secure attachment methods if needed
- Comply with data privacy regulations (GDPR, etc.)

## 📊 Production Deployment

### Step 1: Test Mode

Always test with `test_mode=True` first:

```python
smtp_config = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': 'your-email@gmail.com',
    'sender_password': 'your-app-password',
    'test_mode': True,  # All emails go to test_recipient
    'test_recipient': 'your-test-email@gmail.com'
}
```

### Step 2: Verify Test Emails

1. Check that emails are received
2. Verify formatting is correct
3. Confirm all data is accurate
4. Test with different email clients

### Step 3: Production Deployment

Once testing is complete:

```python
smtp_config = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': 'your-email@gmail.com',
    'sender_password': 'your-app-password',
    'test_mode': False,  # Send to actual recipients
    'test_recipient': None
}
```

### Step 4: Monitor

- Check logs for failed sends
- Monitor bounce rates
- Track delivery success
- Handle undeliverable addresses

## 🔄 Batch Processing

For large numbers of emails:

```python
# Add rate limiting
import time

def send_email_with_rate_limit(self, smtp_config, delay=1):
    """Send emails with rate limiting."""
    for notification in self.notifications:
        try:
            # Send email
            self.send_single_email(notification, smtp_config)
            
            # Wait before next email
            time.sleep(delay)
            
        except Exception as e:
            logger.error(f"Failed to send to {notification['email']}: {e}")
```

## 📋 Email Template Customization

### Modify Email Subject

In `certification_workflow.py`, line 463:

```python
msg['Subject'] = f"IBM Certification Status - Westpac Banking Corporation"
```

Change to:
```python
msg['Subject'] = f"Your Certification Status Update - {datetime.now().strftime('%B %Y')}"
```

### Modify Email Body

In `generate_notification_message()` method, customize the template:

```python
message = f"""
Dear {name},

[Your custom message here]

Your Current Certifications:
{'=' * 80}

[Certification details...]
"""
```

## 🐛 Common Issues

### Issue: "Authentication failed"
**Solution**: 
- Verify username/password are correct
- Use App Password for Gmail
- Check if SMTP AUTH is enabled

### Issue: "Connection refused"
**Solution**:
- Verify SMTP server address
- Check port number (587 for TLS, 465 for SSL)
- Check firewall settings

### Issue: "TLS error"
**Solution**:
- Use port 587 with STARTTLS
- Update Python SSL certificates
- Check server TLS support

### Issue: "Rate limit exceeded"
**Solution**:
- Add delays between emails
- Use batch processing
- Consider using email service (SendGrid, etc.)

## 📞 Support

For email configuration issues:
1. Check provider documentation
2. Review error messages in logs
3. Test with `test_email.py` script
4. Contact IT support for enterprise email
5. Contact IBM BOB for workflow issues

## 📚 Additional Resources

- [Gmail SMTP Settings](https://support.google.com/mail/answer/7126229)
- [Office 365 SMTP Settings](https://support.microsoft.com/en-us/office/pop-imap-and-smtp-settings-8361e398-8af4-4e97-b147-6c6c4ac95353)
- [Python smtplib Documentation](https://docs.python.org/3/library/smtplib.html)
- [Email Security Best Practices](https://www.ibm.com/security/email-security)

---

**Remember**: Always test email configuration in test mode before production deployment!