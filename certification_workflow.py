"""
IBM BOB - Autonomous Agentic Workflow for Certification Status Notifications
=============================================================================

This workflow processes two Excel files and automates certification-status notifications:
- File A: Active Offshore Cloud List (resource email addresses and project details)
- File B: T2G Certification Financial Services spreadsheet (certification data)

Author: IBM BOB
Date: 2026-05-21
"""

import pandas as pd
import numpy as np
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('certification_workflow.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class CertificationWorkflow:
    """Autonomous workflow for processing certification data and sending notifications."""
    
    def __init__(self, file_a_path, file_b_path, output_dir=None):
        """
        Initialize the workflow with file paths.
        
        Args:
            file_a_path: Path to Active Offshore Cloud List Excel file
            file_b_path: Path to T2G Certification Financial Services Excel file
            output_dir: Directory for output files (default: same as file_b_path)
        """
        self.file_a_path = Path(file_a_path)
        self.file_b_path = Path(file_b_path)
        self.output_dir = Path(output_dir) if output_dir else self.file_b_path.parent
        
        # Column names
        self.file_a_email_col = 'EMP_INTRANETID'  # IBM E-mail ID column in File A
        self.file_b_email_col = 'Internet Email'  # Internet Email column in File B
        self.client_name_col = 'Global_Client_Name'
        self.target_client = 'WESTPAC BANKING CORPORATION'
        
        # Data containers
        self.file_a_data = None
        self.file_b_data = None
        self.matched_data = None
        self.notifications = []
        
        logger.info("Workflow initialized")
        logger.info(f"File A: {self.file_a_path}")
        logger.info(f"File B: {self.file_b_path}")
        logger.info(f"Output directory: {self.output_dir}")
    
    def normalize_email(self, email):
        """
        Normalize email address for comparison (lowercase, strip whitespace).
        
        Args:
            email: Email address string
            
        Returns:
            Normalized email string or None if invalid
        """
        if pd.isna(email):
            return None
        return str(email).strip().lower()
    
    def parse_name_from_email(self, email):
        """
        Extract name from email address (substring before '@').
        
        Args:
            email: Email address string
            
        Returns:
            Name extracted from email or 'Not Available'
        """
        if pd.isna(email):
            return "Not Available"
        
        try:
            email_str = str(email).strip()
            if '@' in email_str:
                name_part = email_str.split('@')[0]
                # Replace dots and underscores with spaces and title case
                name = name_part.replace('.', ' ').replace('_', ' ').title()
                return name
            return "Not Available"
        except Exception as e:
            logger.warning(f"Error parsing name from email {email}: {e}")
            return "Not Available"
    
    def load_file_a(self):
        """Load and validate File A (Active Offshore Cloud List)."""
        logger.info("Loading File A: Active Offshore Cloud List")
        
        try:
            self.file_a_data = pd.read_excel(self.file_a_path)
            logger.info(f"File A loaded successfully: {len(self.file_a_data)} rows")
            
            # Validate required column exists
            if self.file_a_email_col not in self.file_a_data.columns:
                raise ValueError(f"Required column '{self.file_a_email_col}' not found in File A")
            
            # Normalize email addresses
            self.file_a_data['normalized_email'] = self.file_a_data[self.file_a_email_col].apply(
                self.normalize_email
            )
            
            # Remove rows with missing emails
            initial_count = len(self.file_a_data)
            self.file_a_data = self.file_a_data[self.file_a_data['normalized_email'].notna()]
            removed = initial_count - len(self.file_a_data)
            
            if removed > 0:
                logger.warning(f"Removed {removed} rows with missing email addresses from File A")
            
            logger.info(f"File A processed: {len(self.file_a_data)} valid email addresses")
            return True
            
        except Exception as e:
            logger.error(f"Error loading File A: {e}")
            raise
    
    def load_file_b(self):
        """Load and validate File B (T2G Certification Financial Services)."""
        logger.info("Loading File B: T2G Certification Financial Services")
        
        try:
            # Load the specific worksheet
            xl = pd.ExcelFile(self.file_b_path)
            
            # Find worksheet matching pattern "T2G Certification data*"
            worksheet_name = None
            pattern = 'T2G Certification data'
            
            for sheet_name in xl.sheet_names:
                if sheet_name.startswith(pattern):
                    worksheet_name = sheet_name
                    logger.info(f"Found worksheet matching pattern '{pattern}*': {worksheet_name}")
                    break
            
            if not worksheet_name:
                raise ValueError(
                    f"No worksheet found starting with '{pattern}' in File B. "
                    f"Available worksheets: {xl.sheet_names}"
                )
            
            self.file_b_data = pd.read_excel(xl, sheet_name=worksheet_name)
            logger.info(f"File B loaded successfully: {len(self.file_b_data)} rows from worksheet '{worksheet_name}'")
            
            # Validate required columns
            required_columns = [
                self.file_b_email_col,
                self.client_name_col,
                'Vendor',
                'Credential Title',
                'Credential Award Date',
                'Credential Expiry Date'
            ]
            
            missing_columns = [col for col in required_columns if col not in self.file_b_data.columns]
            if missing_columns:
                raise ValueError(f"Required columns not found in File B: {missing_columns}")
            
            # Normalize email addresses
            self.file_b_data['normalized_email'] = self.file_b_data[self.file_b_email_col].apply(
                self.normalize_email
            )
            
            logger.info(f"File B processed: {len(self.file_b_data)} total certification records")
            return True
            
        except Exception as e:
            logger.error(f"Error loading File B: {e}")
            raise
    
    def filter_westpac_records(self):
        """Filter File B records for Westpac Banking Corporation."""
        logger.info(f"Filtering records for client: {self.target_client}")
        
        try:
            initial_count = len(self.file_b_data)
            
            # Filter for Westpac (case-insensitive)
            self.file_b_data = self.file_b_data[
                self.file_b_data[self.client_name_col].str.upper() == self.target_client.upper()
            ]
            
            filtered_count = len(self.file_b_data)
            logger.info(f"Filtered {filtered_count} records for {self.target_client} (from {initial_count} total)")
            
            if filtered_count == 0:
                logger.warning(f"No records found for {self.target_client}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error filtering Westpac records: {e}")
            raise
    
    def match_emails(self):
        """Match email addresses between File A and File B."""
        logger.info("Matching email addresses between File A and File B")
        
        try:
            # Perform inner join on normalized email addresses
            self.matched_data = pd.merge(
                self.file_a_data,
                self.file_b_data,
                on='normalized_email',
                how='inner',
                suffixes=('_fileA', '_fileB')
            )
            
            matched_count = len(self.matched_data)
            unique_emails = self.matched_data['normalized_email'].nunique()
            
            logger.info(f"Matched {matched_count} certification records for {unique_emails} unique email addresses")
            
            if matched_count == 0:
                logger.warning("No matching email addresses found between File A and File B")
            
            return True
            
        except Exception as e:
            logger.error(f"Error matching emails: {e}")
            raise
    
    def extract_and_consolidate_data(self):
        """Extract required fields and create consolidated output."""
        logger.info("Extracting and consolidating certification data")
        
        try:
            if self.matched_data is None or len(self.matched_data) == 0:
                logger.warning("No matched data to consolidate")
                return True
            
            # Extract required fields
            consolidated = pd.DataFrame()
            
            # Internet Email (from File B)
            consolidated['Internet Email'] = self.matched_data[self.file_b_email_col]
            
            # Name (parsed from email)
            consolidated['Name'] = self.matched_data[self.file_b_email_col].apply(
                self.parse_name_from_email
            )
            
            # Vendor
            consolidated['Vendor'] = self.matched_data['Vendor'].fillna('Not Available')
            
            # Credential Title
            consolidated['Credential Title'] = self.matched_data['Credential Title'].fillna('Not Available')
            
            # Credential Award Date
            consolidated['Credential Award Date'] = self.matched_data['Credential Award Date'].apply(
                lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) and isinstance(x, (pd.Timestamp, datetime)) else 'Not Available'
            )
            
            # Credential Expiry Date
            consolidated['Credential Expiry Date'] = self.matched_data['Credential Expiry Date'].apply(
                lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) and isinstance(x, (pd.Timestamp, datetime)) else 'Not Available'
            )
            
            # Add additional useful fields from File A
            if 'EMP_NAME' in self.matched_data.columns:
                consolidated['Employee Name'] = self.matched_data['EMP_NAME'].fillna('Not Available')
            
            if 'EMP ID' in self.matched_data.columns:
                consolidated['Employee ID'] = self.matched_data['EMP ID'].fillna('Not Available')
            
            self.matched_data = consolidated
            
            logger.info(f"Consolidated data created: {len(consolidated)} records")
            logger.info(f"Unique employees: {consolidated['Internet Email'].nunique()}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error consolidating data: {e}")
            raise
    
    def save_output_spreadsheet(self):
        """Save consolidated data to Excel file."""
        logger.info("Saving consolidated output spreadsheet")
        
        try:
            if self.matched_data is None or len(self.matched_data) == 0:
                logger.warning("No data to save")
                return True
            
            # Generate output filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = self.output_dir / f'Westpac_Certification_Consolidated_{timestamp}.xlsx'
            
            # Save to Excel
            self.matched_data.to_excel(output_file, index=False, sheet_name='Consolidated Data')
            
            logger.info(f"Output spreadsheet saved: {output_file}")
            logger.info(f"Total records: {len(self.matched_data)}")
            
            return output_file
            
        except Exception as e:
            logger.error(f"Error saving output spreadsheet: {e}")
            raise
    
    def generate_notification_message(self, email, certifications):
        """
        Generate notification message for a single email address.
        
        Args:
            email: Email address
            certifications: DataFrame of certifications for this email
            
        Returns:
            Formatted notification message
        """
        try:
            # Get name from first record
            name = certifications.iloc[0]['Name']
            
            # Build message
            message = f"""
Dear {name},

This is an automated notification regarding your IBM certification status for the Westpac Banking Corporation project.

Your Current Certifications:
{'=' * 80}

"""
            
            # Add each certification
            for idx, cert in certifications.iterrows():
                message += f"""
Certification #{idx + 1}:
  • Vendor:              {cert['Vendor']}
  • Credential Title:    {cert['Credential Title']}
  • Award Date:          {cert['Credential Award Date']}
  • Expiry Date:         {cert['Credential Expiry Date']}
{'-' * 80}
"""
            
            message += f"""

Total Certifications: {len(certifications)}

This is an automated message. Please do not reply to this email.
For questions, contact your project manager.

Best regards,
IBM Certification Management System
"""
            
            return message
            
        except Exception as e:
            logger.error(f"Error generating notification for {email}: {e}")
            return None
    
    def generate_all_notifications(self):
        """Generate notification messages for all matched emails."""
        logger.info("Generating notification messages")
        
        try:
            if self.matched_data is None or len(self.matched_data) == 0:
                logger.warning("No data to generate notifications")
                return True
            
            # Group by email address
            grouped = self.matched_data.groupby('Internet Email')
            
            self.notifications = []
            
            for email, group in grouped:
                message = self.generate_notification_message(email, group)
                if message:
                    self.notifications.append({
                        'email': email,
                        'name': group.iloc[0]['Name'],
                        'cert_count': len(group),
                        'message': message
                    })
            
            logger.info(f"Generated {len(self.notifications)} notification messages")
            
            return True
            
        except Exception as e:
            logger.error(f"Error generating notifications: {e}")
            raise
    
    def save_notifications_to_file(self):
        """Save all notification messages to a text file."""
        logger.info("Saving notification messages to file")
        
        try:
            if not self.notifications:
                logger.warning("No notifications to save")
                return True
            
            # Generate output filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = self.output_dir / f'Westpac_Certification_Notifications_{timestamp}.txt'
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("=" * 100 + "\n")
                f.write("IBM CERTIFICATION NOTIFICATIONS - WESTPAC BANKING CORPORATION\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 100 + "\n\n")
                
                for idx, notification in enumerate(self.notifications, 1):
                    f.write(f"\n{'=' * 100}\n")
                    f.write(f"NOTIFICATION {idx} of {len(self.notifications)}\n")
                    f.write(f"{'=' * 100}\n")
                    f.write(f"To: {notification['email']}\n")
                    f.write(f"Name: {notification['name']}\n")
                    f.write(f"Certifications: {notification['cert_count']}\n")
                    f.write(f"{'-' * 100}\n")
                    f.write(notification['message'])
                    f.write("\n\n")
            
            logger.info(f"Notifications saved to: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error saving notifications: {e}")
            raise
    
    def send_email_notifications(self, smtp_server, smtp_port, sender_email, sender_password, 
                                 test_mode=True, test_recipient=None):
        """
        Send email notifications (optional - requires SMTP configuration).
        
        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP port
            sender_email: Sender email address
            sender_password: Sender password/app password
            test_mode: If True, send all emails to test_recipient instead
            test_recipient: Email address for test mode
        """
        logger.info("Sending email notifications")
        
        if test_mode and not test_recipient:
            logger.error("Test mode enabled but no test_recipient provided")
            return False
        
        try:
            sent_count = 0
            failed_count = 0
            
            for notification in self.notifications:
                try:
                    # Create message
                    msg = MIMEMultipart()
                    msg['From'] = sender_email
                    msg['To'] = test_recipient if test_mode else notification['email']
                    msg['Subject'] = f"IBM Certification Status - Westpac Banking Corporation"
                    
                    # Add body
                    body = notification['message']
                    if test_mode:
                        body = f"[TEST MODE - Original recipient: {notification['email']}]\n\n" + body
                    
                    msg.attach(MIMEText(body, 'plain'))
                    
                    # Send email
                    with smtplib.SMTP(smtp_server, smtp_port) as server:
                        server.starttls()
                        server.login(sender_email, sender_password)
                        server.send_message(msg)
                    
                    sent_count += 1
                    logger.info(f"Email sent to: {notification['email']}")
                    
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Failed to send email to {notification['email']}: {e}")
            
            logger.info(f"Email sending complete: {sent_count} sent, {failed_count} failed")
            return True
            
        except Exception as e:
            logger.error(f"Error in email sending process: {e}")
            return False
    
    def run(self, send_emails=False, smtp_config=None):
        """
        Execute the complete workflow.
        
        Args:
            send_emails: Whether to send email notifications
            smtp_config: Dictionary with SMTP configuration (if send_emails=True)
        
        Returns:
            Dictionary with workflow results
        """
        logger.info("=" * 100)
        logger.info("STARTING CERTIFICATION WORKFLOW")
        logger.info("=" * 100)
        
        results = {
            'success': False,
            'file_a_records': 0,
            'file_b_records': 0,
            'westpac_records': 0,
            'matched_records': 0,
            'unique_emails': 0,
            'notifications_generated': 0,
            'output_spreadsheet': None,
            'notifications_file': None,
            'emails_sent': 0,
            'errors': []
        }
        
        try:
            # Step 1: Load File A
            logger.info("\n" + "=" * 100)
            logger.info("STEP 1: Loading File A (Active Offshore Cloud List)")
            logger.info("=" * 100)
            self.load_file_a()
            results['file_a_records'] = len(self.file_a_data)
            
            # Step 2: Load File B
            logger.info("\n" + "=" * 100)
            logger.info("STEP 2: Loading File B (T2G Certification Financial Services)")
            logger.info("=" * 100)
            self.load_file_b()
            results['file_b_records'] = len(self.file_b_data)
            
            # Step 3: Filter Westpac records
            logger.info("\n" + "=" * 100)
            logger.info("STEP 3: Filtering Westpac Banking Corporation records")
            logger.info("=" * 100)
            self.filter_westpac_records()
            results['westpac_records'] = len(self.file_b_data)
            
            # Step 4: Match emails
            logger.info("\n" + "=" * 100)
            logger.info("STEP 4: Matching email addresses")
            logger.info("=" * 100)
            self.match_emails()
            results['matched_records'] = len(self.matched_data) if self.matched_data is not None else 0
            
            # Step 5: Extract and consolidate
            logger.info("\n" + "=" * 100)
            logger.info("STEP 5: Extracting and consolidating data")
            logger.info("=" * 100)
            self.extract_and_consolidate_data()
            if self.matched_data is not None:
                results['unique_emails'] = self.matched_data['Internet Email'].nunique()
            
            # Step 6: Save output spreadsheet
            logger.info("\n" + "=" * 100)
            logger.info("STEP 6: Saving consolidated spreadsheet")
            logger.info("=" * 100)
            output_file = self.save_output_spreadsheet()
            results['output_spreadsheet'] = str(output_file) if output_file else None
            
            # Step 7: Generate notifications
            logger.info("\n" + "=" * 100)
            logger.info("STEP 7: Generating notification messages")
            logger.info("=" * 100)
            self.generate_all_notifications()
            results['notifications_generated'] = len(self.notifications)
            
            # Step 8: Save notifications to file
            logger.info("\n" + "=" * 100)
            logger.info("STEP 8: Saving notification messages to file")
            logger.info("=" * 100)
            notifications_file = self.save_notifications_to_file()
            results['notifications_file'] = str(notifications_file) if notifications_file else None
            
            # Step 9: Send emails (optional)
            if send_emails and smtp_config:
                logger.info("\n" + "=" * 100)
                logger.info("STEP 9: Sending email notifications")
                logger.info("=" * 100)
                self.send_email_notifications(**smtp_config)
                results['emails_sent'] = len(self.notifications)
            
            results['success'] = True
            
            logger.info("\n" + "=" * 100)
            logger.info("WORKFLOW COMPLETED SUCCESSFULLY")
            logger.info("=" * 100)
            logger.info(f"File A records: {results['file_a_records']}")
            logger.info(f"File B total records: {results['file_b_records']}")
            logger.info(f"Westpac records: {results['westpac_records']}")
            logger.info(f"Matched records: {results['matched_records']}")
            logger.info(f"Unique emails: {results['unique_emails']}")
            logger.info(f"Notifications generated: {results['notifications_generated']}")
            logger.info(f"Output spreadsheet: {results['output_spreadsheet']}")
            logger.info(f"Notifications file: {results['notifications_file']}")
            
            return results
            
        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            results['errors'].append(str(e))
            return results


def main():
    """Main entry point for the workflow."""
    import glob
    
    # File paths with pattern matching
    base_dir = Path(r"C:/Users/KAPILPEMMARAJU/Downloads/CertificationsWestpac")
    
    # Find File A (any file starting with "Active Offshore")
    file_a_pattern = str(base_dir / "Active Offshore*.xlsx")
    file_a_matches = glob.glob(file_a_pattern)
    if not file_a_matches:
        raise FileNotFoundError(f"No files found matching pattern: {file_a_pattern}")
    file_a = Path(sorted(file_a_matches, reverse=True)[0])  # Get most recent
    logger.info(f"Found File A: {file_a.name}")
    
    # Find File B (any file starting with "T2G Certification")
    file_b_pattern = str(base_dir / "T2G Certification*.xlsx")
    file_b_matches = glob.glob(file_b_pattern)
    if not file_b_matches:
        raise FileNotFoundError(f"No files found matching pattern: {file_b_pattern}")
    file_b = Path(sorted(file_b_matches, reverse=True)[0])  # Get most recent
    logger.info(f"Found File B: {file_b.name}")
    
    # Create workflow instance
    workflow = CertificationWorkflow(
        file_a_path=file_a,
        file_b_path=file_b,
        output_dir=base_dir
    )
    
    # Run workflow (without email sending for now)
    results = workflow.run(send_emails=False)
    
    # Print summary
    print("\n" + "=" * 100)
    print("WORKFLOW EXECUTION SUMMARY")
    print("=" * 100)
    print(f"Status: {'SUCCESS' if results['success'] else 'FAILED'}")
    print(f"File A records: {results['file_a_records']}")
    print(f"File B total records: {results['file_b_records']}")
    print(f"Westpac records: {results['westpac_records']}")
    print(f"Matched records: {results['matched_records']}")
    print(f"Unique emails: {results['unique_emails']}")
    print(f"Notifications generated: {results['notifications_generated']}")
    print(f"\nOutput files:")
    print(f"  Spreadsheet: {results['output_spreadsheet']}")
    print(f"  Notifications: {results['notifications_file']}")
    
    if results['errors']:
        print(f"\nErrors encountered:")
        for error in results['errors']:
            print(f"  - {error}")
    
    print("=" * 100)
    
    return results


if __name__ == "__main__":
    main()

# Made with Bob
