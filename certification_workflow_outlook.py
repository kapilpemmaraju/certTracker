"""
IBM BOB - Certification Workflow with Outlook Integration
==========================================================

Complete workflow with:
- All V3 features (duplicate prevention, etc.)
- Outlook Win32 email integration (no SMTP needed)
- Draft mode for review before sending

Author: IBM BOB
Date: 2026-05-21
Version: 4.0.0 (Outlook Edition)
"""

import pandas as pd
from datetime import datetime
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any
from config_loader import ConfigLoader
from notification_tracker import NotificationTracker
from outlook_email_sender import OutlookEmailSender

# Import V2 workflow as base
from certification_workflow_v2 import CertificationWorkflowV2

logger = logging.getLogger(__name__)


class CertificationWorkflowOutlook(CertificationWorkflowV2):
    """
    Enhanced workflow with Outlook email integration.
    
    Features:
    - All V2 features (configuration-driven, scalable)
    - Duplicate notification prevention
    - Outlook Win32 email sending (no SMTP config needed)
    - Draft mode for review
    """
    
    def __init__(self, config: ConfigLoader, base_dir: Path = None, draft_mode: bool = True):
        """
        Initialize workflow with Outlook integration.
        
        Args:
            config: ConfigLoader instance
            base_dir: Base directory for relative paths
            draft_mode: If True, creates email drafts instead of sending
        """
        # Initialize parent class
        super().__init__(config, base_dir)
        
        # Initialize notification tracker
        tracker_file = self.output_dir / "notification_history.json"
        self.tracker = NotificationTracker(str(tracker_file))
        
        # Initialize Outlook email sender
        self.draft_mode = draft_mode
        self.outlook_sender = None
        self._init_outlook_sender()
        
        logger.info(f"Workflow initialized with Outlook integration (draft_mode={draft_mode})")
    
    def _init_outlook_sender(self):
        """Initialize Outlook email sender."""
        try:
            self.outlook_sender = OutlookEmailSender(draft_mode=self.draft_mode)
            logger.info("Outlook email sender initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Outlook: {e}")
            logger.warning("Email sending will be disabled")
            self.outlook_sender = None
    
    def filter_new_certifications(self):
        """Filter out certifications that have already been notified."""
        if self.matched_data is None or len(self.matched_data) == 0:
            logger.warning("No matched data to filter")
            return True
        
        logger.info("Filtering for new certifications (not previously notified)")
        
        try:
            initial_count = len(self.matched_data)
            
            # Convert to list of dicts for tracker
            certifications = self.matched_data.to_dict('records')
            
            # Filter using tracker
            new_certifications = self.tracker.get_new_certifications(certifications)
            
            # Convert back to DataFrame
            if new_certifications:
                self.matched_data = pd.DataFrame(new_certifications)
                filtered_count = len(self.matched_data)
                
                logger.info(f"Filtered {initial_count} certifications to {filtered_count} new ones")
                logger.info(f"Skipped {initial_count - filtered_count} duplicate notifications")
                
                self.metrics['initial_matched_records'] = initial_count
                self.metrics['new_certifications'] = filtered_count
                self.metrics['duplicate_certifications'] = initial_count - filtered_count
            else:
                logger.warning("No new certifications to notify")
                self.matched_data = pd.DataFrame()
                self.metrics['new_certifications'] = 0
                self.metrics['duplicate_certifications'] = initial_count
            
            return True
            
        except Exception as e:
            logger.error(f"Error filtering new certifications: {e}")
            raise
    
    def send_outlook_notifications(self):
        """Send notifications using Outlook."""
        if not self.notifications:
            logger.warning("No notifications to send")
            return True
        
        if self.outlook_sender is None:
            logger.error("Outlook sender not initialized. Cannot send emails.")
            return False
        
        # Apply email limit if in test mode
        notifications_to_send = self.notifications
        if hasattr(self, '_limit_emails') and self._limit_emails > 0:
            notifications_to_send = self.notifications[:self._limit_emails]
            logger.info(f"TEST MODE: Limiting to {len(notifications_to_send)} emails")
        
        logger.info(f"Sending {len(notifications_to_send)} notifications via Outlook...")
        
        try:
            sent_count = 0
            failed_count = 0
            
            for notification in notifications_to_send:
                original_email = notification['email']
                name = notification['name']
                
                # Override email if test_email is provided
                email = original_email
                if hasattr(self, '_test_email') and self._test_email:
                    email = self._test_email
                    logger.info(f"TEST MODE: Redirecting email from {original_email} to {email}")
                
                # Get certifications for this email
                email_certs = self.matched_data[
                    self.matched_data['Internet Email'].str.lower() == original_email.lower()
                ]
                
                # Convert to list of dicts
                certifications = email_certs.to_dict('records')
                
                # Send via Outlook
                success = self.outlook_sender.send_certification_notification(
                    email=email,
                    name=name,
                    certifications=certifications,
                    client_name=self.target_client
                )
                
                if success:
                    sent_count += 1
                    
                    # Record sent notification (only if not in test mode)
                    if not hasattr(self, '_test_mode') or not self._test_mode:
                        for cert in certifications:
                            self.tracker.record_notification(
                                email=original_email,
                                credential_title=cert.get('Credential Title', ''),
                                credential_award_date=cert.get('Credential Award Date', ''),
                                credential_expiry_date=cert.get('Credential Expiry Date', ''),
                                vendor=cert.get('Vendor', '')
                            )
                else:
                    failed_count += 1
            
            if self.draft_mode:
                logger.info(f"Created {sent_count} email drafts in Outlook")
                logger.info("Check your Outlook Drafts folder to review and send")
            else:
                logger.info(f"Sent {sent_count} emails via Outlook")
            
            if failed_count > 0:
                logger.warning(f"Failed to send {failed_count} emails")
            
            self.metrics['emails_sent'] = sent_count
            self.metrics['emails_failed'] = failed_count
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending Outlook notifications: {e}")
            raise
    
    def generate_tracking_report(self) -> Path:
        """Generate notification tracking report."""
        logger.info("Generating notification tracking report")
        
        try:
            report_content = self.tracker.generate_report()
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_file = self.output_dir / f"Notification_Tracking_Report_{timestamp}.txt"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            logger.info(f"Tracking report saved: {report_file}")
            self.metrics['tracking_report'] = str(report_file)
            
            return report_file
            
        except Exception as e:
            logger.error(f"Error generating tracking report: {e}")
            raise
    
    def run(self, send_emails: bool = True, test_mode: bool = False,
            test_email: str = None, limit_emails: int = 0) -> Dict[str, Any]:
        """
        Execute the complete workflow with Outlook email sending.
        
        Args:
            send_emails: Whether to send emails
            test_mode: If True, enables test mode features
            test_email: Email address to send all test emails to (overrides actual recipients)
            limit_emails: Maximum number of emails to send (0 = no limit)
        """
        self._test_mode = test_mode
        self._test_email = test_email
        self._limit_emails = limit_emails
        
        logger.info("=" * 100)
        logger.info("STARTING CERTIFICATION WORKFLOW (OUTLOOK EDITION)")
        if test_mode:
            logger.info("*** TEST MODE ENABLED ***")
            if test_email:
                logger.info(f"*** All emails will be sent to: {test_email} ***")
            if limit_emails > 0:
                logger.info(f"*** Email limit: {limit_emails} ***")
        logger.info("=" * 100)
        
        results = {
            'success': False,
            'errors': []
        }
        
        try:
            # Steps 1-5: Load, filter, match, consolidate
            logger.info("\n" + "=" * 100)
            logger.info("STEP 1: Loading File A")
            logger.info("=" * 100)
            self.load_file_a()
            
            logger.info("\n" + "=" * 100)
            logger.info("STEP 2: Loading File B")
            logger.info("=" * 100)
            self.load_file_b()
            
            logger.info("\n" + "=" * 100)
            logger.info("STEP 3: Filtering by client")
            logger.info("=" * 100)
            self.filter_by_client()
            
            logger.info("\n" + "=" * 100)
            logger.info("STEP 4: Matching emails")
            logger.info("=" * 100)
            self.match_emails()
            
            logger.info("\n" + "=" * 100)
            logger.info("STEP 5: Extracting and consolidating")
            logger.info("=" * 100)
            self.extract_and_consolidate_data()
            
            # Step 6: Filter for new certifications
            logger.info("\n" + "=" * 100)
            logger.info("STEP 6: Filtering new certifications (duplicate prevention)")
            logger.info("=" * 100)
            self.filter_new_certifications()
            
            # Check if there are any new certifications
            if self.matched_data is None or len(self.matched_data) == 0:
                logger.warning("No new certifications to process")
                self.generate_tracking_report()
                
                results['success'] = True
                results['message'] = "No new certifications to notify"
                results.update(self.metrics)
                
                logger.info("\n" + "=" * 100)
                logger.info("WORKFLOW COMPLETED - NO NEW NOTIFICATIONS NEEDED")
                logger.info("=" * 100)
                
                return results
            
            # Continue with remaining steps
            logger.info("\n" + "=" * 100)
            logger.info("STEP 7: Saving spreadsheet")
            logger.info("=" * 100)
            self.save_output_spreadsheet()
            
            logger.info("\n" + "=" * 100)
            logger.info("STEP 8: Generating notifications")
            logger.info("=" * 100)
            self.generate_all_notifications()
            
            logger.info("\n" + "=" * 100)
            logger.info("STEP 9: Saving notifications to file")
            logger.info("=" * 100)
            self.save_notifications_to_file()
            
            # Step 10: Send via Outlook
            if send_emails and self.outlook_sender:
                logger.info("\n" + "=" * 100)
                logger.info("STEP 10: Sending notifications via Outlook")
                logger.info("=" * 100)
                self.send_outlook_notifications()
            else:
                logger.info("\n" + "=" * 100)
                logger.info("STEP 10: Email sending disabled")
                logger.info("=" * 100)
                logger.info("Notifications saved to file only")
            
            # Step 11: Generate tracking report
            logger.info("\n" + "=" * 100)
            logger.info("STEP 11: Generating tracking report")
            logger.info("=" * 100)
            self.generate_tracking_report()
            
            # Save metrics
            self.save_metrics()
            
            results['success'] = True
            results.update(self.metrics)
            
            logger.info("\n" + "=" * 100)
            logger.info("WORKFLOW COMPLETED SUCCESSFULLY")
            logger.info("=" * 100)
            logger.info(f"New certifications processed: {self.metrics.get('new_certifications', 0)}")
            logger.info(f"Duplicate notifications prevented: {self.metrics.get('duplicate_certifications', 0)}")
            
            if send_emails:
                if self.draft_mode:
                    logger.info(f"Email drafts created: {self.metrics.get('emails_sent', 0)}")
                    logger.info("📧 Check your Outlook Drafts folder to review and send")
                else:
                    logger.info(f"Emails sent: {self.metrics.get('emails_sent', 0)}")
            
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
        
        # Create workflow with Outlook integration
        # draft_mode=True: Creates drafts for review
        # draft_mode=False: Sends emails immediately
        workflow = CertificationWorkflowOutlook(
            config=config,
            base_dir=base_dir,
            draft_mode=True  # ⭐ Change to False to send immediately
        )
        
        # Run workflow with email sending enabled
        results = workflow.run(send_emails=True)
        
        # Print summary
        print("\n" + "=" * 100)
        print("WORKFLOW EXECUTION SUMMARY")
        print("=" * 100)
        print(f"Status: {'SUCCESS' if results['success'] else 'FAILED'}")
        print(f"File A records: {results.get('file_a_records', 0)}")
        print(f"File B records: {results.get('file_b_records', 0)}")
        print(f"Filtered records: {results.get('filtered_records', 0)}")
        print(f"Initial matched records: {results.get('initial_matched_records', 0)}")
        print(f"New certifications: {results.get('new_certifications', 0)}")
        print(f"Duplicate certifications (skipped): {results.get('duplicate_certifications', 0)}")
        print(f"Unique emails: {results.get('unique_emails', 0)}")
        print(f"Notifications generated: {results.get('notifications_generated', 0)}")
        
        if results.get('emails_sent'):
            if workflow.draft_mode:
                print(f"Email drafts created: {results.get('emails_sent', 0)}")
                print("\n📧 CHECK YOUR OUTLOOK DRAFTS FOLDER")
                print("   Review the emails and send them manually")
            else:
                print(f"Emails sent: {results.get('emails_sent', 0)}")
        
        print(f"\nOutput files:")
        print(f"  Spreadsheet: {results.get('output_spreadsheet', 'N/A')}")
        print(f"  Notifications: {results.get('notifications_file', 'N/A')}")
        print(f"  Tracking Report: {results.get('tracking_report', 'N/A')}")
        
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
