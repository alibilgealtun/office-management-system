from datetime import datetime
import datetime as dt
from sqlalchemy import func, and_
from app.common.logger import get_logger
from app.common.db import Database
from app.models.image_record import ImageRecord
from app.models.rfid_record import RFIDRecord
from .chatgpt_client import ChatGPTClient

logger = get_logger(__name__)

class ReportGenerator:
    def __init__(self):
        self.db = Database()
        self.chatgpt = ChatGPTClient()
        logger.info("Report generator initialized")

    def generate_daily_report(self):
        """Generate daily report using ChatGPT"""
        try:
            # Get today's date
            today = datetime.now().date()
            
            # Get data from database
            image_data = self._get_image_data(today)
            rfid_data = self._get_rfid_data(today)
            
            data = {
                'image_data':image_data,
                'rfid_data':rfid_data
            }
            
            # Get HTML report from ChatGPT
            html_report = self.chatgpt.analyze_usage_patterns(data)
            
            logger.info("Daily report generated successfully via ChatGPT")
            return html_report

        except Exception as e:
            logger.error(f"Error generating daily report: {str(e)}")
            return self._generate_fallback_html_report(image_data, rfid_data)

    def _format_hourly_stats(self, hourly_stats):
        """Format hourly statistics for the prompt"""
        formatted = []
        for hour in range(24):
            if hour in hourly_stats:
                stats = hourly_stats[hour]
                formatted.append(
                    f"Hour {hour:02d}:00 - "
                    f"Entries: {stats['entries']}, "
                    f"Exits: {stats['exits']}"
                )
        return "\n".join(formatted)

    def _format_detailed_records(self, records):
        """Format detailed records for the prompt"""
        formatted = []
        for record in records:
            timestamp = datetime.fromisoformat(record['timestamp'])
            action = "entered" if record['is_entry'] else "exited"
            formatted.append(
                f"{timestamp.strftime('%H:%M:%S')} - "
                f"Card {record['card_id']} {action}"
            )
        return "\n".join(formatted)

    def _generate_fallback_html_report(self, image_data, rfid_data):
        """Generate a basic HTML report if ChatGPT fails"""
        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #333; }}
                .section {{ margin: 20px 0; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f5f5f5; }}
            </style>
        </head>
        <body>
            <h1>Security Report - {datetime.now().date()}</h1>
            
            <div class="section">
                <h2>Image Processing Statistics</h2>
                <p>Total Detections: {image_data['total_detections']}</p>
                <p>Total Persons: {image_data['total_persons']}</p>
                <p>Average Persons per Detection: {image_data['average_persons']:.2f}</p>
            </div>
            
            <div class="section">
                <h2>RFID Access Statistics</h2>
                <p>Total Events: {rfid_data['total_events']}</p>
                <p>Unique Cards: {rfid_data['unique_cards']}</p>
                <p>Total Entries: {rfid_data['total_entries']}</p>
                <p>Total Exits: {rfid_data['total_exits']}</p>
            </div>
        </body>
        </html>
        """

    def _get_image_data(self, date):
        """Retrieves image processing data for the given date"""
        try:
            # Create session
            session = self.db.Session()
            
            # Get start and end of the specified date
            start_date = datetime.combine(date, datetime.min.time())
            end_date = datetime.combine(date, datetime.max.time())
            
            # Query image records for the specified date
            records = session.query(ImageRecord).filter(
                and_(
                    ImageRecord.timestamp >= start_date,
                    ImageRecord.timestamp <= end_date
                )
            ).order_by(ImageRecord.timestamp).all()
            
            # Process the records
            image_data = []
            for record in records:
                image_data.append({
                    'timestamp': record.timestamp.isoformat(),
                    'person_count': record.person_count
                })
            
            # Calculate statistics
            total_detections = len(records)
            total_persons = sum(record.person_count for record in records)
            
            # Get hourly distribution
            hourly_stats = {}
            for record in records:
                hour = record.timestamp.hour
                if hour not in hourly_stats:
                    hourly_stats[hour] = {
                        'detections': 0,
                        'total_persons': 0,
                        'max_persons': 0
                    }
                hourly_stats[hour]['detections'] += 1
                hourly_stats[hour]['total_persons'] += record.person_count
                hourly_stats[hour]['max_persons'] = max(
                    hourly_stats[hour]['max_persons'],
                    record.person_count
                )
            
            return {
                'date': date.isoformat(),
                'total_detections': total_detections,
                'total_persons': total_persons,
                'average_persons': total_persons / total_detections if total_detections > 0 else 0,
                'hourly_stats': hourly_stats,
                'detailed_records': image_data
            }
            
        except Exception as e:
            logger.error(f"Error fetching image data: {str(e)}")
            raise
        finally:
            session.close()

    def _get_rfid_data(self, date):
        """Retrieves RFID data for the given date"""
        try:
            # Create session
            session = self.db.Session()
            
            # Get start and end of the specified date
            start_date = datetime.combine(date, datetime.min.time())
            end_date = datetime.combine(date, datetime.max.time())
            
            # Query RFID records for the specified date
            records = session.query(RFIDRecord).filter(
                and_(
                    RFIDRecord.timestamp >= start_date,
                    RFIDRecord.timestamp <= end_date
                )
            ).order_by(RFIDRecord.timestamp).all()
            
            # Process the records
            rfid_data = []
            unique_cards = set()
            entries = 0
            exits = 0
            
            for record in records:
                rfid_data.append({
                    'timestamp': record.timestamp.isoformat(),
                    'card_id': record.card_id,
                    'is_entry': record.is_entry
                })
                unique_cards.add(record.card_id)
                if record.is_entry:
                    entries += 1
                else:
                    exits += 1
            
            # Get hourly distribution
            hourly_stats = {}
            for record in records:
                hour = record.timestamp.hour
                if hour not in hourly_stats:
                    hourly_stats[hour] = {
                        'entries': 0,
                        'exits': 0,
                        'total_events': 0
                    }
                if record.is_entry:
                    hourly_stats[hour]['entries'] += 1
                else:
                    hourly_stats[hour]['exits'] += 1
                hourly_stats[hour]['total_events'] += 1
            
            return {
                'date': date.isoformat(),
                'total_events': len(records),
                'unique_cards': len(unique_cards),
                'total_entries': entries,
                'total_exits': exits,
                'hourly_stats': hourly_stats,
                'detailed_records': rfid_data
            }
            
        except Exception as e:
            logger.error(f"Error fetching RFID data: {str(e)}")
            raise
        finally:
            session.close()

    def _analyze_data(self, image_data, rfid_data):
        """Sends data to ChatGPT for analysis"""
        combined_data = {
            'image_data': image_data,
            'rfid_data': rfid_data
        }
        
        # Debugging: Print the data before sending it
        logger.info(f"Sending to ChatGPT: {combined_data}")

        return self.chatgpt.analyze_usage_patterns(combined_data)

    def _format_report(self, analysis):
        """Formats the analysis results into a readable report"""
        try:
            report = []
            

            
            return "\n".join(report)
            
        except Exception as e:
            logger.error(f"Error formatting report: {str(e)}")
            raise 