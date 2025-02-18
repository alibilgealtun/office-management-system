import openai
from app.common.logger import get_logger
from app.config import OPENAI_API_KEY
from openai import OpenAI
import datetime

logger = get_logger(__name__)

class ChatGPTClient:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("ChatGPT client initialized")

    def analyze_usage_patterns(self, data):
        """Sends data to OpenAI ChatGPT for analysis"""
        try:
            prompt = self._format_data_for_analysis(data)

            response = self.client.chat.completions.create(  # New API method
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert data assistant. Prepare a report for how the office was used today, generate highlights and stuff. Do not include any unnecessary details. Make it like a professional 'daily office usage' report. GENERATE YOUR MESSAGE IN HTML FORMAT"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )

            analysis = response.choices[0].message.content  # Updated response handling
            return self._format_analysis_response(analysis)

        except Exception as e:
            logger.error(f"Error analyzing data with ChatGPT: {str(e)}")
            raise

    def _format_data_for_analysis(self, data):
        """Formats the data into a prompt for ChatGPT"""
        try:
            # Extract correct parts
            image_data = data.get("image_data", {}).get("detailed_records", [])
            rfid_data = data.get("rfid_data", {}).get("detailed_records", [])

            if not isinstance(image_data, list) or not isinstance(rfid_data, list):
                raise ValueError(f"Invalid data format! image_data={type(image_data)}, rfid_data={type(rfid_data)}")

            prompt = "Please analyze the following facility usage data:\n\n"

            # Format image processing data
            prompt += "Image Processing Data:\n"
            for record in image_data:
                if not isinstance(record, dict):  # Ensure it's a dictionary
                    raise ValueError(f"Expected dict in image_data but got {type(record)}: {record}")
                prompt += f"- Timestamp: {record['timestamp']}, Persons detected: {record['person_count']}\n"

            # Format RFID data
            prompt += "\nRFID Access Data:\n"
            for record in rfid_data:
                if not isinstance(record, dict):  # Ensure it's a dictionary
                    raise ValueError(f"Expected dict in rfid_data but got {type(record)}: {record}")
                event_type = "entry" if record["is_entry"] else "exit"
                prompt += f"- Card ID: {record['card_id']}, {event_type} at {record['timestamp']}\n"

            prompt += "\nPlease provide a detailed analysis of usage patterns, trends, and any notable observations."
            return prompt

        except Exception as e:
            logger.error(f"Error formatting data for analysis: {str(e)}")
            raise

    def _format_analysis_response(self, analysis):
        """Formats the ChatGPT response into a structured format"""
        try:
            return {
                'analysis': analysis,
                'timestamp': datetime.datetime.now().isoformat(),
                'version': 'gpt-3.5-turbo', 
                'type': 'daily_analysis'
            }
        except Exception as e:
            logger.error(f"Error formatting analysis response: {str(e)}")
            raise 