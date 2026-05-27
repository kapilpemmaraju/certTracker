"""
Notification Tracker - Prevents Duplicate Notifications
========================================================

This module tracks sent notifications to prevent sending duplicate
notifications for the same credential to the same resource.

Features:
- Tracks sent notifications by email + credential title
- Persistent storage (JSON file)
- Duplicate detection
- History management
- Reporting

Author: IBM BOB
Date: 2026-05-21
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Optional
import logging

logger = logging.getLogger(__name__)


class NotificationTracker:
    """Track sent notifications to prevent duplicates."""
    
    def __init__(self, tracking_file: str = "notification_history.json"):
        """
        Initialize notification tracker.
        
        Args:
            tracking_file: Path to JSON file for storing notification history
        """
        self.tracking_file = Path(tracking_file)
        self.history = self._load_history()
        logger.info(f"Notification tracker initialized: {self.tracking_file}")
    
    def _load_history(self) -> Dict:
        """Load notification history from file."""
        if self.tracking_file.exists():
            try:
                with open(self.tracking_file, 'r') as f:
                    history = json.load(f)
                logger.info(f"Loaded {len(history.get('notifications', []))} notification records")
                return history
            except Exception as e:
                logger.error(f"Error loading history: {e}")
                return {"notifications": [], "metadata": {}}
        
        return {"notifications": [], "metadata": {}}
    
    def _save_history(self):
        """Save notification history to file."""
        try:
            # Update metadata
            self.history["metadata"] = {
                "last_updated": datetime.now().isoformat(),
                "total_notifications": len(self.history["notifications"])
            }
            
            with open(self.tracking_file, 'w') as f:
                json.dump(self.history, f, indent=2)
            
            logger.info(f"Saved notification history: {len(self.history['notifications'])} records")
        except Exception as e:
            logger.error(f"Error saving history: {e}")
    
    def _generate_notification_id(self, email: str, credential_title: str) -> str:
        """
        Generate unique ID for email + credential combination.
        
        Args:
            email: Resource email address
            credential_title: Credential title
            
        Returns:
            Unique hash ID
        """
        # Normalize inputs
        email_normalized = email.strip().lower()
        credential_normalized = credential_title.strip().lower()
        
        # Create unique identifier
        identifier = f"{email_normalized}|{credential_normalized}"
        
        # Generate hash
        return hashlib.sha256(identifier.encode()).hexdigest()
    
    def has_been_notified(self, email: str, credential_title: str) -> bool:
        """
        Check if notification has already been sent.
        
        Args:
            email: Resource email address
            credential_title: Credential title
            
        Returns:
            True if notification already sent, False otherwise
        """
        notification_id = self._generate_notification_id(email, credential_title)
        
        # Check if ID exists in history
        for record in self.history["notifications"]:
            if record.get("notification_id") == notification_id:
                logger.info(f"Duplicate detected: {email} - {credential_title}")
                return True
        
        return False
    
    def record_notification(self, email: str, credential_title: str, 
                          credential_award_date: str = None,
                          credential_expiry_date: str = None,
                          vendor: str = None) -> bool:
        """
        Record a sent notification.
        
        Args:
            email: Resource email address
            credential_title: Credential title
            credential_award_date: Award date (optional)
            credential_expiry_date: Expiry date (optional)
            vendor: Vendor name (optional)
            
        Returns:
            True if recorded successfully, False if duplicate
        """
        # Check for duplicate
        if self.has_been_notified(email, credential_title):
            logger.warning(f"Attempted duplicate notification: {email} - {credential_title}")
            return False
        
        # Create notification record
        notification_id = self._generate_notification_id(email, credential_title)
        
        record = {
            "notification_id": notification_id,
            "email": email.strip().lower(),
            "credential_title": credential_title.strip(),
            "vendor": vendor,
            "credential_award_date": credential_award_date,
            "credential_expiry_date": credential_expiry_date,
            "sent_timestamp": datetime.now().isoformat(),
            "sent_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Add to history
        self.history["notifications"].append(record)
        
        # Save to file
        self._save_history()
        
        logger.info(f"Recorded notification: {email} - {credential_title}")
        return True
    
    def get_notifications_for_email(self, email: str) -> List[Dict]:
        """
        Get all notifications sent to a specific email.
        
        Args:
            email: Resource email address
            
        Returns:
            List of notification records
        """
        email_normalized = email.strip().lower()
        return [
            record for record in self.history["notifications"]
            if record.get("email") == email_normalized
        ]
    
    def get_notifications_for_credential(self, credential_title: str) -> List[Dict]:
        """
        Get all notifications for a specific credential.
        
        Args:
            credential_title: Credential title
            
        Returns:
            List of notification records
        """
        credential_normalized = credential_title.strip().lower()
        return [
            record for record in self.history["notifications"]
            if record.get("credential_title", "").lower() == credential_normalized
        ]
    
    def get_new_certifications(self, certifications: List[Dict]) -> List[Dict]:
        """
        Filter certifications to only include those not yet notified.
        
        Args:
            certifications: List of certification dictionaries with 'Internet Email' and 'Credential Title'
            
        Returns:
            List of certifications that haven't been notified
        """
        new_certifications = []
        
        for cert in certifications:
            email = cert.get('Internet Email', '')
            credential_title = cert.get('Credential Title', '')
            
            if not self.has_been_notified(email, credential_title):
                new_certifications.append(cert)
        
        logger.info(f"Filtered {len(certifications)} certifications to {len(new_certifications)} new ones")
        return new_certifications
    
    def get_statistics(self) -> Dict:
        """
        Get notification statistics.
        
        Returns:
            Dictionary with statistics
        """
        notifications = self.history["notifications"]
        
        if not notifications:
            return {
                "total_notifications": 0,
                "unique_emails": 0,
                "unique_credentials": 0,
                "date_range": None
            }
        
        # Calculate statistics
        unique_emails = len(set(n["email"] for n in notifications))
        unique_credentials = len(set(n["credential_title"] for n in notifications))
        
        dates = [n["sent_date"] for n in notifications if "sent_date" in n]
        date_range = f"{min(dates)} to {max(dates)}" if dates else None
        
        return {
            "total_notifications": len(notifications),
            "unique_emails": unique_emails,
            "unique_credentials": unique_credentials,
            "date_range": date_range,
            "last_notification": notifications[-1]["sent_timestamp"] if notifications else None
        }
    
    def generate_report(self) -> str:
        """
        Generate a text report of notification history.
        
        Returns:
            Formatted report string
        """
        stats = self.get_statistics()
        
        report = f"""
{'=' * 80}
NOTIFICATION HISTORY REPORT
{'=' * 80}

STATISTICS:
-----------
Total Notifications Sent:    {stats['total_notifications']}
Unique Email Addresses:       {stats['unique_emails']}
Unique Credentials:           {stats['unique_credentials']}
Date Range:                   {stats['date_range'] or 'N/A'}
Last Notification:            {stats['last_notification'] or 'N/A'}

RECENT NOTIFICATIONS (Last 10):
--------------------------------
"""
        
        # Add recent notifications
        recent = self.history["notifications"][-10:]
        for i, record in enumerate(reversed(recent), 1):
            report += f"""
{i}. {record['email']}
   Credential: {record['credential_title']}
   Vendor: {record.get('vendor', 'N/A')}
   Sent: {record['sent_timestamp']}
"""
        
        report += f"\n{'=' * 80}\n"
        return report
    
    def clear_history(self, confirm: bool = False):
        """
        Clear all notification history.
        
        Args:
            confirm: Must be True to actually clear
        """
        if not confirm:
            logger.warning("Clear history called without confirmation")
            return False
        
        self.history = {"notifications": [], "metadata": {}}
        self._save_history()
        logger.info("Notification history cleared")
        return True
    
    def export_to_csv(self, output_file: str):
        """
        Export notification history to CSV.
        
        Args:
            output_file: Path to output CSV file
        """
        import csv
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                if not self.history["notifications"]:
                    logger.warning("No notifications to export")
                    return
                
                # Get field names from first record
                fieldnames = list(self.history["notifications"][0].keys())
                
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.history["notifications"])
            
            logger.info(f"Exported {len(self.history['notifications'])} records to {output_file}")
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create tracker
    tracker = NotificationTracker()
    
    # Example: Check if notification already sent
    email = "john.doe@example.com"
    credential = "AWS Certified Solutions Architect"
    
    if not tracker.has_been_notified(email, credential):
        print(f"✅ Can send notification to {email} for {credential}")
        
        # Record the notification
        tracker.record_notification(
            email=email,
            credential_title=credential,
            vendor="AWS",
            credential_award_date="2026-05-21"
        )
    else:
        print(f"⚠️ Already notified {email} about {credential}")
    
    # Get statistics
    stats = tracker.get_statistics()
    print(f"\nStatistics: {stats}")
    
    # Generate report
    print(tracker.generate_report())

# Made with Bob
