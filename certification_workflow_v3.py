"""
IBM BOB - Certification Workflow V3.0 with Duplicate Prevention
================================================================

Enhanced version with:
- Duplicate notification prevention
- Notification history tracking
- All V2.0 features (configuration-driven, scalable, etc.)

Author: IBM BOB
Date: 2026-05-21
Version: 3.0.0
"""

import pandas as pd
from datetime import datetime
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any
from config_loader import ConfigLoader
from notification_tracker import NotificationTracker

# Import V2 workflow as base
from certification_workflow_v2 import CertificationWorkflowV2

logger = logging.getLogger(__name__)


class CertificationWorkflowV3(CertificationWorkflowV2):
    """
    Enhanced workflow with duplicate notification prevention.
    
    Inherits all features from V2 and adds:
    - Notification tracking
    - Duplicate prevention
    - History management
    """
    
    def __init__(self, config: ConfigLoader, base_dir: Path = None):
        """
        Initialize workflow with configuration and notification tracker.
        
        Args:
            config: ConfigLoader instance
            base_dir: Base directory for relative paths
        """
        # Initialize parent class
        super().__init__(config, base_dir)
        
        # Initialize notification tracker
        tracker_file = self.output_dir / "notification_history.json"
        self.tracker = NotificationTracker(str(tracker_file))
        
        logger.info("Workflow V3 initialized with duplicate prevention")
    
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
    
    def record_sent_notifications(self):
        """Record all sent notifications in the tracker."""
        if not self.notifications:
            logger.warning("No notifications to record")
            return True
        
        logger.info("Recording sent notifications to prevent duplicates")
        
        try:
            recorded_count = 0
            duplicate_count = 0
            
            for notification in self.notifications:
                email = notification['email']
                
                # Get certifications for this email from matched_data
                email_certs = self.matched_data[
                    self.matched_data['Internet Email'].str.lower() == email.lower()
                ]
                
                # Record each certification
                for _, cert in email_certs.iterrows():
                    success = self.tracker.record_notification(
                        email=email,
                        credential_title=cert.get('Credential Title', ''),
                        credential_award_date=cert.get('Credential Award Date', ''),
                        credential_expiry_date=cert.get('Credential Expiry Date', ''),
                        vendor=cert.get('Vendor', '')
                    )
                    
                    if success:
                        recorded_count += 1
                    else:
                        duplicate_count += 1
            
            logger.info(f"Recorded {recorded_count} notifications")
            if duplicate_count > 0:
                logger.warning(f"Detected {duplicate_count} duplicates during recording")
            
            self.metrics['notifications_recorded'] = recorded_count
            
            return True
            
        except Exception as e:
            logger.error(f"Error recording notifications: {e}")
            raise
    
    def generate_tracking_report(self) -> Path:
        """Generate notification tracking report."""
        logger.info("Generating notification tracking report")
        
        try:
            # Generate report
            report_content = self.tracker.generate_report()
            
            # Save to file
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
    
    def run(self) -> Dict[str, Any]:
        """Execute the complete workflow with duplicate prevention."""
        logger.info("=" * 100)
        logger.info("STARTING CERTIFICATION WORKFLOW V3.0 (WITH DUPLICATE PREVENTION)")
        logger.info("=" * 100)
        
        results = {
            'success': False,
            'errors': []
        }
        
        try:
            # Steps 1-5: Same as V2 (load, filter, match, consolidate)
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
            
            # NEW STEP: Filter for new certifications only
            logger.info("\n" + "=" * 100)
            logger.info("STEP 6: Filtering new certifications (duplicate prevention)")
            logger.info("=" * 100)
            self.filter_new_certifications()
            
            # Check if there are any new certifications
            if self.matched_data is None or len(self.matched_data) == 0:
                logger.warning("No new certifications to process")
                logger.info("All certifications have already been notified")
                
                # Still generate tracking report
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
            logger.info("STEP 9: Saving notifications")
            logger.info("=" * 100)
            self.save_notifications_to_file()
            
            # NEW STEP: Record sent notifications
            logger.info("\n" + "=" * 100)
            logger.info("STEP 10: Recording sent notifications")
            logger.info("=" * 100)
            self.record_sent_notifications()
            
            # NEW STEP: Generate tracking report
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
        workflow = CertificationWorkflowV3(config, base_dir)
        
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
        print(f"Initial matched records: {results.get('initial_matched_records', 0)}")
        print(f"New certifications: {results.get('new_certifications', 0)}")
        print(f"Duplicate certifications (skipped): {results.get('duplicate_certifications', 0)}")
        print(f"Unique emails: {results.get('unique_emails', 0)}")
        print(f"Notifications generated: {results.get('notifications_generated', 0)}")
        print(f"Notifications recorded: {results.get('notifications_recorded', 0)}")
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
