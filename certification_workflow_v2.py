"""
IBM BOB - Scalable Configuration-Driven Certification Workflow
===============================================================

Enhanced version with:
- Configuration-driven architecture (YAML)
- Loose coupling through dependency injection
- Scalable design patterns
- Environment variable support
- Multiple output formats
- Advanced error handling

Author: IBM BOB
Date: 2026-05-21
Version: 2.0.0
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
from typing import Dict, List, Optional, Any
import json
from config_loader import ConfigLoader

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


class CertificationWorkflowV2:
    """
    Scalable, configuration-driven workflow for certification processing.
    
    Features:
    - Configuration-driven (YAML)
    - Loose coupling
    - Dependency injection
    - Multiple output formats
    - Advanced error handling
    """
    
    def __init__(self, config: ConfigLoader, base_dir: Optional[Path] = None):
        """
        Initialize workflow with configuration.
        
        Args:
            config: ConfigLoader instance with workflow configuration
            base_dir: Base directory for relative paths (default: current directory)
        """
        self.config = config
        self.base_dir = base_dir or Path.cwd()
        
        # Validate configuration
        if not self.config.validate():
            raise ValueError("Invalid configuration")
        
        # Initialize paths
        self._init_paths()
        
        # Initialize configuration values
        self._init_config_values()
        
        # Data containers
        self.file_a_data = None
        self.file_b_data = None
        self.matched_data = None
        self.notifications = []
        self.metrics = {}
        
        logger.info("Workflow initialized with configuration")
        logger.info(f"Base directory: {self.base_dir}")
    
    def _init_paths(self):
        """Initialize file paths from configuration."""
        # Input files - use pattern matching to find files
        import glob
        
        # Try to find File A using pattern
        file_a_pattern = self.config.get('files.file_a.path_pattern', 'Active Offshore*.xlsx')
        file_a_search = str(self.base_dir / file_a_pattern)
        file_a_matches = glob.glob(file_a_search)
        
        if file_a_matches:
            # Use most recent file
            self.file_a_path = Path(sorted(file_a_matches, reverse=True)[0])
            logger.info(f"Found File A using pattern: {self.file_a_path.name}")
        else:
            # Fallback to configured path
            file_a_path_str = self.config.get('files.file_a.path')
            if file_a_path_str:
                self.file_a_path = self.base_dir / file_a_path_str if not Path(file_a_path_str).is_absolute() else Path(file_a_path_str)
            else:
                self.file_a_path = None
                logger.warning(f"File A not found. Searched for pattern: {file_a_pattern}")
        
        # Try to find File B using pattern
        file_b_pattern = self.config.get('files.file_b.path_pattern', 'T2G Certification*.xlsx')
        file_b_search = str(self.base_dir / file_b_pattern)
        file_b_matches = glob.glob(file_b_search)
        
        if file_b_matches:
            # Use most recent file
            self.file_b_path = Path(sorted(file_b_matches, reverse=True)[0])
            logger.info(f"Found File B using pattern: {self.file_b_path.name}")
        else:
            # Fallback to configured path
            file_b_path_str = self.config.get('files.file_b.path')
            if file_b_path_str:
                self.file_b_path = self.base_dir / file_b_path_str if not Path(file_b_path_str).is_absolute() else Path(file_b_path_str)
            else:
                self.file_b_path = None
                logger.warning(f"File B not found. Searched for pattern: {file_b_pattern}")
        
        # Output directory
        output_dir = self.config.get('files.output.directory', './output')
        self.output_dir = Path(output_dir)
        if not self.output_dir.is_absolute():
            self.output_dir = self.base_dir / self.output_dir
        
        # Create output directory if needed
        if self.config.get('files.output.create_if_missing', True):
            self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup directory
        if self.config.get('files.backup.enabled', False):
            backup_dir = self.config.get('files.backup.directory', './backup')
            self.backup_dir = Path(backup_dir)
            if not self.backup_dir.is_absolute():
                self.backup_dir = self.base_dir / self.backup_dir
            self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def _init_config_values(self):
        """Initialize configuration values."""
        # Column names
        self.file_a_email_col = self.config.get('files.file_a.email_column')
        self.file_b_email_col = self.config.get('files.file_b.email_column')
        self.client_name_col = self.config.get('files.file_b.client_column')
        self.worksheet_name = self.config.get('files.file_b.worksheet')
        
        # Processing configuration
        self.target_client = self.config.get('processing.target_client')
        self.case_sensitive = self.config.get('processing.case_sensitive', False)
        self.missing_data_placeholder = self.config.get('processing.missing_data_placeholder', 'Not Available')
        self.date_format = self.config.get('processing.date_format', '%Y-%m-%d')
        
        # Required and optional fields
        self.required_fields = self.config.get('processing.required_fields', [])
        self.optional_fields = self.config.get('processing.optional_fields', [])
    
    def normalize_email(self, email: str) -> Optional[str]:
        """
        Normalize email address for comparison.
        
        Args:
            email: Email address string
            
        Returns:
            Normalized email string or None if invalid
        """
        if pd.isna(email):
            return None
        
        email_str = str(email).strip()
        
        # Validate email format if configured
        if self.config.get('validation.validate_email_format', True):
            import re
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(pattern, email_str):
                logger.warning(f"Invalid email format: {email_str}")
                return None
        
        # Apply case sensitivity setting
        if not self.config.get('processing.email_matching.case_sensitive', False):
            email_str = email_str.lower()
        
        return email_str
    
    def parse_name_from_email(self, email: str) -> str:
        """
        Extract name from email address.
        
        Args:
            email: Email address string
            
        Returns:
            Parsed name or placeholder
        """
        if pd.isna(email):
            return self.missing_data_placeholder
        
        try:
            email_str = str(email).strip()
            if '@' in email_str:
                name_part = email_str.split('@')[0]
                
                # Apply name parsing configuration
                if self.config.get('processing.name_parsing.replace_dots', True):
                    name_part = name_part.replace('.', ' ')
                
                if self.config.get('processing.name_parsing.replace_underscores', True):
                    name_part = name_part.replace('_', ' ')
                
                if self.config.get('processing.name_parsing.title_case', True):
                    name_part = name_part.title()
                
                return name_part
            
            return self.missing_data_placeholder
            
        except Exception as e:
            logger.warning(f"Error parsing name from email {email}: {e}")
            return self.missing_data_placeholder
    
    def load_file_a(self):
        """Load and validate File A."""
        logger.info(f"Loading File A: {self.file_a_path}")
        
        try:
            # Validate file exists
            if self.config.get('validation.check_file_exists', True):
                if not self.file_a_path.exists():
                    raise FileNotFoundError(f"File A not found: {self.file_a_path}")
            
            # Load file
            self.file_a_data = pd.read_excel(self.file_a_path)
            logger.info(f"File A loaded: {len(self.file_a_data)} rows")
            
            # Validate required column
            if self.file_a_email_col not in self.file_a_data.columns:
                raise ValueError(f"Required column '{self.file_a_email_col}' not found in File A")
            
            # Normalize emails
            self.file_a_data['normalized_email'] = self.file_a_data[self.file_a_email_col].apply(
                self.normalize_email
            )
            
            # Remove invalid emails
            initial_count = len(self.file_a_data)
            self.file_a_data = self.file_a_data[self.file_a_data['normalized_email'].notna()]
            removed = initial_count - len(self.file_a_data)
            
            if removed > 0:
                logger.warning(f"Removed {removed} rows with invalid email addresses")
            
            logger.info(f"File A processed: {len(self.file_a_data)} valid records")
            self.metrics['file_a_records'] = len(self.file_a_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading File A: {e}")
            raise
    
    def load_file_b(self):
        """Load and validate File B."""
        logger.info(f"Loading File B: {self.file_b_path}")
        
        try:
            # Validate file exists
            if self.config.get('validation.check_file_exists', True):
                if not self.file_b_path.exists():
                    raise FileNotFoundError(f"File B not found: {self.file_b_path}")
            
            # Load Excel file
            xl = pd.ExcelFile(self.file_b_path)
            
            # Find worksheet using flexible pattern matching
            worksheet_pattern = self.config.get('files.file_b.worksheet_pattern', 'T2G Certification data')
            worksheet_name = None
            
            logger.info(f"Searching for worksheet matching pattern: '{worksheet_pattern}*'")
            logger.info(f"Available worksheets: {xl.sheet_names}")
            
            # Normalize pattern for comparison (remove trailing spaces/asterisks)
            pattern_normalized = worksheet_pattern.rstrip('* ')
            
            for sheet_name in xl.sheet_names:
                # Check if sheet name starts with pattern (flexible matching)
                # Handle both "T2G Certification data" and "T2G Certification data-"
                if sheet_name.startswith(pattern_normalized):
                    worksheet_name = sheet_name
                    logger.info(f"✓ Found worksheet: '{worksheet_name}'")
                    break
                # Also try with hyphen
                elif sheet_name.startswith(pattern_normalized + '-'):
                    worksheet_name = sheet_name
                    logger.info(f"✓ Found worksheet: '{worksheet_name}'")
                    break
            
            if not worksheet_name:
                raise ValueError(
                    f"No worksheet found starting with '{pattern_normalized}' in File B.\n"
                    f"Available worksheets: {xl.sheet_names}\n"
                    f"Please update 'files.file_b.worksheet_pattern' in config.yaml if needed."
                )
            
            # Load worksheet
            self.file_b_data = pd.read_excel(xl, sheet_name=worksheet_name)
            logger.info(f"File B loaded: {len(self.file_b_data)} rows from worksheet '{worksheet_name}'")
            
            # Validate required columns
            required_columns = [
                self.file_b_email_col,
                self.client_name_col
            ] + self.required_fields
            
            missing_columns = [col for col in required_columns if col not in self.file_b_data.columns]
            if missing_columns:
                raise ValueError(f"Required columns not found in File B: {missing_columns}")
            
            # Normalize emails
            self.file_b_data['normalized_email'] = self.file_b_data[self.file_b_email_col].apply(
                self.normalize_email
            )
            
            logger.info(f"File B processed: {len(self.file_b_data)} records")
            self.metrics['file_b_records'] = len(self.file_b_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading File B: {e}")
            raise
    
    def filter_by_client(self):
        """Filter File B records by target client."""
        logger.info(f"Filtering records for client: {self.target_client}")
        
        try:
            initial_count = len(self.file_b_data)
            
            # Apply case sensitivity setting
            if self.case_sensitive:
                self.file_b_data = self.file_b_data[
                    self.file_b_data[self.client_name_col] == self.target_client
                ]
            else:
                self.file_b_data = self.file_b_data[
                    self.file_b_data[self.client_name_col].str.upper() == self.target_client.upper()
                ]
            
            filtered_count = len(self.file_b_data)
            logger.info(f"Filtered {filtered_count} records (from {initial_count} total)")
            
            self.metrics['filtered_records'] = filtered_count
            
            if filtered_count == 0:
                logger.warning(f"No records found for {self.target_client}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error filtering by client: {e}")
            raise
    
    def match_emails(self):
        """Match email addresses between File A and File B."""
        logger.info("Matching email addresses")
        
        try:
            # Perform inner join
            self.matched_data = pd.merge(
                self.file_a_data,
                self.file_b_data,
                on='normalized_email',
                how='inner',
                suffixes=('_fileA', '_fileB')
            )
            
            matched_count = len(self.matched_data)
            unique_emails = self.matched_data['normalized_email'].nunique()
            
            logger.info(f"Matched {matched_count} records for {unique_emails} unique emails")
            
            self.metrics['matched_records'] = matched_count
            self.metrics['unique_emails'] = unique_emails
            
            # Check minimum match rate
            min_match_rate = self.config.get('advanced.min_match_rate', 0.0)
            if len(self.file_a_data) > 0:
                match_rate = unique_emails / len(self.file_a_data)
                self.metrics['match_rate'] = match_rate
                
                if match_rate < min_match_rate:
                    logger.warning(f"Match rate {match_rate:.2%} is below minimum {min_match_rate:.2%}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error matching emails: {e}")
            raise
    
    def extract_and_consolidate_data(self):
        """Extract required fields and create consolidated output."""
        logger.info("Extracting and consolidating data")
        
        try:
            if self.matched_data is None or len(self.matched_data) == 0:
                logger.warning("No matched data to consolidate")
                return True
            
            consolidated = pd.DataFrame()
            
            # Internet Email
            consolidated['Internet Email'] = self.matched_data[self.file_b_email_col]
            
            # Name (parsed from email)
            consolidated['Name'] = self.matched_data[self.file_b_email_col].apply(
                self.parse_name_from_email
            )
            
            # Extract required fields
            for field in self.required_fields:
                if field in self.matched_data.columns:
                    if 'Date' in field:
                        # Format dates
                        consolidated[field] = self.matched_data[field].apply(
                            lambda x: x.strftime(self.date_format) if pd.notna(x) and isinstance(x, (pd.Timestamp, datetime)) else self.missing_data_placeholder
                        )
                    else:
                        consolidated[field] = self.matched_data[field].fillna(self.missing_data_placeholder)
            
            # Extract optional fields if available
            for field in self.optional_fields:
                if field in self.matched_data.columns:
                    consolidated[field] = self.matched_data[field].fillna(self.missing_data_placeholder)
            
            # Add fields from File A if available
            if 'EMP_NAME' in self.matched_data.columns:
                consolidated['Employee Name'] = self.matched_data['EMP_NAME'].fillna(self.missing_data_placeholder)
            
            if 'EMP ID' in self.matched_data.columns:
                consolidated['Employee ID'] = self.matched_data['EMP ID'].fillna(self.missing_data_placeholder)
            
            self.matched_data = consolidated
            
            logger.info(f"Consolidated data created: {len(consolidated)} records")
            
            return True
            
        except Exception as e:
            logger.error(f"Error consolidating data: {e}")
            raise
    
    def save_output_spreadsheet(self) -> Optional[Path]:
        """Save consolidated data to Excel file."""
        if not self.config.get('output.spreadsheet.enabled', True):
            logger.info("Spreadsheet output disabled in configuration")
            return None
        
        logger.info("Saving consolidated spreadsheet")
        
        try:
            if self.matched_data is None or len(self.matched_data) == 0:
                logger.warning("No data to save")
                return None
            
            # Generate filename from pattern
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename_pattern = self.config.get('output.spreadsheet.filename_pattern')
            filename = filename_pattern.format(
                client=self.target_client.replace(' ', '_'),
                timestamp=timestamp
            )
            
            output_file = self.output_dir / filename
            
            # Save to Excel
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                self.matched_data.to_excel(writer, index=False, sheet_name='Consolidated Data')
                
                # Apply formatting if configured
                if self.config.get('output.spreadsheet.freeze_header', True):
                    worksheet = writer.sheets['Consolidated Data']
                    worksheet.freeze_panes = 'A2'
                
                if self.config.get('output.spreadsheet.auto_filter', True):
                    worksheet = writer.sheets['Consolidated Data']
                    worksheet.auto_filter.ref = worksheet.dimensions
            
            logger.info(f"Spreadsheet saved: {output_file}")
            self.metrics['output_spreadsheet'] = str(output_file)
            
            return output_file
            
        except Exception as e:
            logger.error(f"Error saving spreadsheet: {e}")
            raise
    
    def generate_notification_message(self, email: str, certifications: pd.DataFrame) -> str:
        """Generate notification message for a single email."""
        try:
            name = certifications.iloc[0]['Name']
            
            # Get template from configuration
            greeting = self.config.get('notifications.template.greeting', 'Dear {name},')
            footer = self.config.get('notifications.template.footer', '')
            
            message = f"""
{greeting.format(name=name)}

This is an automated notification regarding your IBM certification status for the {self.target_client} project.

Your Current Certifications:
{'=' * 80}

"""
            
            # Add each certification
            for idx, cert in certifications.iterrows():
                message += f"""
Certification #{idx + 1}:
  • Vendor:              {cert.get('Vendor', self.missing_data_placeholder)}
  • Credential Title:    {cert.get('Credential Title', self.missing_data_placeholder)}
  • Award Date:          {cert.get('Credential Award Date', self.missing_data_placeholder)}
  • Expiry Date:         {cert.get('Credential Expiry Date', self.missing_data_placeholder)}
{'-' * 80}
"""
            
            message += f"""

Total Certifications: {len(certifications)}

{footer}
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
            
            # Group by email
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
            
            logger.info(f"Generated {len(self.notifications)} notifications")
            self.metrics['notifications_generated'] = len(self.notifications)
            
            return True
            
        except Exception as e:
            logger.error(f"Error generating notifications: {e}")
            raise
    
    def save_notifications_to_file(self) -> Optional[Path]:
        """Save notification messages to file."""
        if not self.config.get('output.notifications_file.enabled', True):
            logger.info("Notifications file output disabled")
            return None
        
        logger.info("Saving notification messages")
        
        try:
            if not self.notifications:
                logger.warning("No notifications to save")
                return None
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename_pattern = self.config.get('notifications.filename_pattern')
            filename = filename_pattern.format(
                client=self.target_client.replace(' ', '_'),
                timestamp=timestamp
            )
            
            output_file = self.output_dir / filename
            
            with open(output_file, 'w', encoding='utf-8') as f:
                if self.config.get('output.notifications_file.include_header', True):
                    f.write("=" * 100 + "\n")
                    f.write(f"IBM CERTIFICATION NOTIFICATIONS - {self.target_client}\n")
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
            
            logger.info(f"Notifications saved: {output_file}")
            self.metrics['notifications_file'] = str(output_file)
            
            return output_file
            
        except Exception as e:
            logger.error(f"Error saving notifications: {e}")
            raise
    
    def save_metrics(self):
        """Save workflow metrics to JSON file."""
        if not self.config.get('monitoring.collect_metrics', True):
            return
        
        try:
            metrics_file = self.output_dir / self.config.get('monitoring.metrics_file', 'workflow_metrics.json')
            
            self.metrics['timestamp'] = datetime.now().isoformat()
            self.metrics['config_version'] = self.config.get('version', 'unknown')
            
            with open(metrics_file, 'w') as f:
                json.dump(self.metrics, f, indent=2)
            
            logger.info(f"Metrics saved: {metrics_file}")
            
        except Exception as e:
            logger.error(f"Error saving metrics: {e}")
    
    def run(self) -> Dict[str, Any]:
        """Execute the complete workflow."""
        logger.info("=" * 100)
        logger.info("STARTING CERTIFICATION WORKFLOW V2.0")
        logger.info("=" * 100)
        
        results = {
            'success': False,
            'errors': []
        }
        
        try:
            # Step 1: Load File A
            logger.info("\n" + "=" * 100)
            logger.info("STEP 1: Loading File A")
            logger.info("=" * 100)
            self.load_file_a()
            
            # Step 2: Load File B
            logger.info("\n" + "=" * 100)
            logger.info("STEP 2: Loading File B")
            logger.info("=" * 100)
            self.load_file_b()
            
            # Step 3: Filter by client
            logger.info("\n" + "=" * 100)
            logger.info("STEP 3: Filtering by client")
            logger.info("=" * 100)
            self.filter_by_client()
            
            # Step 4: Match emails
            logger.info("\n" + "=" * 100)
            logger.info("STEP 4: Matching emails")
            logger.info("=" * 100)
            self.match_emails()
            
            # Step 5: Extract and consolidate
            logger.info("\n" + "=" * 100)
            logger.info("STEP 5: Extracting and consolidating")
            logger.info("=" * 100)
            self.extract_and_consolidate_data()
            
            # Step 6: Save spreadsheet
            logger.info("\n" + "=" * 100)
            logger.info("STEP 6: Saving spreadsheet")
            logger.info("=" * 100)
            self.save_output_spreadsheet()
            
            # Step 7: Generate notifications
            logger.info("\n" + "=" * 100)
            logger.info("STEP 7: Generating notifications")
            logger.info("=" * 100)
            self.generate_all_notifications()
            
            # Step 8: Save notifications
            logger.info("\n" + "=" * 100)
            logger.info("STEP 8: Saving notifications")
            logger.info("=" * 100)
            self.save_notifications_to_file()
            
            # Step 9: Save metrics
            self.save_metrics()
            
            results['success'] = True
            results.update(self.metrics)
            
            logger.info("\n" + "=" * 100)
            logger.info("WORKFLOW COMPLETED SUCCESSFULLY")
            logger.info("=" * 100)
            
            return results
            
        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            results['errors'].append(str(e))
            return results


def main():
    """Main entry point."""
    try:
        # Load configuration
        config = ConfigLoader("config.yaml")
        
        # Set base directory
        base_dir = Path(r"C:/Users/KAPILPEMMARAJU/Downloads/CertificationsWestpac")
        
        # Create workflow
        workflow = CertificationWorkflowV2(config, base_dir)
        
        # Run workflow
        results = workflow.run()
        
        # Print summary
        print("\n" + "=" * 100)
        print("WORKFLOW EXECUTION SUMMARY")
        print("=" * 100)
        print(f"Status: {'SUCCESS' if results['success'] else 'FAILED'}")
        print(f"File A records: {results.get('file_a_records', 0)}")
        print(f"File B records: {results.get('file_b_records', 0)}")
        print(f"Filtered records: {results.get('filtered_records', 0)}")
        print(f"Matched records: {results.get('matched_records', 0)}")
        print(f"Unique emails: {results.get('unique_emails', 0)}")
        print(f"Notifications: {results.get('notifications_generated', 0)}")
        print(f"\nOutput files:")
        print(f"  Spreadsheet: {results.get('output_spreadsheet', 'N/A')}")
        print(f"  Notifications: {results.get('notifications_file', 'N/A')}")
        
        if results.get('errors'):
            print(f"\nErrors:")
            for error in results['errors']:
                print(f"  - {error}")
        
        print("=" * 100)
        
        return results
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()

# Made with Bob
