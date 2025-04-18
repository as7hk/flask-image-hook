import os
import requests
from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

# پوشه‌ای برای ذخیره عکس‌ها
DOWNLOAD_FOLDER = 'downloaded_images'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/flask-image-hook-2', methods=['POST'])
def twitter_hook():
    data = request.get_json(silent=True)

    if not data:
        return "❌ No JSON received", 400

    # فرض: لینک عکس توی کلید 'image_url'
    image_url = data.get('image_url')

    if not image_url:
        return "❗ No image_url found in JSON", 400

    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f"image_{timestamp}.jpg"
            path = os.path.join(DOWNLOAD_FOLDER, filename)
            with open(path, 'wb') as f:
                f.write(response.content)
            print(f"✅ Image saved to: {path}")
            return f"Image saved as {filename}", 200
        else:
            return f"⚠️ Failed to download image: {response.status_code}", 400
    except Exception as e:
        print("❌ Error:", e)
        return f"Error downloading image: {str(e)}", 500
