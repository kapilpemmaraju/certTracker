"""
Outlook Win32 Email Sender
===========================

This module sends emails using the installed Outlook application via Win32 COM.
No SMTP configuration needed - uses your existing Outlook installation.

Features:
- Uses installed Outlook application
- No SMTP server configuration required
- Sends from your default Outlook account
- Supports HTML and plain text emails
- Automatic signature inclusion
- Draft mode for review before sending

Author: IBM BOB
Date: 2026-05-21
"""

import win32com.client
import logging
from datetime import datetime
from typing import List, Optional
import pythoncom

logger = logging.getLogger(__name__)


class OutlookEmailSender:
    """Send emails using Outlook Win32 COM interface."""
    
    def __init__(self, draft_mode: bool = False):
        """
        Initialize Outlook email sender.
        
        Args:
            draft_mode: If True, creates drafts instead of sending immediately
        """
        self.draft_mode = draft_mode
        self.outlook = None
        self._initialize_outlook()
        
        logger.info(f"Outlook email sender initialized (draft_mode={draft_mode})")
    
    def _initialize_outlook(self):
        """Initialize Outlook COM object."""
        try:
            # Initialize COM
            pythoncom.CoInitialize()
            
            # Create Outlook application object
            self.outlook = win32com.client.Dispatch("Outlook.Application")
            
            logger.info("Outlook COM object created successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Outlook: {e}")
            logger.error("Make sure Microsoft Outlook is installed")
            raise
    
    def send_email(self, 
                   to: str,
                   subject: str,
                   body: str,
                   cc: Optional[str] = None,
                   bcc: Optional[str] = None,
                   html_body: bool = False) -> bool:
        """
        Send an email using Outlook.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text or HTML)
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)
            html_body: If True, body is treated as HTML
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create new mail item
            mail = self.outlook.CreateItem(0)  # 0 = olMailItem
            
            # Set recipients
            mail.To = to
            if cc:
                mail.CC = cc
            if bcc:
                mail.BCC = bcc
            
            # Set subject
            mail.Subject = subject
            
            # Set body
            if html_body:
                mail.HTMLBody = body
            else:
                mail.Body = body
            
            # Send or save as draft
            if self.draft_mode:
                mail.Save()
                logger.info(f"Email draft created for: {to}")
                logger.info(f"Subject: {subject}")
            else:
                mail.Send()
                logger.info(f"Email sent to: {to}")
                logger.info(f"Subject: {subject}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to}: {e}")
            return False
    
    def send_certification_notification(self,
                                       email: str,
                                       name: str,
                                       certifications: List[dict],
                                       client_name: str = "WESTPAC BANKING CORPORATION") -> bool:
        """
        Send certification notification email.
        
        Args:
            email: Recipient email address
            name: Recipient name
            certifications: List of certification dictionaries
            client_name: Client name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate subject
            subject = f" Certifications Status - {name}"
            
            # Generate HTML body
            html_body = self._generate_html_notification(name, certifications, client_name)
            
            # Send email
            return self.send_email(
                to=email,
                subject=subject,
                body=html_body,
                html_body=True
            )
            
        except Exception as e:
            logger.error(f"Failed to send certification notification to {email}: {e}")
            return False
    
    def _generate_html_notification(self, name: str, certifications: List[dict], client_name: str) -> str:
        """Generate HTML email body for certification notification."""
        
        # Start HTML
        html = f"""
<html>
<head>
    <style>
        body {{ font-family: Calibri, Arial, sans-serif; font-size: 11pt; }}
        .header {{ color: #0066cc; font-size: 14pt; font-weight: bold; margin-bottom: 20px; }}
        .cert-box {{ border: 1px solid #ddd; padding: 15px; margin: 10px 0; background-color: #f9f9f9; }}
        .cert-title {{ font-weight: bold; color: #333; font-size: 12pt; margin-bottom: 10px; }}
        .cert-detail {{ margin: 5px 0; }}
        .label {{ font-weight: bold; color: #666; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 10pt; }}
    </style>
</head>
<body>
    <p>Dear {name},</p>
    
    <p>This is an automated notification regarding your IBM certification status for the <strong>{client_name}</strong> project.</p>
    
    <div class="header">Your Current Certifications</div>
"""
        
        # Add each certification
        for idx, cert in enumerate(certifications, 1):
            vendor = cert.get('Vendor', 'Not Available')
            title = cert.get('Credential Title', 'Not Available')
            award_date = cert.get('Credential Award Date', 'Not Available')
            expiry_date = cert.get('Credential Expiry Date', 'Not Available')
            
            html += f"""
    <div class="cert-box">
        <div class="cert-title">Certification #{idx}: {title}</div>
        <div class="cert-detail"><span class="label">Vendor:</span> {vendor}</div>
        <div class="cert-detail"><span class="label">Award Date:</span> {award_date}</div>
        <div class="cert-detail"><span class="label">Expiry Date:</span> {expiry_date}</div>
    </div>
"""
        
        # Add footer
        html += f"""
    <p><strong>Total Certifications: {len(certifications)}</strong></p>
    
    <div class="footer">
        <p>This is an automated message. Please do not reply to this email.<br>
        For questions, contact your project manager.</p>
        
        <p>Best regards,<br>
        IBM  Management Team - Westpac Account <br>
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</body>
</html>
"""
        
        return html
    
    def send_batch_notifications(self, notifications: List[dict]) -> dict:
        """
        Send multiple certification notifications.
        
        Args:
            notifications: List of notification dictionaries with 'email', 'name', 'certifications'
            
        Returns:
            Dictionary with success/failure counts
        """
        results = {
            'total': len(notifications),
            'sent': 0,
            'failed': 0,
            'failed_emails': []
        }
        
        logger.info(f"Sending {len(notifications)} certification notifications...")
        
        for notification in notifications:
            email = notification.get('email')
            name = notification.get('name')
            certifications = notification.get('certifications', [])
            
            success = self.send_certification_notification(email, name, certifications)
            
            if success:
                results['sent'] += 1
            else:
                results['failed'] += 1
                results['failed_emails'].append(email)
        
        logger.info(f"Batch sending complete: {results['sent']} sent, {results['failed']} failed")
        
    def send_certification_reminder(self,
                                   to_email: str,
                                   cc_email: str,
                                   emp_name: str,
                                   t2g_status: str,
                                   industry_badge_status: str,
                                   client_name: str = "WESTPAC BANKING CORPORATION") -> bool:
        """
        Send certification completion reminder email with manager CC.
        
        Args:
            to_email: Employee email address
            cc_email: Manager email address (CC)
            emp_name: Employee name
            t2g_status: T2G certification status
            industry_badge_status: Industry badge status
            client_name: Client name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate subject
            subject = f"Action Required: Complete IBM Certifications - {client_name}"
            
            # Generate HTML body
            html_body = self._generate_reminder_html(
                emp_name, t2g_status, industry_badge_status, client_name
            )
            
            # Send email with CC
            return self.send_email(
                to=to_email,
                subject=subject,
                body=html_body,
                cc=cc_email,
                html_body=True
            )
            
        except Exception as e:
            logger.error(f"Failed to send reminder to {to_email}: {e}")
            return False
    
    def _generate_reminder_html(self, emp_name: str, t2g_status: str, 
                                industry_badge_status: str, client_name: str) -> str:
        """Generate HTML email body for certification reminder."""
        
        html = f"""
<html>
<head>
    <style>
        body {{ font-family: Calibri, Arial, sans-serif; font-size: 11pt; }}
        .header {{ color: #cc0000; font-size: 14pt; font-weight: bold; margin-bottom: 20px; }}
        .status-box {{ border: 2px solid #ff9999; padding: 15px; margin: 15px 0; background-color: #fff5f5; }}
        .status-item {{ margin: 10px 0; padding: 10px; background-color: white; border-left: 4px solid #cc0000; }}
        .label {{ font-weight: bold; color: #666; }}
        .value {{ color: #cc0000; font-weight: bold; }}
        .action-box {{ border: 2px solid #0066cc; padding: 15px; margin: 20px 0; background-color: #f0f8ff; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 10pt; }}
        ul {{ margin: 10px 0; padding-left: 20px; }}
        li {{ margin: 5px 0; }}
    </style>
</head>
<body>
    <p>Dear {emp_name},</p>
    
    <p>This is an important reminder regarding your IBM certification requirements for the <strong>{client_name}</strong> project.</p>
    
    <div class="header">⚠️ Action Required: Certification Status</div>
    
    <div class="status-box">
        <div class="status-item">
            <span class="label">T2G Certification Status:</span> 
            <span class="value">{t2g_status}</span>
        </div>
        <div class="status-item">
            <span class="label">Industry Badge Status:</span> 
            <span class="value">{industry_badge_status}</span>
        </div>
    </div>
    
    <div class="action-box">
        <p><strong>📋 Required Actions:</strong></p>
        <ul>
            <li>Complete all required T2G certifications</li>
            <li>Obtain the required Industry badge credentials</li>
            <li>Update your certification status in the system</li>
            <li>Contact your manager if you need guidance</li>
        </ul>
    </div>
    
    <p><strong>Why This Matters:</strong></p>
    <ul>
        <li>Client requirements mandate certified resources</li>
        <li>Your certifications ensure project compliance</li>
        <li>Timely completion helps maintain project staffing</li>
    </ul>
    
    <p><strong>Next Steps:</strong></p>
    <ol>
        <li>Review the required certifications for your role</li>
        <li>Access IBM's learning platform to begin training</li>
        <li>Schedule and complete certification exams</li>
        <li>Update your profile once certifications are obtained</li>
    </ol>
    
    <p>If you have any questions or need assistance, please reach out to your manager (CC'd on this email) or the project management team.</p>
    
    <div class="footer">
        <p><strong>This is an automated reminder. Please take action promptly.</strong></p>
        <p>For questions, contact your project manager or the IBM Certification Team.</p>
        
        <p>Best regards,<br>
        IBM Certification Management Team - Westpac Account<br>
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</body>
</html>
"""
        
        return html
    def send_industry_badge_reminder(self,
                                     to_email: str,
                                     cc_email: str,
                                     emp_name: str,
                                     badge_status: str,
                                     client_name: str = "WESTPAC BANKING CORPORATION") -> bool:
        """
        Send Industry Badge completion reminder email with manager CC.
        
        Args:
            to_email: Employee email address
            cc_email: Manager email address (CC)
            emp_name: Employee name
            badge_status: Industry badge status
            client_name: Client name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate subject
            subject = f"Action Required: Complete Industry Badge - {client_name}"
            
            # Generate HTML body
            html_body = self._generate_industry_badge_html(
                emp_name, badge_status, client_name
            )
            
            # Send email with CC
            return self.send_email(
                to=to_email,
                subject=subject,
                body=html_body,
                cc=cc_email,
                html_body=True
            )
            
        except Exception as e:
            logger.error(f"Failed to send Industry Badge reminder to {to_email}: {e}")
            return False
    
    def _generate_industry_badge_html(self, emp_name: str, badge_status: str, 
                                      client_name: str) -> str:
        """Generate HTML email body for Industry Badge reminder."""
        
        html = f"""
<html>
<head>
    <style>
        body {{ font-family: Calibri, Arial, sans-serif; font-size: 11pt; }}
        .header {{ color: #ff6600; font-size: 14pt; font-weight: bold; margin-bottom: 20px; }}
        .status-box {{ border: 2px solid #ffcc99; padding: 15px; margin: 15px 0; background-color: #fff9f5; }}
        .status-item {{ margin: 10px 0; padding: 10px; background-color: white; border-left: 4px solid #ff6600; }}
        .label {{ font-weight: bold; color: #666; }}
        .value {{ color: #ff6600; font-weight: bold; }}
        .action-box {{ border: 2px solid #0066cc; padding: 15px; margin: 20px 0; background-color: #f0f8ff; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 10pt; }}
        ul {{ margin: 10px 0; padding-left: 20px; }}
        li {{ margin: 5px 0; }}
        .highlight {{ background-color: #ffffcc; padding: 10px; border-left: 4px solid #ffcc00; margin: 15px 0; }}
    </style>
</head>
<body>
    <p>Dear {emp_name},</p>
    
    <p>This is an important reminder regarding your <strong>Industry Badge</strong> requirement for the <strong>{client_name}</strong> project.</p>
    
    <div class="header">🎯 Action Required: Industry Badge Completion</div>
    
    <div class="status-box">
        <div class="status-item">
            <span class="label">Current Industry Badge Status:</span> 
            <span class="value">{badge_status}</span>
        </div>
    </div>
    
    <div class="highlight">
        <strong>⚠️ Important:</strong> Your Industry Badge credential is currently marked as <strong>"{badge_status}"</strong>. 
        This credential is mandatory for all resources working on the {client_name} project.
    </div>
    
    <div class="action-box">
        <p><strong>📋 Required Actions:</strong></p>
        <ul>
            <li><strong>Obtain the Industry Badge credential</strong> specific to the Financial Services sector</li>
            <li>Complete all required training modules and assessments</li>
            <li>Pass the Industry Badge certification exam</li>
            <li>Update your certification profile in the IBM system</li>
            <li>Notify your manager once the badge is obtained</li>
        </ul>
    </div>
    
    <p><strong>Why Industry Badge Matters:</strong></p>
    <ul>
        <li><strong>Client Mandate:</strong> {client_name} requires all project resources to hold valid Industry Badge credentials</li>
        <li><strong>Domain Expertise:</strong> Demonstrates your knowledge of Financial Services industry practices</li>
        <li><strong>Project Compliance:</strong> Essential for maintaining project staffing and compliance requirements</li>
        <li><strong>Career Development:</strong> Enhances your professional credentials and industry expertise</li>
    </ul>
    
    <p><strong>Next Steps:</strong></p>
    <ol>
        <li>Access IBM's learning platform and locate the Industry Badge program</li>
        <li>Review the Financial Services Industry Badge requirements</li>
        <li>Complete all prerequisite training modules</li>
        <li>Schedule and pass the Industry Badge assessment</li>
        <li>Update your IBM profile with the new credential</li>
        <li>Inform your manager (CC'd on this email) upon completion</li>
    </ol>
    
    <div class="highlight">
        <strong>📅 Timeline:</strong> Please prioritize completing your Industry Badge as soon as possible to ensure continued project eligibility.
    </div>
    
    <p>If you have any questions about the Industry Badge requirements, training resources, or need assistance with the certification process, please reach out to your manager (CC'd on this email) or the IBM Certification Team.</p>
    
    <div class="footer">
        <p><strong>This is an automated reminder. Please take action promptly.</strong></p>
        <p>For questions about Industry Badge requirements, contact your project manager or the IBM Certification Team.</p>
        
        <p>Best regards,<br>
        IBM Certification Management Team - Westpac Account<br>
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</body>
</html>
"""
        
        return html
    
    
        return results
    
    def test_outlook_connection(self) -> bool:
        """Test Outlook connection."""
        try:
            # Try to access Outlook namespace
            namespace = self.outlook.GetNamespace("MAPI")
            
            # Get default account
            accounts = namespace.Accounts
            if accounts.Count > 0:
                default_account = accounts.Item(1)
                logger.info(f"Outlook connection successful")
                logger.info(f"Default account: {default_account.DisplayName}")
                return True
            else:
                logger.error("No Outlook accounts configured")
                return False
                
        except Exception as e:
            logger.error(f"Outlook connection test failed: {e}")
            return False
    
    def __del__(self):
        """Cleanup COM objects."""
        try:
            pythoncom.CoUninitialize()
        except:
            pass


def test_outlook_email():
    """Test Outlook email functionality."""
    print("=" * 80)
    print("OUTLOOK EMAIL SENDER TEST")
    print("=" * 80)
    
    try:
        # Initialize sender
        print("\n1. Initializing Outlook...")
        sender = OutlookEmailSender(draft_mode=True)  # Draft mode for testing
        print("✅ Outlook initialized")
        
        # Test connection
        print("\n2. Testing Outlook connection...")
        if sender.test_outlook_connection():
            print("✅ Outlook connection successful")
        else:
            print("❌ Outlook connection failed")
            return False
        
        # Send test email
        print("\n3. Creating test email draft...")
        
        # Get user's email for testing
        namespace = sender.outlook.GetNamespace("MAPI")
        default_account = namespace.Accounts.Item(1)
        test_email = default_account.SmtpAddress
        
        print(f"   Test recipient: {test_email}")
        
        # Sample certification data
        sample_certs = [
            {
                'Vendor': 'AWS',
                'Credential Title': 'AWS Certified Solutions Architect - Associate',
                'Credential Award Date': '2025-03-15',
                'Credential Expiry Date': '2028-03-15'
            },
            {
                'Vendor': 'IBM',
                'Credential Title': 'IBM Certified Advocate - Cloud v3',
                'Credential Award Date': '2025-06-20',
                'Credential Expiry Date': 'Not Available'
            }
        ]
        
        success = sender.send_certification_notification(
            email=test_email,
            name="Test User",
            certifications=sample_certs
        )
        
        if success:
            print("✅ Test email draft created successfully")
            print("\n📧 Check your Outlook Drafts folder to review the email")
            print("   If it looks good, you can send it manually or disable draft_mode")
        else:
            print("❌ Failed to create test email")
            return False
        
        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED!")
        print("=" * 80)
        print("\nNext steps:")
        print("1. Check your Outlook Drafts folder")
        print("2. Review the test email")
        print("3. If satisfied, set draft_mode=False in the workflow")
        print("4. Run the workflow to send actual notifications")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("\nCommon issues:")
        print("- Microsoft Outlook not installed")
        print("- Outlook not configured with an account")
        print("- pywin32 package not installed (pip install pywin32)")
        return False


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Run test
    test_outlook_email()

# Made with Bob
