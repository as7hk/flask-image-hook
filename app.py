import os
import requests
from flask import Flask, request
from datetime import datetime
import mimetypes
import logging

app = Flask(__name__)

# تنظیم لاگ‌گیری
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# پوشه‌ای برای ذخیره عکس‌ها
DOWNLOAD_FOLDER = 'downloaded_images'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# حداکثر اندازه فایل (مثلا 10 مگابایت)
MAX_CONTENT_LENGTH = 10 * 1024 * 1024

@app.route('/flask-image-hook-2', methods=['POST'])
def twitter_hook():
    data = request.get_json(silent=True)

    if not data:
        logger.error("No JSON received")
        return "❌ No JSON received", 400

    image_url = data.get('image_url')
    if not image_url or not image_url.startswith(('http://', 'https://')):
        logger.error("Invalid or missing image_url")
        return "❗ Invalid or missing image_url", 400

    try:
        response = requests.get(image_url, stream=True, timeout=10)
        if response.status_code != 200:
            logger.error(f"Failed to download image: {response.status_code}")
            return f"⚠️ Failed to download image: {response.status_code}", 400

        # بررسی نوع محتوا
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            logger.error(f"URL does not point to an image: {content_type}")
            return "❗ URL does not point to an image", 400

        # بررسی اندازه محتوا
        content_length = int(response.headers.get('content-length', 0))
        if content_length > MAX_CONTENT_LENGTH:
            logger.error(f"Image too large: {content_length} bytes")
            return "❗ Image too large", 400

        # استخراج پسوند فایل از نوع محتوا
        extension = mimetypes.guess_extension(content_type) or '.jpg'
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"image_{timestamp}{extension}"
        path = os.path.join(DOWNLOAD_FOLDER, filename)

        # ذخیره تصویر
        with open(path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        logger.info(f"Image saved to: {path}")
        return f"Image saved as {filename}", 200

    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading image: {str(e)}")
        return f"Error downloading image: {str(e)}", 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return f"Unexpected error: {str(e)}", 500

# این بخش برای اجرای مستقیم فایل است
if __name__ == '__main__':
    app.run(debug=True)
