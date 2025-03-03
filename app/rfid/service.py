from mfrc522 import SimpleMFRC522
from rpi_lcd import LCD
import RPi.GPIO as GPIO
import time
from datetime import datetime
import unicodedata
from app.common.logger import get_logger
from app.common.db import Database
from app.models.rfid_card import RFIDCard
from app.models.rfid_record import RFIDRecord
from app.analytics.report_generator import ReportGenerator
from app.analytics.email_notifier import EmailNotifier

logger = get_logger(__name__)

class MFRC522Service:
    def __init__(self):
        try:
            # Initialize RFID reader
            self.reader = SimpleMFRC522()
            
            # Initialize LCD
            self.lcd = LCD()
            
            # Initialize LED
            self.led_pin = 18
            GPIO.setup(self.led_pin, GPIO.OUT, initial=GPIO.LOW)
            
            # Initialize database
            self.db = Database()
            self.last_readings = {}
            self.report_generator = ReportGenerator()
            self.email_notifier = EmailNotifier()
            
            # Initial LCD message
            self.lcd.text("Ready to scan", 1)
            self.lcd.text("cards...", 2)
            
            logger.info("MFRC522 service initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing MFRC522 service: {str(e)}")
            self.cleanup()
            raise

    def normalize_text(self, text):
        """Normalize text to ASCII-compatible format"""
        try:
            # Replace Turkish characters with ASCII equivalents
            replacements = {
                'ı': 'i', 'İ': 'I',
                'ğ': 'g', 'Ğ': 'G',
                'ü': 'u', 'Ü': 'U',
                'ş': 's', 'Ş': 'S',
                'ö': 'o', 'Ö': 'O',
                'ç': 'c', 'Ç': 'C',
                'â': 'a', 'Â': 'A',
                'î': 'i', 'Î': 'I',
                'û': 'u', 'Û': 'U'
            }
            
            # First replace known Turkish characters
            for old, new in replacements.items():
                text = text.replace(old, new)
            
            # Then normalize remaining non-ASCII characters
            normalized = unicodedata.normalize('NFKD', text)
            ascii_text = normalized.encode('ascii', 'ignore').decode('ascii')
            
            return ascii_text.strip()
            
        except Exception as e:
            logger.error(f"Error normalizing text: {str(e)}")
            return text.encode('ascii', 'ignore').decode('ascii').strip()

    def write_card(self, name, is_admin=False):
        """Write data to a new RFID card"""
        try:
            # Generate unique card ID
            card_id = str(int(time.time()))
            data = f"{name},{card_id},{'A' if is_admin else 'U'}"
            
            # Show instruction
            self.lcd.text("Place card to", 1)
            self.lcd.text("write...", 2)
            
            # Write to card with timeout
            start_time = time.time()
            while time.time() - start_time < 10:  # 10 second timeout
                try:
                    self.reader.write(data)
                    break
                except Exception as e:
                    if time.time() - start_time >= 10:
                        raise TimeoutError("Card write timeout")
                    time.sleep(0.1)
                    continue
            
            # Save to database
            card = RFIDCard(
                card_id=card_id,
                name=name,
                is_admin=is_admin,
                created_at=datetime.now()
            )
            self.db.save(card)
            
            # Success feedback
            GPIO.output(self.led_pin, GPIO.HIGH)
            self.lcd.text("Card written", 1)
            self.lcd.text("successfully!", 2)
            time.sleep(0.5)
            GPIO.output(self.led_pin, GPIO.LOW)
            
            logger.info(f"Written new card for {name} (Admin: {is_admin})")
            return card_id
            
        except Exception as e:
            logger.error(f"Error writing card: {str(e)}")
            self.lcd.text("Error writing", 1)
            self.lcd.text("card!", 2)
            time.sleep(0.5)
            raise
        finally:
            self.lcd.text("Ready to scan", 1)
            self.lcd.text("cards...", 2)

    def read_card(self):
        """Read RFID card"""
        try:
            # Use blocking read first to ensure card detection works
            id, text = self.reader.read()
            if not text or not text.strip():
                return None

            # Parse card data
            try:
                name, card_id, status = text.strip().split(',')
                is_admin = (status == 'A')
            except ValueError:
                logger.error(f"Invalid card data format: {text}")
                return None

            # Check for duplicate reads
            timestamp = datetime.now()
            last_reading = self.last_readings.get(card_id)
            if last_reading:
                time_diff = (timestamp - last_reading['timestamp']).total_seconds()
                if time_diff < 3:  # 3-second cooldown
                    return None
                is_entry = not last_reading.get('is_entry', True)
            else:
                is_entry = True

            # Visual feedback
            GPIO.output(self.led_pin, GPIO.HIGH)
            self.lcd.text(f"{'Welcome' if is_entry else 'Goodbye'}", 1)
            self.lcd.text(f"{name}", 2)

            # Save to database
            try:
                record = RFIDRecord(
                    card_id=card_id,
                    name=name,
                    timestamp=timestamp,
                    is_entry=is_entry
                )
                self.db.save(record)
            except Exception as e:
                logger.error(f"Database error: {str(e)}")

            # Update last reading
            self.last_readings[card_id] = {
                'timestamp': timestamp,
                'is_entry': is_entry
            }

            # Log the action
            action = "entered" if is_entry else "exited"
            logger.info(f"Card {card_id} ({name}) {action}")
            print(f"\n{name} has {action}")

            # If admin card, generate and send report
            if is_admin and is_entry:  # Only generate report on admin entry
                try:
                    report = self.report_generator.generate_daily_report()
                    self.email_notifier.send_report(report)
                    
                    # Show report status on LCD
                    time.sleep(1)  # Brief pause before showing report status
                    self.lcd.text("Generating", 1)
                    self.lcd.text("report...", 2)
                    time.sleep(2)
                    
                    self.lcd.text("Report sent", 1)
                    self.lcd.text("successfully!", 2)
                    time.sleep(2)
                    
                    logger.info(f"Admin {name} triggered report generation")
                except Exception as e:
                    logger.error(f"Error generating admin report: {str(e)}")
                    self.lcd.text("Report error!", 1)
                    self.lcd.text("Try again later", 2)
                    time.sleep(2)

            else:
                # Keep welcome/goodbye message for 3 seconds for non-admin cards
                time.sleep(3)

            # Reset visual feedback
            GPIO.output(self.led_pin, GPIO.LOW)
            self.lcd.text("Ready to scan", 1)
            self.lcd.text("cards...", 2)

            return card_id

        except Exception as e:
            logger.error(f"Error reading card: {str(e)}")
            self.lcd.text("Error reading", 1)
            self.lcd.text("card!", 2)
            time.sleep(3)  # Show error message for 3 seconds
            self.lcd.text("Ready to scan", 1)
            self.lcd.text("cards...", 2)
            return None

    def flash_led(self, duration=0.1):
        """Flash LED for visual feedback"""
        try:
            GPIO.output(self.led_pin, GPIO.HIGH)
            time.sleep(duration)
            GPIO.output(self.led_pin, GPIO.LOW)
        except Exception as e:
            logger.error(f"Error flashing LED: {str(e)}")

    def generate_admin_report(self):
        """Generate and send report for admin"""
        try:
            report = self.report_generator.generate_daily_report()
            self.email_notifier.send_report(report)
            
            self.lcd.text("Report sent", 1)
            self.lcd.text("successfully!", 2)
            time.sleep(2)
            
            logger.info("Admin report generated and sent")
        except Exception as e:
            logger.error(f"Error generating admin report: {str(e)}")
            self.lcd.text("Report error!", 1)
            
            time.sleep(2)

    def cleanup(self):
        """Clean up resources"""
        try:
            GPIO.output(self.led_pin, GPIO.LOW)
            GPIO.cleanup()
            self.lcd.clear()
            logger.info("MFRC522 service cleaned up")
        except Exception as e:
            logger.error(f"Error in cleanup: {str(e)}")
