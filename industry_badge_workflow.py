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
from typing import Optional, Dict, Any
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
    
    def find_column_case_insensitive(self, df: pd.DataFrame, column_name: str,
                                    fuzzy: bool = True) -> Optional[str]:
        """
        Find a column in DataFrame using case-insensitive and fuzzy matching.
        
        Args:
            df: DataFrame to search
            column_name: Column name to find (case-insensitive)
            fuzzy: If True, also tries partial/fuzzy matching
            
        Returns:
            Actual column name if found, None otherwise
        """
        search_lower = column_name.lower()
        
        # Try exact match first (case-insensitive)
        for col in df.columns:
            if isinstance(col, str) and col.lower() == search_lower:
                logger.debug(f"Found exact match: '{col}' for search '{column_name}'")
                return col
        
        # Try fuzzy matching if enabled
        if fuzzy:
            # Remove common separators for comparison
            search_normalized = search_lower.replace('_', '').replace(' ', '').replace('-', '')
            
            for col in df.columns:
                if isinstance(col, str):
                    col_normalized = col.lower().replace('_', '').replace(' ', '').replace('-', '')
                    
                    # Check if search term is contained in column name
                    if search_normalized in col_normalized:
                        logger.info(f"Found fuzzy match: '{col}' for search '{column_name}'")
                        return col
                    
                    # Check if column name is contained in search term
                    if col_normalized in search_normalized:
                        logger.info(f"Found fuzzy match: '{col}' for search '{column_name}'")
                        return col
        
        return None
    
    def get_column_value(self, row: pd.Series, column_name: str, default: str = '',
                        fuzzy: bool = True) -> str:
        """
        Get column value with case-insensitive and fuzzy matching.
        
        Args:
            row: DataFrame row
            column_name: Column name to retrieve (case-insensitive, fuzzy)
            default: Default value if column not found or value is None
            fuzzy: If True, also tries partial/fuzzy matching
            
        Returns:
            Column value as string, or default
        """
        # Try exact match first
        if column_name in row.index:
            value = row.get(column_name, default)
            if value is None or (isinstance(value, float) and pd.isna(value)):
                return default
            return str(value).strip()
        
        search_lower = column_name.lower()
        
        # Try case-insensitive exact match
        for col in row.index:
            if isinstance(col, str) and col.lower() == search_lower:
                value = row.get(col, default)
                if value is None or (isinstance(value, float) and pd.isna(value)):
                    return default
                return str(value).strip()
        
        # Try fuzzy matching if enabled
        if fuzzy:
            search_normalized = search_lower.replace('_', '').replace(' ', '').replace('-', '')
            
            for col in row.index:
                if isinstance(col, str):
                    col_normalized = col.lower().replace('_', '').replace(' ', '').replace('-', '')
                    
                    # Check if search term is contained in column name
                    if search_normalized in col_normalized:
                        value = row.get(col, default)
                        if value is None or (isinstance(value, float) and pd.isna(value)):
                            return default
                        return str(value).strip()
                    
                    # Check if column name is contained in search term
                    if col_normalized in search_normalized:
                        value = row.get(col, default)
                        if value is None or (isinstance(value, float) and pd.isna(value)):
                            return default
                        return str(value).strip()
        
        return default
    
    def load_file_a(self) -> pd.DataFrame:
        """Load and process File A (Active Offshore list)."""
        try:
            import glob
            
            # Use pattern matching to find file
            pattern = self.config.get('files.file_a.path_pattern', 'Active Offshore*.xlsx')
            search_path = str(self.base_dir / pattern)
            matching_files = glob.glob(search_path)
            
            if not matching_files:
                # Fallback to exact path
                file_a_path = self.base_dir / self.config.get('files.file_a.path')
            else:
                # Use most recent file
                file_a_path = Path(sorted(matching_files, reverse=True)[0])
                logger.info(f"Found File A matching pattern: {file_a_path.name}")
            
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
            df = df[df[email_col].str.contains('@', na=False)].copy()
            
            self.file_a_data = df
            
            logger.info(f"File A processed: {len(df)} valid records")
            
            # Type assertion for type checker
            assert isinstance(self.file_a_data, pd.DataFrame)
            return self.file_a_data
            
        except Exception as e:
            logger.error(f"Failed to load File A: {e}")
            raise
    
    def load_file_b(self) -> pd.DataFrame:
        """Load and process File B (HC Certification Status)."""
        try:
            import glob
            
            # Use pattern matching to find file
            pattern = self.config.get('files.file_b.path_pattern', 'T2G Certification*.xlsx')
            search_path = str(self.base_dir / pattern)
            matching_files = glob.glob(search_path)
            
            if not matching_files:
                # Fallback to exact path
                file_b_path_str = self.config.get('files.file_b.path')
                if not file_b_path_str:
                    raise ValueError(
                        "File B path not configured. Please set 'files.file_b.path' in config.yaml "
                        "or ensure files matching pattern 'T2G Certification*.xlsx' exist in the base directory."
                    )
                file_b_path = self.base_dir / file_b_path_str
            else:
                # Use most recent file
                file_b_path = Path(sorted(matching_files, reverse=True)[0])
                logger.info(f"Found File B matching pattern: {file_b_path.name}")
            
            if not file_b_path.exists():
                raise FileNotFoundError(
                    f"File B not found: {file_b_path}\n"
                    f"Please ensure the file exists or update the path in config.yaml"
                )
            
            logger.info(f"Loading File B: {file_b_path}")
            
            # Find worksheet matching pattern
            xl = pd.ExcelFile(file_b_path)
            hc_worksheet = None
            hc_pattern = self.config.get('files.file_b.hc_worksheet_pattern', 'HC Certification status')
            
            logger.info(f"Searching for worksheet matching pattern: '{hc_pattern}*'")
            logger.info(f"Available worksheets: {xl.sheet_names}")
            
            # Normalize pattern for flexible matching
            pattern_normalized = hc_pattern.rstrip('* ')
            
            # Try to find worksheet - flexible matching with hyphen support
            for sheet_name in xl.sheet_names:
                # Check direct match
                if sheet_name.startswith(pattern_normalized):
                    hc_worksheet = sheet_name
                    logger.info(f"✓ Found worksheet: '{hc_worksheet}'")
                    break
                # Also try with hyphen separator
                elif sheet_name.startswith(pattern_normalized + '-'):
                    hc_worksheet = sheet_name
                    logger.info(f"✓ Found worksheet: '{hc_worksheet}'")
                    break
            
            if not hc_worksheet:
                raise ValueError(
                    f"No worksheet found starting with '{pattern_normalized}' in file '{file_b_path.name}'.\n"
                    f"Available worksheets: {xl.sheet_names}\n"
                    f"Please update 'files.file_b.hc_worksheet_pattern' in config.yaml if needed."
                )
            
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
            
            # Column name for Industry Badge status (try case-insensitive match)
            badge_col_search = "Industry Badge Met Ind Cred Lvl?"
            badge_col = self.find_column_case_insensitive(self.file_b_data, badge_col_search)
            
            # Check if column exists
            if badge_col is None:
                logger.error(f"Column '{badge_col_search}' not found in File B (case-insensitive search)")
                logger.info(f"Available columns: {list(self.file_b_data.columns)}")
                raise KeyError(
                    f"Column '{badge_col_search}' not found in the HC Certification Status worksheet. "
                    f"Please verify that you're using the correct worksheet and that the column exists. "
                    f"Available columns: {list(self.file_b_data.columns)}"
                )
            
            logger.info(f"Found column: '{badge_col}' (matched case-insensitively)")
            
            # Find employees with "No Badge"
            no_badge_mask = (
                self.file_b_data[badge_col].astype(str).str.upper() == 'NO BADGE'
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
            
            # Get column names - use fuzzy matching for File B
            file_a_email_col = self.config.get('files.file_a.email_column')
            
            # Try to find the Intranet ID column with fuzzy matching
            file_b_email_col_search = 'Intranet ID'
            file_b_email_col = self.find_column_case_insensitive(
                self.file_b_data,
                file_b_email_col_search,
                fuzzy=True
            )
            
            if not file_b_email_col:
                # Fallback: try alternative names
                for alt_name in ['EMP_INTRANETID', 'INTRANET_ID', 'EMP INTRANETID', 'Employee Intranet ID']:
                    file_b_email_col = self.find_column_case_insensitive(
                        self.file_b_data,
                        alt_name,
                        fuzzy=True
                    )
                    if file_b_email_col:
                        logger.info(f"Found email column using alternative name: '{file_b_email_col}'")
                        break
            
            if not file_b_email_col:
                raise ValueError(
                    f"Could not find email/Intranet ID column in File B. "
                    f"Searched for: '{file_b_email_col_search}' and alternatives. "
                    f"Available columns: {list(self.file_b_data.columns)}"
                )
            
            logger.info(f"Using File B email column: '{file_b_email_col}'")
            
            # Standardize email columns for matching
            if file_b_email_col in self.file_b_data.columns:
                self.file_b_data = self.file_b_data.copy()
                # Convert to Series explicitly for type safety
                email_series = self.file_b_data[file_b_email_col]
                if isinstance(email_series, pd.Series):
                    self.file_b_data['email_lower'] = (
                        email_series.astype(str).str.strip().str.lower()
                    )
            else:
                raise ValueError(f"Column '{file_b_email_col}' not found in File B")
            
            if file_a_email_col in self.file_a_data.columns:
                self.file_a_data = self.file_a_data.copy()
                # Convert to Series explicitly for type safety
                email_series = self.file_a_data[file_a_email_col]
                if isinstance(email_series, pd.Series):
                    self.file_a_data['email_lower'] = (
                        email_series.astype(str).str.strip().str.lower()
                    )
            else:
                raise ValueError(f"Column '{file_a_email_col}' not found in File A")
            
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
    
    def save_output_spreadsheet(self) -> Optional[Path]:
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
                           test_email: Optional[str] = None, limit: int = 0) -> bool:
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
            emp_name = "Unknown"  # Initialize to avoid unbound variable
            for idx, row in self.matched_data.iterrows():
                # Check limit
                if limit > 0 and sent_count >= limit:
                    logger.info(f"Reached email limit of {limit}")
                    break
                
                try:
                    # Get employee details using case-insensitive column matching
                    emp_email = self.get_column_value(row, 'Intranet ID', '')
                    emp_name = self.get_column_value(row, 'Emp_Name', 'Employee')
                    manager_email = self.get_column_value(row, 'GLOBAL_MGR', '')
                    badge_status = self.get_column_value(row, 'Industry Badge Met Ind Cred Lvl?', 'No Badge')
                    
                    # Use test email if in test mode, ensure not None
                    to_email = test_email if (test_mode and test_email) else emp_email
                    cc_email = test_email if (test_mode and test_email) else manager_email
                    
                    # Skip if no valid email
                    if not to_email:
                        logger.warning(f"Skipping {emp_name}: no valid email address")
                        continue
                    
                    # Send email
                    success = self.email_sender.send_industry_badge_reminder(
                        to_email=to_email,
                        cc_email=cc_email or "",  # Provide empty string if None
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
            
            return {
                'success': failed_count == 0,
                'sent': sent_count,
                'failed': failed_count,
                'no_employees': False
            }
            
        except Exception as e:
            logger.error(f"Failed to send emails: {e}")
            return {
                'success': False,
                'sent': 0,
                'failed': 0,
                'error': str(e)
            }
    
    def run(self, test_mode: bool = False, test_email: Optional[str] = None,
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
            
            # Track how many employees need badge before matching
            employees_needing_badge = len(self.file_b_data) if self.file_b_data is not None else 0
            
            # Step 5: Match with File A
            logger.info("\nSTEP 5: Matching with File A")
            logger.info("=" * 100)
            self.match_with_file_a()
            
            # Check if any employees were matched
            matched_count = len(self.matched_data) if self.matched_data is not None and not self.matched_data.empty else 0
            
            if matched_count == 0:
                logger.info("\n" + "=" * 100)
                logger.info("✓ WORKFLOW COMPLETED SUCCESSFULLY")
                logger.info("=" * 100)
                logger.info("ℹ️  Found employees needing Industry Badge, but none matched with Active Offshore list")
                logger.info("This means the employees are not in the current active offshore resource list.")
                logger.info("No reminder emails will be sent.")
                logger.info("=" * 100)
                
                return {
                    'success': True,
                    'employees_found': 0,
                    'employees_needing_badge': employees_needing_badge,
                    'no_active_employees': True,
                    'message': 'No active offshore employees pending for Industry Badge completion',
                    'output_file': None,
                    'draft_mode': self.draft_mode
                }
            
            # Step 6: Save output spreadsheet
            logger.info("\nSTEP 6: Saving output spreadsheet")
            logger.info("=" * 100)
            output_path = self.save_output_spreadsheet()
            
            # Step 7: Send reminder emails
            logger.info("\nSTEP 7: Sending reminder emails")
            logger.info("=" * 100)
            email_results = self.send_reminder_emails(
                test_mode=test_mode,
                test_email=test_email,
                limit=limit
            )
            
            # Prepare results
            results = {
                'success': email_results.get('success', False) if isinstance(email_results, dict) else email_results,
                'employees_found': matched_count,
                'employees_needing_badge': employees_needing_badge,
                'emails_sent': email_results.get('sent', 0) if isinstance(email_results, dict) else 0,
                'emails_failed': email_results.get('failed', 0) if isinstance(email_results, dict) else 0,
                'output_file': str(output_path) if output_path else None,
                'draft_mode': self.draft_mode,
                'no_active_employees': False
            }
            
            logger.info("\n" + "=" * 100)
            logger.info("✓ WORKFLOW COMPLETED SUCCESSFULLY")
            logger.info("=" * 100)
            logger.info(f"Employees needing badge: {employees_needing_badge}")
            logger.info(f"Active employees matched: {matched_count}")
            logger.info(f"Emails sent: {results['emails_sent']}")
            if self.draft_mode:
                logger.info("📧 Check your Outlook Drafts folder to review and send")
            logger.info("=" * 100)
            
            return results
            
        except Exception as e:
            logger.error("\n" + "=" * 100)
            logger.error("❌ WORKFLOW FAILED")
            logger.error("=" * 100)
            logger.error(f"Error: {e}", exc_info=True)
            logger.error("=" * 100)
            logger.error("Please check the logs above for details.")
            logger.error("=" * 100)
            
            return {
                'success': False,
                'error': str(e),
                'message': 'Workflow encountered an error. Please check the logs.'
            }


def main():
    """Main function for testing."""
    workflow = IndustryBadgeWorkflow(draft_mode=True)
    results = workflow.run(test_mode=True, test_email="test@example.com", limit=3)
    print(f"\nResults: {results}")


if __name__ == "__main__":
    main()

# Made with Bob