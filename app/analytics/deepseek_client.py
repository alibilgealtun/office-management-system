import requests
from app.common.logger import get_logger
from app.config import DEEPSEEK_API_URL, DEEPSEEK_API_KEY

logger = get_logger(__name__)

class DeepSeekClient:
    def __init__(self):
        self.api_url = DEEPSEEK_API_URL
        self.api_key = DEEPSEEK_API_KEY
        logger.info("DeepSeek client initialized")

    def analyze_usage_patterns(self, data):
        """Sends data to DeepSeek for analysis"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f"{self.api_url}/analyze",
                headers=headers,
                json=data
            )
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error analyzing data with DeepSeek: {str(e)}")
            raise 