"""
IBM BOB - Industry Badge Reminder Workflow
==========================================

This workflow identifies employees who need to complete their Industry Badge
and sends reminder emails with manager CC.

Features:
- Loads HC Certification Status worksheet
- Filters for Westpac Banking Corporation
- Finds employees with "No Badge" in Industry Badge column
- Matches with Active Offshore list
- Sends reminder emails with manager CC
- Test mode support
- Draft mode support

Author: IBM BOB
Date: 2026-05-22
Version: 1.0.0
"""

import pandas as pd
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
from config_loader import ConfigLoader
from notification_tracker import NotificationTracker
from outlook_email_sender import OutlookEmailSender

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('industry_badge_workflow.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class IndustryBadgeWorkflow:
    """Workflow for sending Industry Badge completion reminders."""
    
    def __init__(self, config: ConfigLoader = None, base_dir: Path = None, draft_mode: bool = True):
        """
        Initialize Industry Badge workflow.
        
        Args:
            config: Configuration loader instance
            base_dir: Base directory for file operations
            draft_mode: If True, creates email drafts instead of sending
        """
        self.config = config or ConfigLoader()
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.draft_mode = draft_mode
        
        # Initialize email sender
        self.email_sender = OutlookEmailSender(draft_mode=draft_mode)
        
        # Initialize notification tracker
        self.tracker = NotificationTracker()
        
        # Data storage
        self.file_a_data = None
        self.file_b_data = None
        self.matched_data = None
        
        # Target client
        self.target_client = self.config.get('workflow.target_client', 'WESTPAC BANKING CORPORATION')
        
        logger.info("Industry Badge Workflow initialized")
    
    def load_file_a(self) -> pd.DataFrame:
        """Load and process File A (Active Offshore list)."""
        try:
            file_a_path = self.base_dir / self.config.get('files.file_a.path')
            
            logger.info(f"Loading File A: {file_a_path}")
            
            # Read Excel file
            df = pd.read_excel(file_a_path, engine='openpyxl')
            
            logger.info(f"File A loaded: {len(df)} rows")
            
            # Get email column name
            email_col = self.config.get('files.file_a.email_column')
            
            # Validate required columns
            if email_col not in df.columns:
                raise ValueError(f"Column '{email_col}' not found in File A")
            
            # Clean and standardize email addresses
            df[email_col] = df[email_col].astype(str).str.strip().str.lower()
            
            # Remove invalid emails
            df = df[df[email_col].str.contains('@', na=False)]
            
            self.file_a_data = df
            
            logger.info(f"File A processed: {len(df)} valid records")
            
            return self.file_a_data
            
        except Exception as e:
            logger.error(f"Failed to load File A: {e}")
            raise
    
    def load_file_b(self) -> pd.DataFrame:
        """Load and process File B (HC Certification Status)."""
        try:
            file_b_path = self.base_dir / self.config.get('files.file_b.path')
            hc_worksheet = self.config.get('files.file_b.hc_worksheet')
            
            logger.info(f"Loading File B: {file_b_path}")
            logger.info(f"Worksheet: {hc_worksheet}")
            
            # Read Excel file - HC worksheet
            df = pd.read_excel(file_b_path, sheet_name=hc_worksheet, engine='openpyxl')
            
            logger.info(f"File B loaded: {len(df)} rows")
            
            self.file_b_data = df
            
            logger.info(f"File B processed: {len(df)} records")
            
            return self.file_b_data
            
        except Exception as e:
            logger.error(f"Failed to load File B: {e}")
            raise
    
    def filter_by_client(self) -> pd.DataFrame:
        """Filter File B data by target client."""
        try:
            if self.file_b_data is None:
                raise ValueError("File B not loaded")
            
            client_col = self.config.get('files.file_b.client_column')
            
            logger.info(f"Filtering records for client: {self.target_client}")
            
            # Filter by client (case-insensitive)
            mask = self.file_b_data[client_col].str.upper() == self.target_client.upper()
            filtered_data = self.file_b_data[mask].copy()
            
            logger.info(f"Filtered {len(filtered_data)} records (from {len(self.file_b_data)} total)")
            
            self.file_b_data = filtered_data
            
            return filtered_data
            
        except Exception as e:
            logger.error(f"Failed to filter by client: {e}")
            raise
    
    def find_no_badge_employees(self) -> pd.DataFrame:
        """Find employees who need Industry Badge (have 'No Badge')."""
        try:
            if self.file_b_data is None:
                raise ValueError("File B not loaded or filtered")
            
            logger.info("Finding employees who need Industry Badge...")
            
            # Column name for Industry Badge status
            badge_col = "Industry Badge Met Ind Cred Lvl?"
            
            # Find employees with "No Badge"
            no_badge_mask = (
                self.file_b_data[badge_col].str.upper() == 'NO BADGE'
            )
            
            no_badge_df = self.file_b_data[no_badge_mask].copy()
            
            logger.info(f"Found {len(no_badge_df)} employees needing Industry Badge")
            
            self.file_b_data = no_badge_df
            
            return no_badge_df
            
        except Exception as e:
            logger.error(f"Failed to find employees needing Industry Badge: {e}")
            raise
    
    def match_with_file_a(self) -> pd.DataFrame:
        """Match employees with File A to get valid email addresses."""
        try:
            if self.file_a_data is None or self.file_b_data is None:
                raise ValueError("Both files must be loaded first")
            
            logger.info("Matching employees with File A...")
            
            # Get column names
            file_a_email_col = self.config.get('files.file_a.email_column')
            file_b_email_col = 'Intranet ID'  # HC worksheet uses "Intranet ID"
            
            # Standardize email columns for matching
            self.file_b_data['email_lower'] = (
                self.file_b_data[file_b_email_col]
                .astype(str)
                .str.strip()
                .str.lower()
            )
            
            self.file_a_data['email_lower'] = (
                self.file_a_data[file_a_email_col]
                .astype(str)
                .str.strip()
                .str.lower()
            )
            
            # Merge on email
            matched = pd.merge(
                self.file_b_data,
                self.file_a_data,
                left_on='email_lower',
                right_on='email_lower',
                how='inner',
                suffixes=('_b', '_a')
            )
            
            logger.info(f"Matched {len(matched)} employees with File A")
            
            self.matched_data = matched
            
            return matched
            
        except Exception as e:
            logger.error(f"Failed to match with File A: {e}")
            raise
    
    def save_output_spreadsheet(self) -> Path:
        """Save matched data to output spreadsheet."""
        try:
            if self.matched_data is None or self.matched_data.empty:
                logger.warning("No matched data to save")
                return None
            
            logger.info("Saving consolidated spreadsheet...")
            
            # Create output directory
            output_dir = self.base_dir / 'output'
            output_dir.mkdir(exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            client_name = self.target_client.replace(' ', '_')
            filename = f"{client_name}_Industry_Badge_Reminders_{timestamp}.xlsx"
            output_path = output_dir / filename
            
            # Save to Excel
            self.matched_data.to_excel(output_path, index=False, engine='openpyxl')
            
            logger.info(f"Spreadsheet saved: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to save spreadsheet: {e}")
            raise
    
    def send_reminder_emails(self, test_mode: bool = False, 
                           test_email: str = None, limit: int = 0) -> bool:
        """
        Send Industry Badge reminder emails.
        
        Args:
            test_mode: If True, redirects all emails to test_email
            test_email: Email address for test mode
            limit: Maximum number of emails to send (0 = no limit)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.matched_data is None or self.matched_data.empty:
                logger.warning("No matched data to send emails")
                return False
            
            logger.info("Sending Industry Badge reminder emails...")
            
            if test_mode:
                logger.info(f"*** TEST MODE: All emails will be sent to {test_email} ***")
            
            if limit > 0:
                logger.info(f"*** EMAIL LIMIT: Sending only {limit} emails ***")
            
            sent_count = 0
            failed_count = 0
            
            # Process each employee
            for idx, row in self.matched_data.iterrows():
                # Check limit
                if limit > 0 and sent_count >= limit:
                    logger.info(f"Reached email limit of {limit}")
                    break
                
                try:
                    # Get employee details
                    emp_email = row.get('Intranet ID', '').strip()
                    emp_name = row.get('Emp_Name', 'Employee').strip()
                    manager_email = row.get('GLOBAL_MGR', '').strip()
                    badge_status = row.get('Industry Badge Met Ind Cred Lvl?', 'No Badge').strip()
                    
                    # Use test email if in test mode
                    to_email = test_email if test_mode else emp_email
                    cc_email = test_email if test_mode else manager_email
                    
                    # Send email
                    success = self.email_sender.send_industry_badge_reminder(
                        to_email=to_email,
                        cc_email=cc_email,
                        emp_name=emp_name,
                        badge_status=badge_status,
                        client_name=self.target_client
                    )
                    
                    if success:
                        sent_count += 1
                        logger.info(f"✓ Reminder sent to: {emp_name} ({emp_email})")
                    else:
                        failed_count += 1
                        logger.error(f"✗ Failed to send to: {emp_name} ({emp_email})")
                    
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Error sending to {emp_name}: {e}")
            
            logger.info(f"Email sending complete: {sent_count} sent, {failed_count} failed")
            
            return failed_count == 0
            
        except Exception as e:
            logger.error(f"Failed to send emails: {e}")
            return False
    
    def run(self, test_mode: bool = False, test_email: str = None, 
            limit: int = 0) -> dict:
        """
        Run the complete Industry Badge workflow.
        
        Args:
            test_mode: If True, redirects emails to test_email
            test_email: Email address for test mode
            limit: Maximum number of emails to send
            
        Returns:
            Dictionary with workflow results
        """
        try:
            logger.info("=" * 100)
            logger.info("STARTING INDUSTRY BADGE REMINDER WORKFLOW")
            if test_mode:
                logger.info("*** TEST MODE ENABLED ***")
                logger.info(f"*** Test email: {test_email} ***")
                logger.info(f"*** Email limit: {limit} ***")
            logger.info("=" * 100)
            
            # Step 1: Load File A
            logger.info("\nSTEP 1: Loading File A")
            logger.info("=" * 100)
            self.load_file_a()
            
            # Step 2: Load File B (HC Certification Status)
            logger.info("\nSTEP 2: Loading File B (HC Certification Status)")
            logger.info("=" * 100)
            self.load_file_b()
            
            # Step 3: Filter by client
            logger.info("\nSTEP 3: Filtering by client")
            logger.info("=" * 100)
            self.filter_by_client()
            
            # Step 4: Find employees needing Industry Badge
            logger.info("\nSTEP 4: Finding employees needing Industry Badge")
            logger.info("=" * 100)
            self.find_no_badge_employees()
            
            # Step 5: Match with File A
            logger.info("\nSTEP 5: Matching with File A")
            logger.info("=" * 100)
            self.match_with_file_a()
            
            # Step 6: Save output spreadsheet
            logger.info("\nSTEP 6: Saving output spreadsheet")
            logger.info("=" * 100)
            output_path = self.save_output_spreadsheet()
            
            # Step 7: Send reminder emails
            logger.info("\nSTEP 7: Sending reminder emails")
            logger.info("=" * 100)
            email_success = self.send_reminder_emails(
                test_mode=test_mode,
                test_email=test_email,
                limit=limit
            )
            
            # Prepare results
            results = {
                'success': email_success,
                'employees_found': len(self.matched_data) if self.matched_data is not None else 0,
                'output_file': str(output_path) if output_path else None,
                'draft_mode': self.draft_mode
            }
            
            logger.info("\n" + "=" * 100)
            logger.info("WORKFLOW COMPLETED")
            logger.info("=" * 100)
            
            return results
            
        except Exception as e:
            logger.error(f"Workflow failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }


def main():
    """Main function for testing."""
    workflow = IndustryBadgeWorkflow(draft_mode=True)
    results = workflow.run(test_mode=True, test_email="test@example.com", limit=3)
    print(f"\nResults: {results}")


if __name__ == "__main__":
    main()

# Made with Bob