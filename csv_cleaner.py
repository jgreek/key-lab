import csv
import logging
from datetime import datetime
from pathlib import Path


class CSVCleaner:
    def __init__(self, csv_logger, config_manager):
        self.csv_logger = csv_logger
        self.config_manager = config_manager
    
    def get_valid_commands(self):
        """Get all valid commands from both apps and commands sections"""
        valid_commands = set()
        valid_commands.update(self.config_manager.get_apps().keys())
        valid_commands.update(self.config_manager.get_commands().keys())
        return valid_commands
    
    def cleanup_outdated_entries(self):
        """Remove outdated entries from the CSV file that are no longer in config"""
        if not self.csv_logger.csv_log_path.exists():
            return
        
        try:
            valid_commands = self.get_valid_commands()
            rows_to_keep = []
            removed_entries = []
            
            # Read existing CSV data
            with open(self.csv_logger.csv_log_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                fieldnames = reader.fieldnames
                
                for row in reader:
                    command_code = row['code']
                    if command_code in valid_commands:
                        rows_to_keep.append(row)
                    else:
                        removed_entries.append(command_code)
            
            # Write back only valid commands if any were removed
            if removed_entries:
                with open(self.csv_logger.csv_log_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(rows_to_keep)
                
                # Update the csv_logger's action_counts to reflect the cleanup
                self.csv_logger.load_action_counts()
                
                print(f"[{datetime.now().strftime('%Y-%m-%d %I:%M %p')}] CSV cleaned up: removed {len(removed_entries)} outdated entries")
                logging.info(f"Removed outdated CSV entries: {', '.join(removed_entries)}")
                
                return removed_entries
            else:
                logging.info("CSV file is already clean - no outdated entries found")
                return []
                
        except Exception as e:
            logging.error(f"Error cleaning up CSV file: {e}")
            return []
    
    def get_outdated_entries(self):
        """Get list of outdated entries without removing them (for preview)"""
        if not self.csv_logger.csv_log_path.exists():
            return []
        
        try:
            valid_commands = self.get_valid_commands()
            outdated_entries = []
            
            with open(self.csv_logger.csv_log_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    command_code = row['code']
                    if command_code not in valid_commands:
                        outdated_entries.append({
                            'code': command_code,
                            'count': row.get('count', 0),
                            'last_action': row.get('last_action', ''),
                            'comment': row.get('comment', '')
                        })
            
            return outdated_entries
            
        except Exception as e:
            logging.error(f"Error checking for outdated entries: {e}")
            return []
    
    def preview_cleanup(self):
        """Preview what entries would be removed without actually removing them"""
        outdated = self.get_outdated_entries()
        if outdated:
            print(f"Found {len(outdated)} outdated entries that would be removed:")
            for entry in outdated:
                print(f"  - {entry['code']}: {entry['comment']} (used {entry['count']} times)")
        else:
            print("No outdated entries found - CSV file is clean")
        return outdated 