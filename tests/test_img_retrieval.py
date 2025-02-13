import unittest
import cv2
import numpy as np
from sqlalchemy.orm import sessionmaker
from app.common.db import Database
from app.models.image_record import ImageRecord

class TestImageRetrieval(unittest.TestCase):
    def setUp(self):
        """Set up the database connection."""
        self.db = Database()
        self.session = self.db.Session()

    def retrieve_image(self, image_id=None):
        """Retrieve an image by ID or get the latest if no ID is provided."""
        query = self.session.query(ImageRecord)

        if image_id:
            query = query.filter(ImageRecord.id == image_id)
        else:
            query = query.order_by(ImageRecord.id.desc())

        result = query.first()
        return result

    def test_retrieve_specific_image(self):
        """Test if a specific image can be retrieved by ID."""
        image_id = 754 # change it according to img you want to retrieve
        result = self.retrieve_image(image_id)

        self.assertIsNotNone(result, f"No image found with ID {image_id}.")
        image_data = result.image_data
        
        # Convert binary data to a NumPy array
        image_array = np.frombuffer(image_data, dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        self.assertIsNotNone(image, "Failed to decode the image.")
        
        # Display the image (Optional)
        cv2.imshow(f"Image ID: {image_id}", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def test_retrieve_latest_image(self):
        """Test if the latest image can be retrieved."""
        result = self.retrieve_image()  # No ID, so fetch latest
        
        self.assertIsNotNone(result, "No image found in the database.")
        image_data = result.image_data
        
        # Convert binary data to a NumPy array
        image_array = np.frombuffer(image_data, dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        self.assertIsNotNone(image, "Failed to decode the image.")
        
        # Display the image (Optional)
        cv2.imshow("Latest Image", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def tearDown(self):
        """Close database connection."""
        self.session.close()

if __name__ == "__main__":
    unittest.main()