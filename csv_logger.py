import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import logging


class CSVLogger:
    def __init__(self, csv_path):
        self.csv_log_path = Path(csv_path)
        self.action_counts = defaultdict(int)
        self.init_csv_log()
        self.load_action_counts()

    def init_csv_log(self):
        if not self.csv_log_path.exists():
            with open(self.csv_log_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['code', 'count', 'last_action', 'comment'])
            print(f"Created CSV log file at {self.csv_log_path}")

    def safe_int(self, value, default=0):
        """Safely convert a value to int, returning default if conversion fails"""
        try:
            if value and str(value).strip():
                return int(value)
            return default
        except (ValueError, TypeError):
            return default

    def load_action_counts(self):
        counts = defaultdict(int)
        if self.csv_log_path.exists():
            try:
                with open(self.csv_log_path, 'r', newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        if row['code']:
                            # Use safe_int to handle empty or invalid count values
                            counts[row['code']] = self.safe_int(row.get('count', 0))
            except Exception as e:
                logging.error(f"Error loading action counts: {e}")
        self.action_counts = counts

    def log_action(self, code, comment=""):
        try:
            self.action_counts[code] += 1
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            existing_data = {}
            if self.csv_log_path.exists():
                with open(self.csv_log_path, 'r', newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        if row['code']:
                            existing_data[row['code']] = row

            existing_data[code] = {
                'code': code,
                'count': str(self.action_counts[code]),
                'last_action': current_time,
                'comment': comment
            }

            with open(self.csv_log_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=['code', 'count', 'last_action', 'comment'])
                writer.writeheader()
                for code_key in sorted(existing_data.keys()):
                    writer.writerow(existing_data[code_key])

            logging.info(f"Logged action: {code} (count: {self.action_counts[code]})")

        except Exception as e:
            logging.error(f"Error logging action to CSV: {e}")

    def get_action_count(self, code):
        return self.action_counts.get(code, 0)

    def get_stats(self):
        if not self.csv_log_path.exists():
            return []

        try:
            with open(self.csv_log_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                actions = list(reader)

            # Use safe_int for sorting to handle empty or invalid count values
            actions.sort(key=lambda x: self.safe_int(x.get('count')), reverse=True)
            return actions
        except Exception as e:
            logging.error(f"Error reading CSV stats: {e}")
            return []