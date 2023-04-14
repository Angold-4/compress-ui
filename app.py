from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS
from PIL import Image
import os
import subprocess

app = Flask(__name__)
CORS(app)
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["COMPRESS_FOLDER"] = "compress"

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["COMPRESS_FOLDER"], exist_ok=True)


@app.route("/", methods=["GET"])
def index():
    return '''
    <!doctype html>
    <html>
        <head>
            <title>Image Compressor</title>
        </head>
        <body>
            <h1>Image Compressor</h1>
            <form action="/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="image">
                <input type="submit" value="Compress">
            </form>
        </body>
    </html>
    '''


@app.route("/upload", methods=["POST"])
def upload():
    image = request.files["image"]
    image_name = image.filename

    if image_name is None:
        return "No image provided", 400

    image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_name)
    image.save(image_path)

    subprocess.run(["python3", "compress.py", image_path])

    compressed_image_path = os.path.join(app.config["COMPRESS_FOLDER"], image_name)
    return send_from_directory(app.config["COMPRESS_FOLDER"], image_name)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8090)
