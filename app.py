from flask import Flask, request, jsonify
import requests
import os
import re

app = Flask(__name__)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def extract_image_urls(tweet_text):
    # اگر عکس درون توییت به صورت URL داده شده باشه
    urls = re.findall(r'(https?://\S+)', tweet_text)
    return [url for url in urls if 'pic.twitter.com' in url]

@app.route('/twitter-hook', methods=['POST'])
def twitter_hook():
    data = request.json
    tweet_text = data.get('tweet', '')
    tweet_url = data.get('link', '')

    print(f"New tweet from {data.get('username')}: {tweet_text}")
    image_urls = extract_image_urls(tweet_text)

    for url in image_urls:
        download_image(url)

    return jsonify({"status": "received"})

def download_image(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            filename = os.path.join(DOWNLOAD_DIR, url.split("/")[-1] + ".jpg")
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded image: {filename}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
