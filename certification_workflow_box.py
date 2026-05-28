"""
IBM BOB - Autonomous Agentic Workflow for Certification Status Notifications
WITH IBM BOX INTEGRATION
=============================================================================

This enhanced workflow supports:
- Reading input files from IBM Box folders
- Processing certification data
- Uploading output files to IBM Box folders
- Fallback to local file operations when Box is disabled

Author: IBM BOB
Date: 2026-05-28
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging
import sys
from pathlib import Path
from typing import Optional, Dict, List, Tuple

# Import original workflow
from certification_workflow import CertificationWorkflow

# Import Box integration
try:
    from box_integration import BoxIntegration
    BOX_AVAILABLE = True
except ImportError:
    BOX_AVAILABLE = False
    logging.warning("Box integration not available. Install with: pip install boxsdk[jwt]")

# Import config loader
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


class CertificationWorkflowBox(CertificationWorkflow):
    """Enhanced workflow with IBM Box integration."""
    
    def __init__(self, config: ConfigLoader, use_box: bool = None):
        """
        Initialize the workflow with Box integration support.
        
        Args:
            config: ConfigLoader instance with configuration
            use_box: Override Box enabled setting (None = use config)
        """
        self.config = config
        
        # Determine if Box should be used
        self.use_box = use_box if use_box is not None else config.get('box.enabled', False)
        
        # Initialize Box client if enabled
        self.box_client = None
        if self.use_box:
            if not BOX_AVAILABLE:
                raise ImportError("Box integration requested but boxsdk not installed")
            self._init_box_client()
        
        # Get file paths (will be updated after downloading from Box)
        self.file_a_path = None
        self.file_b_path = None
        self.output_dir = None
        
        # Initialize parent class attributes
        self.file_a_email_col = config.get('files.file_a.email_column', 'EMP_INTRANETID')
        self.file_b_email_col = config.get('files.file_b.email_column', 'Internet Email')
        self.client_name_col = config.get('files.file_b.client_column', 'Global_Client_Name')
        self.target_client = config.get('processing.target_client', 'WESTPAC BANKING CORPORATION')
        
        # Data containers
        self.file_a_data = None
        self.file_b_data = None
        self.matched_data = None
        self.notifications = []
        
        # Track downloaded and output files
        self.downloaded_files = []
        self.output_files = []
        
        logger.info("Workflow with Box integration initialized")
        logger.info(f"Box integration: {'ENABLED' if self.use_box else 'DISABLED'}")
    
    def _init_box_client(self):
        """Initialize Box client from configuration."""
        try:
            logger.info("Initializing Box client...")
            
            # Get Box configuration
            config_file = self.config.get('box.jwt.config_file')
            
            if config_file and Path(config_file).exists():
                # Use config file
                self.box_client = BoxIntegration(config_file=config_file)
            else:
                # Use individual credentials
                self.box_client = BoxIntegration(
                    client_id=self.config.get('box.jwt.client_id'),
                    client_secret=self.config.get('box.jwt.client_secret'),
                    enterprise_id=self.config.get('box.jwt.enterprise_id'),
                    jwt_key_id=self.config.get('box.jwt.jwt_key_id'),
                    rsa_private_key_file=self.config.get('box.jwt.rsa_private_key_file'),
                    rsa_private_key_passphrase=self.config.get('box.jwt.rsa_private_key_passphrase')
                )
            
            logger.info("Box client initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Box client: {e}")
            raise
    
    def download_input_files(self) -> Tuple[Path, Path]:
        """
        Download input files from Box or use local files.
        
        Returns:
            Tuple of (file_a_path, file_b_path)
        """
        if self.use_box:
            return self._download_from_box()
        else:
            return self._get_local_files()
    
    def _download_from_box(self) -> Tuple[Path, Path]:
        """Download input files from Box."""
        logger.info("=" * 100)
        logger.info("DOWNLOADING INPUT FILES FROM IBM BOX")
        logger.info("=" * 100)
        
        try:
            input_folder_id = self.config.get('box.folders.input_folder_id')
            if not input_folder_id:
                raise ValueError("Box input folder ID not configured")
            
            # Get file patterns
            file_patterns = self.config.get('box.input_file_patterns', ['*.xlsx', '*.xls'])
            
            # Download files from Box folder
            temp_dir = Path(self.config.get('files.output.directory', './output')) / 'temp'
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            downloaded = self.box_client.download_files_from_folder(
                folder_id=input_folder_id,
                output_dir=temp_dir,
                file_patterns=file_patterns
            )
            
            self.downloaded_files = downloaded
            
            # Identify File A and File B
            file_a_pattern = self.config.get('files.file_a.box_file_name', 'Active Offshore Cloud List')
            file_b_pattern = self.config.get('files.file_b.box_file_name', 'T2G Certification')
            
            file_a_path = None
            file_b_path = None
            
            for file_path in downloaded:
                file_name = file_path.name
                if file_a_pattern.lower() in file_name.lower():
                    file_a_path = file_path
                    logger.info(f"Identified File A: {file_name}")
                elif file_b_pattern.lower() in file_name.lower():
                    file_b_path = file_path
                    logger.info(f"Identified File B: {file_name}")
            
            if not file_a_path or not file_b_path:
                raise ValueError(f"Could not identify input files. Downloaded: {[f.name for f in downloaded]}")
            
            self.file_a_path = file_a_path
            self.file_b_path = file_b_path
            self.output_dir = temp_dir.parent
            
            logger.info(f"Files downloaded successfully from Box")
            return file_a_path, file_b_path
            
        except Exception as e:
            logger.error(f"Error downloading files from Box: {e}")
            raise
    
    def _get_local_files(self) -> Tuple[Path, Path]:
        """Get local file paths from configuration."""
        logger.info("Using local files (Box integration disabled)")
        
        base_dir = Path.cwd()
        
        file_a_path = self.config.get_file_path('files.file_a.path', base_dir)
        file_b_path = self.config.get_file_path('files.file_b.path', base_dir)
        output_dir = Path(self.config.get('files.output.directory', './output'))
        
        self.file_a_path = file_a_path
        self.file_b_path = file_b_path
        self.output_dir = output_dir
        
        logger.info(f"File A: {file_a_path}")
        logger.info(f"File B: {file_b_path}")
        
        return file_a_path, file_b_path
    
    def upload_output_files(self, output_files: List[Path]) -> Dict[str, str]:
        """
        Upload output files to Box or keep local.
        
        Args:
            output_files: List of output file paths
            
        Returns:
            Dictionary mapping file paths to Box file IDs (or empty if local)
        """
        if self.use_box:
            return self._upload_to_box(output_files)
        else:
            logger.info("Output files saved locally (Box integration disabled)")
            return {}
    
    def _upload_to_box(self, output_files: List[Path]) -> Dict[str, str]:
        """Upload output files to Box."""
        logger.info("=" * 100)
        logger.info("UPLOADING OUTPUT FILES TO IBM BOX")
        logger.info("=" * 100)
        
        try:
            output_folder_id = self.config.get('box.folders.output_folder_id')
            if not output_folder_id:
                raise ValueError("Box output folder ID not configured")
            
            # Upload files
            uploaded = self.box_client.upload_files(output_files, output_folder_id)
            
            logger.info(f"Uploaded {len(uploaded)} files to Box")
            for file_path, file_id in uploaded.items():
                logger.info(f"  - {Path(file_path).name} (ID: {file_id})")
            
            return uploaded
            
        except Exception as e:
            logger.error(f"Error uploading files to Box: {e}")
            raise
    
    def cleanup(self):
        """Clean up temporary files."""
        if self.use_box and self.config.get('box.cleanup_temp_files', True):
            logger.info("Cleaning up temporary files...")
            if self.box_client:
                self.box_client.cleanup_temp_files()
    
    def run(self, send_emails=False, smtp_config=None):
        """
        Execute the complete workflow with Box integration.
        
        Args:
            send_emails: Whether to send email notifications
            smtp_config: Dictionary with SMTP configuration
            
        Returns:
            Dictionary with workflow results
        """
        logger.info("=" * 100)
        logger.info("STARTING CERTIFICATION WORKFLOW WITH BOX INTEGRATION")
        logger.info("=" * 100)
        
        results = {
            'success': False,
            'box_enabled': self.use_box,
            'file_a_records': 0,
            'file_b_records': 0,
            'westpac_records': 0,
            'matched_records': 0,
            'unique_emails': 0,
            'notifications_generated': 0,
            'output_spreadsheet': None,
            'notifications_file': None,
            'emails_sent': 0,
            'box_files_downloaded': 0,
            'box_files_uploaded': 0,
            'errors': []
        }
        
        try:
            # Step 1: Download/Get input files
            logger.info("\n" + "=" * 100)
            logger.info("STEP 1: Getting input files")
            logger.info("=" * 100)
            self.download_input_files()
            if self.use_box:
                results['box_files_downloaded'] = len(self.downloaded_files)
            
            # Step 2-8: Run standard workflow
            logger.info("\n" + "=" * 100)
            logger.info("STEP 2: Loading File A (Active Offshore Cloud List)")
            logger.info("=" * 100)
            self.load_file_a()
            results['file_a_records'] = len(self.file_a_data)
            
            logger.info("\n" + "=" * 100)
            logger.info("STEP 3: Loading File B (T2G Certification Financial Services)")
            logger.info("=" * 100)
            self.load_file_b()
            results['file_b_records'] = len(self.file_b_data)
            
            logger.info("\n" + "=" * 100)
            logger.info("STEP 4: Filtering Westpac Banking Corporation records")
            logger.info("=" * 100)
            self.filter_westpac_records()
            results['westpac_records'] = len(self.file_b_data)
            
            logger.info("\n" + "=" * 100)
            logger.info("STEP 5: Matching email addresses")
            logger.info("=" * 100)
            self.match_emails()
            results['matched_records'] = len(self.matched_data) if self.matched_data is not None else 0
            
            logger.info("\n" + "=" * 100)
            logger.info("STEP 6: Extracting and consolidating data")
            logger.info("=" * 100)
            self.extract_and_consolidate_data()
            if self.matched_data is not None:
                results['unique_emails'] = self.matched_data['Internet Email'].nunique()
            
            logger.info("\n" + "=" * 100)
            logger.info("STEP 7: Saving consolidated spreadsheet")
            logger.info("=" * 100)
            output_file = self.save_output_spreadsheet()
            results['output_spreadsheet'] = str(output_file) if output_file else None
            if output_file:
                self.output_files.append(output_file)
            
            logger.info("\n" + "=" * 100)
            logger.info("STEP 8: Generating notification messages")
            logger.info("=" * 100)
            self.generate_all_notifications()
            results['notifications_generated'] = len(self.notifications)
            
            logger.info("\n" + "=" * 100)
            logger.info("STEP 9: Saving notification messages to file")
            logger.info("=" * 100)
            notifications_file = self.save_notifications_to_file()
            results['notifications_file'] = str(notifications_file) if notifications_file else None
            if notifications_file:
                self.output_files.append(notifications_file)
            
            # Step 10: Upload output files to Box
            if self.use_box and self.output_files:
                logger.info("\n" + "=" * 100)
                logger.info("STEP 10: Uploading output files to Box")
                logger.info("=" * 100)
                uploaded = self.upload_output_files(self.output_files)
                results['box_files_uploaded'] = len(uploaded)
            
            # Step 11: Send emails (optional)
            if send_emails and smtp_config:
                logger.info("\n" + "=" * 100)
                logger.info("STEP 11: Sending email notifications")
                logger.info("=" * 100)
                self.send_email_notifications(**smtp_config)
                results['emails_sent'] = len(self.notifications)
            
            results['success'] = True
            
            logger.info("\n" + "=" * 100)
            logger.info("WORKFLOW COMPLETED SUCCESSFULLY")
            logger.info("=" * 100)
            logger.info(f"Box integration: {'ENABLED' if self.use_box else 'DISABLED'}")
            if self.use_box:
                logger.info(f"Files downloaded from Box: {results['box_files_downloaded']}")
                logger.info(f"Files uploaded to Box: {results['box_files_uploaded']}")
            logger.info(f"File A records: {results['file_a_records']}")
            logger.info(f"File B total records: {results['file_b_records']}")
            logger.info(f"Westpac records: {results['westpac_records']}")
            logger.info(f"Matched records: {results['matched_records']}")
            logger.info(f"Unique emails: {results['unique_emails']}")
            logger.info(f"Notifications generated: {results['notifications_generated']}")
            
            return results
            
        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            results['errors'].append(str(e))
            return results
        
        finally:
            # Cleanup temporary files
            self.cleanup()


def main():
    """Main entry point for the workflow with Box integration."""
    
    # Load configuration
    config = ConfigLoader("config.yaml")
    
    # Validate configuration
    if not config.validate():
        logger.error("Configuration validation failed")
        return
    
    # Create workflow instance
    workflow = CertificationWorkflowBox(config)
    
    # Run workflow
    results = workflow.run(send_emails=False)
    
    # Print summary
    print("\n" + "=" * 100)
    print("WORKFLOW EXECUTION SUMMARY")
    print("=" * 100)
    print(f"Status: {'SUCCESS' if results['success'] else 'FAILED'}")
    print(f"Box Integration: {'ENABLED' if results['box_enabled'] else 'DISABLED'}")
    if results['box_enabled']:
        print(f"Files downloaded from Box: {results['box_files_downloaded']}")
        print(f"Files uploaded to Box: {results['box_files_uploaded']}")
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