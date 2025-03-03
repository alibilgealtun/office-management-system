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

            response = self.client.chat.completions.create( 
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert data assistant. Prepare a professional 'Daily Office Usage' report based on the provided data. The report should be structured in HTML format and include:"},
                    {"role": "system", "content": 
                        """
                        <h1>Daily Office Usage Report</h1>

                        <h2>Summary</h2>
                        <p>Provide a brief overview of today's office usage, including the total number of employees who entered and exited, peak hours, and any notable changes from the previous day.</p>

                        <h2>RFID Data</h2>
                        <ul>
                            <li>How many enterance is made to the office today?</li>
                            <li>Peak Activity Time</li>
                            <li>Low Activity Time</li>
                        </ul>
                        <h2>Image Processing Data</h2>
                        <ul>
                            <li>How many enterance is made to the office today?</li>
                            <li>Peak Activity Time</li>
                            <li>Low Activity Time</li>
                        </ul>
                        

                        <h2>Key Highlights</h2>
                        <ul>
                            <li>List the most important events, including attendance peaks, unusual office usage patterns, or key personnel movements.</li>
                            <li>Mention if any new employees or visitors were detected.</li>
                            <li>Highlight anything you find meaningful for a manager.</li>
                        </ul>
                        

                        <h2>Data Analysis & Trends</h2>
                        <p>Analyze the data to identify trends. Discuss whether office occupancy has increased or decreased compared to previous days. Mention any significant patterns such as extended stays, irregular entry/exit patterns, or clustering of personnel.</p>

                        <h2>Conclusion & Recommendations</h2>
                        <p>Provide a professional conclusion, summarizing insights gained from the data. Offer recommendations such as optimizing office usage hours, security improvements, or policy changes based on observed patterns.</p>

                        <p><i>This report is automatically generated using AI-based data analysis for Feriştah Dalkılıç.</i></p>
                        """
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )

            analysis = response.choices[0].message.content  # Updated response handling
            return analysis

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

    def generate_html_report(self, prompt):
        """Generate HTML report using ChatGPT"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a security report generator. Generate detailed HTML reports with professional styling."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating report with ChatGPT: {str(e)}")
            raise 