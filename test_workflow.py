#!/usr/bin/env python3
"""
Test Workflow Script for Certification Notifications
====================================================
This script runs the workflow in TEST MODE to safely test email functionality
without sending to all employees.

Features:
- Sends emails only to a test recipient
- Limits number of emails sent
- Creates drafts instead of sending
- Provides detailed test report

Usage:
    python test_workflow.py
    python test_workflow.py --test-email your.email@ibm.com
    python test_workflow.py --limit 5
    python test_workflow.py --send-mode  # Actually send instead of drafts
"""

import sys
import os
import logging
import argparse
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config_loader import ConfigLoader
from certification_workflow_outlook import CertificationWorkflowOutlook

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_workflow.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TestWorkflow:
    """Test workflow with safety controls"""
    
    def __init__(self, test_email=None, limit=3, draft_mode=True):
        """
        Initialize test workflow
        
        Args:
            test_email: Email address to send all test emails to
            limit: Maximum number of emails to send (0 = no limit)
            draft_mode: If True, create drafts; if False, send emails
        """
        self.test_email = test_email
        self.limit = limit
        self.draft_mode = draft_mode
        self.config = ConfigLoader()
        
    def run(self):
        """Run the test workflow"""
        logger.info("=" * 80)
        logger.info("STARTING TEST WORKFLOW")
        logger.info("=" * 80)
        logger.info(f"Test Email: {self.test_email or 'Use actual recipients'}")
        logger.info(f"Email Limit: {self.limit if self.limit > 0 else 'No limit'}")
        logger.info(f"Draft Mode: {self.draft_mode}")
        logger.info("=" * 80)
        
        # Confirm with user
        if not self.draft_mode:
            print("\nWARNING: You are about to SEND emails (not drafts)!")
            response = input("Are you sure you want to continue? (yes/no): ")
            if response.lower() != 'yes':
                logger.info("Test cancelled by user")
                return
        
        try:
            # Initialize workflow
            config = ConfigLoader()
            workflow = CertificationWorkflowOutlook(config=config, draft_mode=self.draft_mode)
            
            # Run workflow with test mode
            logger.info("\nRunning workflow...")
            results = workflow.run(
                send_emails=True,
                test_mode=True,
                test_email=self.test_email,
                limit_emails=self.limit
            )
            
            # Print results
            self._print_results(results)
            
            # Save test report
            self._save_test_report(results)
            
            logger.info("\nTest workflow completed successfully!")
            
            if self.draft_mode:
                logger.info("\nNEXT STEPS:")
                logger.info("1. Open Microsoft Outlook")
                logger.info("2. Go to your Drafts folder")
                logger.info(f"3. Review the {self.limit if self.limit > 0 else 'test'} email draft(s)")
                logger.info("4. If satisfied, run production workflow")
            
        except Exception as e:
            logger.error(f"Test workflow failed: {e}", exc_info=True)
            raise
    
    def _print_results(self, results):
        """Print test results"""
        print("\n" + "=" * 80)
        print("TEST RESULTS")
        print("=" * 80)
        print(f"Status: {results.get('status', 'UNKNOWN')}")
        print(f"File A records: {results.get('file_a_records', 0)}")
        print(f"File B records: {results.get('file_b_records', 0)}")
        print(f"Filtered records: {results.get('filtered_records', 0)}")
        print(f"Matched records: {results.get('matched_records', 0)}")
        print(f"Unique emails: {results.get('unique_emails', 0)}")
        print(f"Notifications generated: {results.get('notifications_generated', 0)}")
        print(f"Emails sent/drafted: {results.get('emails_sent', 0)}")
        print("=" * 80)
    
    def _save_test_report(self, results):
        """Save test report to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"output/Test_Report_{timestamp}.txt"
        
        os.makedirs("output", exist_ok=True)
        
        with open(report_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("CERTIFICATION WORKFLOW TEST REPORT\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Test Email: {self.test_email or 'Actual recipients'}\n")
            f.write(f"Email Limit: {self.limit if self.limit > 0 else 'No limit'}\n")
            f.write(f"Draft Mode: {self.draft_mode}\n\n")
            
            f.write("RESULTS:\n")
            f.write("-" * 80 + "\n")
            for key, value in results.items():
                f.write(f"{key}: {value}\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("Test completed successfully\n")
            f.write("=" * 80 + "\n")
        
        logger.info(f"Test report saved: {report_path}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Test Certification Workflow',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test with 3 emails in draft mode (default)
  python test_workflow.py
  
  # Test with specific email address
  python test_workflow.py --test-email your.email@ibm.com
  
  # Test with 5 emails
  python test_workflow.py --limit 5
  
  # Actually send emails (not drafts)
  python test_workflow.py --send-mode
  
  # Send 2 test emails to specific address
  python test_workflow.py --test-email your.email@ibm.com --limit 2 --send-mode
        """
    )
    
    parser.add_argument(
        '--test-email',
        type=str,
        help='Email address to send all test emails to (default: use actual recipients)'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=3,
        help='Maximum number of emails to send (default: 3, use 0 for no limit)'
    )
    
    parser.add_argument(
        '--send-mode',
        action='store_true',
        help='Actually send emails instead of creating drafts (USE WITH CAUTION!)'
    )
    
    args = parser.parse_args()
    
    # Create and run test workflow
    test = TestWorkflow(
        test_email=args.test_email,
        limit=args.limit,
        draft_mode=not args.send_mode
    )
    
    test.run()


if __name__ == "__main__":
    main()

# Made with Bob
