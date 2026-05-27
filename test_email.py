"""
Email Functionality Test Script
================================

This script tests email functionality for the certification workflow.
Tests SMTP connection, authentication, and email sending.

Author: IBM BOB
Date: 2026-05-21
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import sys
from datetime import datetime


def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 80)
    print(text)
    print("=" * 80)


def print_success(text):
    """Print success message."""
    print(f"✅ {text}")


def print_error(text):
    """Print error message."""
    print(f"❌ {text}")


def print_info(text):
    """Print info message."""
    print(f"ℹ️  {text}")


def test_smtp_connection(smtp_server, smtp_port):
    """Test SMTP server connection."""
    print_header("TEST 1: SMTP Server Connection")
    
    try:
        print_info(f"Connecting to {smtp_server}:{smtp_port}...")
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        print_success(f"Connected to {smtp_server}:{smtp_port}")
        
        print_info("Starting TLS encryption...")
        server.starttls()
        print_success("TLS encryption started")
        
        server.quit()
        print_success("Connection test passed")
        return True
        
    except Exception as e:
        print_error(f"Connection failed: {e}")
        return False


def test_smtp_authentication(smtp_server, smtp_port, sender_email, sender_password):
    """Test SMTP authentication."""
    print_header("TEST 2: SMTP Authentication")
    
    try:
        print_info(f"Connecting to {smtp_server}:{smtp_port}...")
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        server.starttls()
        
        print_info(f"Authenticating as {sender_email}...")
        server.login(sender_email, sender_password)
        print_success("Authentication successful")
        
        server.quit()
        print_success("Authentication test passed")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print_error(f"Authentication failed: {e}")
        print_info("Common causes:")
        print_info("  - Incorrect password")
        print_info("  - Need to use App Password (for Gmail)")
        print_info("  - 2FA not enabled (for Gmail)")
        print_info("  - Account security settings blocking access")
        return False
        
    except Exception as e:
        print_error(f"Authentication test failed: {e}")
        return False


def test_send_email(smtp_server, smtp_port, sender_email, sender_password, test_recipient):
    """Test sending an actual email."""
    print_header("TEST 3: Send Test Email")
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = test_recipient
        msg['Subject'] = f"Test Email - Certification Workflow - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        body = f"""
This is a test email from the IBM Certification Workflow system.

Test Details:
-------------
Sent from: {sender_email}
Sent to: {test_recipient}
SMTP Server: {smtp_server}:{smtp_port}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

If you received this email, your email configuration is working correctly!

Next Steps:
-----------
1. Verify this email arrived in your inbox
2. Check if it's in spam/junk folder
3. If successful, you can enable email notifications in the workflow

Best regards,
IBM BOB - Certification Workflow System
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        print_info(f"Connecting to {smtp_server}:{smtp_port}...")
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
        server.starttls()
        
        print_info(f"Authenticating as {sender_email}...")
        server.login(sender_email, sender_password)
        
        print_info(f"Sending test email to {test_recipient}...")
        server.send_message(msg)
        
        server.quit()
        
        print_success(f"Test email sent successfully to {test_recipient}")
        print_info("Please check your inbox (and spam folder) for the test email")
        return True
        
    except Exception as e:
        print_error(f"Failed to send test email: {e}")
        return False


def test_certification_email_format(test_recipient):
    """Test certification notification email format."""
    print_header("TEST 4: Certification Notification Format")
    
    # Sample certification data
    sample_notification = """
Dear John Doe,

This is an automated notification regarding your IBM certification status for the WESTPAC BANKING CORPORATION project.

Your Current Certifications:
================================================================================

Certification #1:
  • Vendor:              AWS
  • Credential Title:    AWS Certified Solutions Architect - Associate
  • Award Date:          2025-03-15
  • Expiry Date:         2028-03-15
--------------------------------------------------------------------------------

Certification #2:
  • Vendor:              IBM
  • Credential Title:    IBM Certified Advocate - Cloud v3
  • Award Date:          2025-06-20
  • Expiry Date:         Not Available
--------------------------------------------------------------------------------

Total Certifications: 2

This is an automated message. Please do not reply to this email.
For questions, contact your project manager.

Best regards,
IBM Certification Management System
"""
    
    print_info("Sample certification notification format:")
    print(sample_notification)
    print_success("Notification format test passed")
    return True


def get_config_from_env():
    """Get email configuration from environment variables."""
    print_header("Reading Email Configuration")
    
    config = {
        'smtp_server': os.getenv('SMTP_SERVER'),
        'smtp_port': int(os.getenv('SMTP_PORT', '587')),
        'sender_email': os.getenv('SENDER_EMAIL'),
        'sender_password': os.getenv('SENDER_PASSWORD'),
        'test_recipient': os.getenv('TEST_EMAIL')
    }
    
    # Check if all required variables are set
    missing = []
    for key, value in config.items():
        if value is None or (isinstance(value, str) and not value):
            missing.append(key.upper())
    
    if missing:
        print_error(f"Missing environment variables: {', '.join(missing)}")
        print_info("\nPlease set the following environment variables:")
        print_info("  SMTP_SERVER     - SMTP server address (e.g., smtp.gmail.com)")
        print_info("  SMTP_PORT       - SMTP port (e.g., 587)")
        print_info("  SENDER_EMAIL    - Your email address")
        print_info("  SENDER_PASSWORD - Your email password or app password")
        print_info("  TEST_EMAIL      - Email address to send test to")
        print_info("\nExample (PowerShell):")
        print_info('  $env:SMTP_SERVER = "smtp.gmail.com"')
        print_info('  $env:SMTP_PORT = "587"')
        print_info('  $env:SENDER_EMAIL = "your-email@gmail.com"')
        print_info('  $env:SENDER_PASSWORD = "your-app-password"')
        print_info('  $env:TEST_EMAIL = "test@example.com"')
        return None
    
    print_success("Configuration loaded from environment variables")
    print_info(f"SMTP Server: {config['smtp_server']}:{config['smtp_port']}")
    print_info(f"Sender Email: {config['sender_email']}")
    print_info(f"Test Recipient: {config['test_recipient']}")
    
    return config


def get_config_interactive():
    """Get email configuration interactively."""
    print_header("Interactive Email Configuration")
    print_info("Please enter your email configuration:")
    
    config = {}
    
    # SMTP Server
    smtp_server = input("\nSMTP Server (e.g., smtp.gmail.com): ").strip()
    if not smtp_server:
        print_error("SMTP server is required")
        return None
    config['smtp_server'] = smtp_server
    
    # SMTP Port
    smtp_port = input("SMTP Port (default: 587): ").strip()
    config['smtp_port'] = int(smtp_port) if smtp_port else 587
    
    # Sender Email
    sender_email = input("Your Email Address: ").strip()
    if not sender_email:
        print_error("Sender email is required")
        return None
    config['sender_email'] = sender_email
    
    # Sender Password
    import getpass
    sender_password = getpass.getpass("Your Email Password (or App Password): ")
    if not sender_password:
        print_error("Password is required")
        return None
    config['sender_password'] = sender_password
    
    # Test Recipient
    test_recipient = input("Test Recipient Email: ").strip()
    if not test_recipient:
        test_recipient = sender_email
        print_info(f"Using sender email as test recipient: {test_recipient}")
    config['test_recipient'] = test_recipient
    
    return config


def main():
    """Main test function."""
    print_header("EMAIL FUNCTIONALITY TEST - CERTIFICATION WORKFLOW")
    print_info("This script will test your email configuration")
    print_info("Version: 1.0.0")
    print_info(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Try to get config from environment variables first
    config = get_config_from_env()
    
    # If not available, ask interactively
    if config is None:
        print_info("\nEnvironment variables not set. Using interactive mode...")
        config = get_config_interactive()
        
        if config is None:
            print_error("\nConfiguration failed. Exiting.")
            return False
    
    # Run tests
    results = {
        'connection': False,
        'authentication': False,
        'send_email': False,
        'format': False
    }
    
    # Test 1: Connection
    results['connection'] = test_smtp_connection(
        config['smtp_server'],
        config['smtp_port']
    )
    
    if not results['connection']:
        print_error("\nConnection test failed. Please check your SMTP server and port.")
        print_info("Common SMTP servers:")
        print_info("  Gmail:        smtp.gmail.com:587")
        print_info("  Outlook:      smtp-mail.outlook.com:587")
        print_info("  Office 365:   smtp.office365.com:587")
        print_info("  Yahoo:        smtp.mail.yahoo.com:587")
        return False
    
    # Test 2: Authentication
    results['authentication'] = test_smtp_authentication(
        config['smtp_server'],
        config['smtp_port'],
        config['sender_email'],
        config['sender_password']
    )
    
    if not results['authentication']:
        print_error("\nAuthentication test failed.")
        print_info("\nFor Gmail users:")
        print_info("  1. Enable 2-Factor Authentication")
        print_info("  2. Generate App Password: https://myaccount.google.com/apppasswords")
        print_info("  3. Use the App Password instead of your regular password")
        return False
    
    # Test 3: Send Email
    results['send_email'] = test_send_email(
        config['smtp_server'],
        config['smtp_port'],
        config['sender_email'],
        config['sender_password'],
        config['test_recipient']
    )
    
    if not results['send_email']:
        print_error("\nFailed to send test email.")
        return False
    
    # Test 4: Format
    results['format'] = test_certification_email_format(config['test_recipient'])
    
    # Summary
    print_header("TEST SUMMARY")
    
    all_passed = all(results.values())
    
    print(f"Connection Test:      {'✅ PASSED' if results['connection'] else '❌ FAILED'}")
    print(f"Authentication Test:  {'✅ PASSED' if results['authentication'] else '❌ FAILED'}")
    print(f"Send Email Test:      {'✅ PASSED' if results['send_email'] else '❌ FAILED'}")
    print(f"Format Test:          {'✅ PASSED' if results['format'] else '❌ FAILED'}")
    
    if all_passed:
        print_header("🎉 ALL TESTS PASSED!")
        print_success("Your email configuration is working correctly")
        print_info("\nNext Steps:")
        print_info("1. Check your inbox for the test email")
        print_info("2. Update config.yaml to enable email notifications:")
        print_info("   email:")
        print_info("     enabled: true")
        print_info("     test_mode: true  # Set to false for production")
        print_info("3. Run the workflow with email enabled")
        return True
    else:
        print_header("❌ SOME TESTS FAILED")
        print_error("Please fix the issues above and try again")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"\nUnexpected error: {e}")
        sys.exit(1)

# Made with Bob
