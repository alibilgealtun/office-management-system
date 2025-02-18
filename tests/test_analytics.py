import unittest
from unittest.mock import Mock, patch
import datetime
from app.analytics.chatgpt_client import ChatGPTClient
from app.analytics.report_generator import ReportGenerator
from app.analytics.email_notifier import EmailNotifier
from app.models.image_record import ImageRecord
from app.models.rfid_record import RFIDRecord

class TestAnalytics(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.mock_db = Mock()
        self.mock_session = Mock()
        self.mock_db.Session.return_value = self.mock_session

    def test_chatgpt_client_analysis(self):
        """Test ChatGPT client's analysis functionality"""
        with patch('openai.ChatCompletion.create') as mock_openai:
            # Setup mock response
            mock_openai.return_value.choices = [
                Mock(message=Mock(content="Test analysis content"))
            ]
            
            client = ChatGPTClient()
            
            # Test data
            test_data = {
                'image_data': [
                    {
                        'timestamp': '2024-02-13T14:00:00',
                        'person_count': 5
                    }
                ],
                'rfid_data': [
                    {
                        'timestamp': '2024-02-13T14:00:00',
                        'card_id': '12345',
                        'is_entry': True
                    }
                ]
            }
            
            # Test analysis
            result = client.analyze_usage_patterns(test_data)
            
            # Assertions
            self.assertIn('analysis', result)
            self.assertIn('timestamp', result)
            self.assertIn('version', result)
            self.assertEqual(result['type'], 'daily_analysis')
            
            # Verify OpenAI API was called correctly
            mock_openai.assert_called_once()
            call_args = mock_openai.call_args[1]
            self.assertEqual(call_args['model'], 'gpt-3.5-turbo')
            self.assertEqual(call_args['temperature'], 0.3)

    def test_report_generator(self):
        """Test report generator functionality"""
        # Create mock data
        mock_image_records = [
            Mock(
                timestamp=datetime.datetime(2024, 2, 13, 14, 0),
                person_count=5,
                id=1
            ),
            Mock(
                timestamp=datetime.datetime(2024, 2, 13, 15, 0),
                person_count=3,
                id=2
            )
        ]
        
        mock_rfid_records = [
            Mock(
                timestamp=datetime.datetime(2024, 2, 13, 14, 0),
                card_id='12345',
                is_entry=True,
                id=1
            ),
            Mock(
                timestamp=datetime.datetime(2024, 2, 13, 15, 0),
                card_id='12345',
                is_entry=False,
                id=2
            )
        ]
        
        # Setup mock query results
        self.mock_session.query.return_value.filter.return_value.order_by.return_value.all.side_effect = [
            mock_image_records,
            mock_rfid_records
        ]
        
        # Create ReportGenerator with mock database
        generator = ReportGenerator()
        generator.db = self.mock_db
        
        # Test image data retrieval
        image_data = generator._get_image_data(datetime.date(2024, 2, 13))
        self.assertEqual(image_data['total_detections'], 2)
        self.assertEqual(image_data['total_persons'], 8)
        self.assertEqual(image_data['average_persons'], 4.0)
        
        # Test RFID data retrieval
        rfid_data = generator._get_rfid_data(datetime.date(2024, 2, 13))
        self.assertEqual(rfid_data['total_events'], 2)
        self.assertEqual(rfid_data['unique_cards'], 1)
        self.assertEqual(rfid_data['total_entries'], 1)
        self.assertEqual(rfid_data['total_exits'], 1)

    @patch('smtplib.SMTP')
    def test_email_notifier(self, mock_smtp):
        """Test email notification functionality"""
        notifier = EmailNotifier()
        test_report = "Test Report Content"
        
        # Test sending email
        notifier.send_report(test_report)
        
        # Verify SMTP interactions
        mock_smtp.assert_called_once()
        mock_smtp.return_value.__enter__.return_value.starttls.assert_called_once()
        mock_smtp.return_value.__enter__.return_value.login.assert_called_once()
        mock_smtp.return_value.__enter__.return_value.send_message.assert_called_once()

    @patch('app.analytics.scheduler.BackgroundScheduler')
    def test_scheduler(self, mock_scheduler):
        """Test scheduler setup and job creation"""
        from app.analytics.scheduler import setup_scheduler
        
        # Test scheduler initialization
        scheduler = setup_scheduler()
        
        # Verify scheduler was created
        mock_scheduler.assert_called_once()
        
        # Verify job was added
        mock_scheduler.return_value.add_job.assert_called()
        
        # Verify correct job parameters
        call_args = mock_scheduler.return_value.add_job.call_args[1]
        self.assertEqual(call_args['id'], 'daily_report_job')

    def test_full_analytics_pipeline(self):
        """Test the entire analytics pipeline integration"""
        with patch('openai.ChatCompletion.create') as mock_openai, \
             patch('smtplib.SMTP') as mock_smtp:
            
            # Setup mock OpenAI response
            mock_openai.return_value.choices = [
                Mock(message=Mock(content="Test analysis content"))
            ]
            
            # Setup mock database records
            mock_records = [
                Mock(
                    timestamp=datetime.datetime.now(),
                    person_count=5,
                    id=1
                )
            ]
            self.mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = mock_records
            
            # Create and test ReportGenerator
            generator = ReportGenerator()
            generator.db = self.mock_db
            
            # Generate and send report
            report = generator.generate_daily_report()
            
            # Verify report was generated
            self.assertIsNotNone(report)
            self.assertIsInstance(report, str)
            
            # Send email
            notifier = EmailNotifier()
            notifier.send_report(report)
            
            # Verify email was sent
            mock_smtp.assert_called_once()

def run_tests():
    unittest.main()

if __name__ == '__main__':
    run_tests() 