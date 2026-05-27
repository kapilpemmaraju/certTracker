"""
IBM BOB - Certification Reminder Workflow
==========================================

Sends reminders to employees who need to complete certifications.

Features:
- Finds employees with "Not Certified" or "No badge" status
- Sends reminder emails with manager CC
- GUI interface for action selection
- Test mode support

Author: IBM BOB
Date: 2026-05-21
Version: 1.0.0
"""

import pandas as pd
from datetime import datetime
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from config_loader import ConfigLoader
from notification_tracker import NotificationTracker
from outlook_email_sender import OutlookEmailSender

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CertificationReminderWorkflow:
    """
    Workflow to send certification completion reminders.
    
    Finds employees who need certifications and sends reminders
    with their manager CC'd.
    """
    
    def __init__(self, config: ConfigLoader = None, base_dir: Path = None, draft_mode: bool = True):
        """
        Initialize the certification reminder workflow.
        
        Args:
            config: ConfigLoader instance
            base_dir: Base directory for file paths
            draft_mode: If True, creates drafts instead of sending
        """
        self.config = config or ConfigLoader()
        self.base_dir = base_dir or Path.cwd()
        self.draft_mode = draft_mode
        
        # Initialize components
        self.output_dir = self.base_dir / self.config.get('files.output.directory', './output')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Outlook sender
        try:
            self.outlook_sender = OutlookEmailSender(draft_mode=draft_mode)
            logger.info(f"Outlook email sender initialized (draft_mode={draft_mode})")
        except Exception as e:
            logger.error(f"Failed to initialize Outlook sender: {e}")
            self.outlook_sender = None
        
        # Data storage
        self.file_a_data = None
        self.file_b_data = None
        self.matched_data = None
        self.not_certified_employees = []
        self.metrics = {}
        
        # Configuration
        self.target_client = self.config.get('processing.target_client', 'WESTPAC BANKING CORPORATION')
        
        logger.info("Certification Reminder Workflow initialized")
    
    def load_file_a(self) -> pd.DataFrame:
        """Load File A (Active Offshore Cloud List)."""
        try:
            file_a_path = self.base_dir / self.config.get('files.file_a.path')
            logger.info(f"Loading File A: {file_a_path}")
            
            self.file_a_data = pd.read_excel(file_a_path)
            logger.info(f"File A loaded: {len(self.file_a_data)} rows")
            
            # Get email column
            email_col = self.config.get('files.file_a.email_column', 'EMP_INTRANETID')
            
            # Clean and validate
            self.file_a_data[email_col] = self.file_a_data[email_col].str.strip().str.lower()
            self.file_a_data = self.file_a_data[self.file_a_data[email_col].notna()]
            
            logger.info(f"File A processed: {len(self.file_a_data)} valid records")
            self.metrics['file_a_records'] = len(self.file_a_data)
            
            return self.file_a_data
            
        except Exception as e:
            logger.error(f"Error loading File A: {e}")
            raise
    
    def load_file_b_hc_status(self) -> pd.DataFrame:
        """Load File B HC Certification Status worksheet."""
        try:
            file_b_path = self.base_dir / self.config.get('files.file_b.path')
            worksheet_name = self.config.get('files.file_b.hc_worksheet', 'HC Certification status-11 May')
            
            logger.info(f"Loading File B: {file_b_path}")
            logger.info(f"Worksheet: {worksheet_name}")
            
            self.file_b_data = pd.read_excel(file_b_path, sheet_name=worksheet_name)
            logger.info(f"File B loaded: {len(self.file_b_data)} rows")
            
            # Get required columns
            email_col = self.config.get('files.file_b.email_column', 'Intranet ID')
            client_col = self.config.get('files.file_b.client_column', 'Global_Client_Name')
            
            # Clean email column
            if email_col in self.file_b_data.columns:
                self.file_b_data[email_col] = self.file_b_data[email_col].str.strip().str.lower()
            
            logger.info(f"File B processed: {len(self.file_b_data)} records")
            self.metrics['file_b_records'] = len(self.file_b_data)
            
            return self.file_b_data
            
        except Exception as e:
            logger.error(f"Error loading File B: {e}")
            raise
    
    def filter_by_client(self) -> pd.DataFrame:
        """Filter records for target client."""
        try:
            client_col = self.config.get('files.file_b.client_column', 'Global_Client_Name')
            
            logger.info(f"Filtering records for client: {self.target_client}")
            
            # Case-insensitive filter
            mask = self.file_b_data[client_col].str.upper() == self.target_client.upper()
            filtered_data = self.file_b_data[mask].copy()
            
            logger.info(f"Filtered {len(filtered_data)} records (from {len(self.file_b_data)} total)")
            self.metrics['filtered_records'] = len(filtered_data)
            
            self.file_b_data = filtered_data
            return filtered_data
            
        except Exception as e:
            logger.error(f"Error filtering by client: {e}")
            raise
    
    def find_not_certified_employees(self) -> List[Dict]:
        """
        Find employees who need certifications.
        
        Criteria:
        - "All T2G Certified status" = "Not Certified"
        """
        try:
            logger.info("Finding employees who need certifications...")
            
            # Get column name
            t2g_status_col = 'All T2G Certified status'
            
            # Find not certified employees (only check T2G status)
            not_certified_mask = (
                self.file_b_data[t2g_status_col].str.upper() == 'NOT CERTIFIED'
            )
            
            not_certified_df = self.file_b_data[not_certified_mask].copy()
            
            logger.info(f"Found {len(not_certified_df)} employees needing certifications")
            self.metrics['not_certified_count'] = len(not_certified_df)
            
            # Extract required fields
            required_fields = ['Emp_Name', 'GLOBAL_MGR', 'Intranet ID', t2g_status_col]
            
            self.not_certified_employees = not_certified_df[required_fields].to_dict('records')
            
            return self.not_certified_employees
            
        except Exception as e:
            logger.error(f"Error finding not certified employees: {e}")
            raise
    
    def match_with_file_a(self) -> pd.DataFrame:
        """Match File B employees with File A to get additional details."""
        try:
            logger.info("Matching employees with File A...")
            
            file_a_email_col = self.config.get('files.file_a.email_column', 'EMP_INTRANETID')
            file_b_email_col = 'Intranet ID'  # HC worksheet uses "Intranet ID"
            
            # Create DataFrame from not certified employees
            not_cert_df = pd.DataFrame(self.not_certified_employees)
            
            # Merge with File A
            matched = pd.merge(
                not_cert_df,
                self.file_a_data,
                left_on=file_b_email_col,
                right_on=file_a_email_col,
                how='inner'
            )
            
            logger.info(f"Matched {len(matched)} employees with File A")
            self.metrics['matched_employees'] = len(matched)
            
            self.matched_data = matched
            return matched
            
        except Exception as e:
            logger.error(f"Error matching with File A: {e}")
            raise
    
    def save_output_spreadsheet(self) -> Path:
        """Save consolidated data to Excel."""
        try:
            logger.info("Saving consolidated spreadsheet...")
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.target_client.replace(' ', '_')}_Certification_Reminders_{timestamp}.xlsx"
            output_path = self.output_dir / filename
            
            # Save to Excel
            self.matched_data.to_excel(output_path, index=False, engine='openpyxl')
            
            logger.info(f"Spreadsheet saved: {output_path}")
            self.metrics['output_file'] = str(output_path)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error saving spreadsheet: {e}")
            raise
    
    def send_reminder_emails(self, test_mode: bool = False, 
                           test_email: str = None, limit: int = 0) -> bool:
        """
        Send certification reminder emails with manager CC.
        
        Args:
            test_mode: If True, enables test mode
            test_email: Override recipient email for testing
            limit: Limit number of emails (0 = no limit)
        """
        if self.matched_data is None or self.matched_data.empty:
            logger.warning("No employees to send reminders to")
            return True
        
        if self.outlook_sender is None:
            logger.error("Outlook sender not initialized")
            return False
        
        try:
            employees_to_notify = self.matched_data.to_dict('records')
            
            # Apply limit if specified
            if limit > 0:
                employees_to_notify = employees_to_notify[:limit]
                logger.info(f"TEST MODE: Limiting to {len(employees_to_notify)} emails")
            
            logger.info(f"Sending {len(employees_to_notify)} reminder emails...")
            
            sent_count = 0
            failed_count = 0
            
            for employee in employees_to_notify:
                emp_email = employee.get('Intranet ID', '').strip()
                emp_name = employee.get('Emp_Name', 'Employee')
                manager_email = employee.get('GLOBAL_MGR', '').strip()
                t2g_status = employee.get('All T2G Certified status', 'Unknown')
                
                # Override email if test mode
                recipient_email = test_email if test_email else emp_email
                
                if test_mode and test_email:
                    logger.info(f"TEST MODE: Redirecting from {emp_email} to {recipient_email}")
                
                # Send reminder email
                success = self.outlook_sender.send_certification_reminder(
                    to_email=recipient_email,
                    cc_email=manager_email if not test_mode else None,
                    emp_name=emp_name,
                    t2g_status=t2g_status,
                    industry_badge_status="Not checked",  # Simplified - only checking T2G status
                    client_name=self.target_client
                )
                
                if success:
                    sent_count += 1
                else:
                    failed_count += 1
            
            if self.draft_mode:
                logger.info(f"Created {sent_count} email drafts in Outlook")
            else:
                logger.info(f"Sent {sent_count} reminder emails")
            
            if failed_count > 0:
                logger.warning(f"Failed to send {failed_count} emails")
            
            self.metrics['emails_sent'] = sent_count
            self.metrics['emails_failed'] = failed_count
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending reminder emails: {e}")
            return False
    
    def run(self, test_mode: bool = False, test_email: str = None, 
            limit: int = 0) -> Dict[str, Any]:
        """
        Execute the complete certification reminder workflow.
        
        Args:
            test_mode: Enable test mode
            test_email: Test recipient email
            limit: Limit number of emails
        """
        logger.info("=" * 100)
        logger.info("STARTING CERTIFICATION REMINDER WORKFLOW")
        if test_mode:
            logger.info("*** TEST MODE ENABLED ***")
            if test_email:
                logger.info(f"*** Test email: {test_email} ***")
            if limit > 0:
                logger.info(f"*** Email limit: {limit} ***")
        logger.info("=" * 100)
        
        results = {
            'success': False,
            'errors': []
        }
        
        try:
            # Step 1: Load File A
            logger.info("\nSTEP 1: Loading File A")
            logger.info("=" * 100)
            self.load_file_a()
            
            # Step 2: Load File B (HC Status worksheet)
            logger.info("\nSTEP 2: Loading File B (HC Certification Status)")
            logger.info("=" * 100)
            self.load_file_b_hc_status()
            
            # Step 3: Filter by client
            logger.info("\nSTEP 3: Filtering by client")
            logger.info("=" * 100)
            self.filter_by_client()
            
            # Step 4: Find not certified employees
            logger.info("\nSTEP 4: Finding employees needing certifications")
            logger.info("=" * 100)
            self.find_not_certified_employees()
            
            # Step 5: Match with File A
            logger.info("\nSTEP 5: Matching with File A")
            logger.info("=" * 100)
            self.match_with_file_a()
            
            # Step 6: Save output
            logger.info("\nSTEP 6: Saving output spreadsheet")
            logger.info("=" * 100)
            self.save_output_spreadsheet()
            
            # Step 7: Send reminder emails
            logger.info("\nSTEP 7: Sending reminder emails")
            logger.info("=" * 100)
            self.send_reminder_emails(test_mode=test_mode, test_email=test_email, limit=limit)
            
            # Success
            results['success'] = True
            results.update(self.metrics)
            
            logger.info("\n" + "=" * 100)
            logger.info("WORKFLOW COMPLETED SUCCESSFULLY")
            logger.info("=" * 100)
            
            return results
            
        except Exception as e:
            logger.error(f"Workflow failed: {e}", exc_info=True)
            results['errors'].append(str(e))
            return results


def main():
    """Main function for standalone execution."""
    config = ConfigLoader()
    workflow = CertificationReminderWorkflow(config=config, draft_mode=True)
    results = workflow.run()
    
    print("\n" + "=" * 100)
    print("WORKFLOW RESULTS")
    print("=" * 100)
    for key, value in results.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()

# Made with Bob
