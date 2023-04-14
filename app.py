from flask import Flask, request, send_from_directory, jsonify, render_template_string
from flask_cors import CORS
from PIL import Image
import os
import subprocess

app = Flask(__name__)
CORS(app)
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["COMPRESS_FOLDER"] = "compress"
app.config["SPECIFIC_FOLDER"] = "specific"

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["COMPRESS_FOLDER"], exist_ok=True)
os.makedirs(app.config["SPECIFIC_FOLDER"], exist_ok=True)

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
            <br>
            <form action="/specific" method="post" enctype="multipart/form-data">
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

    subprocess.run(["sh", "compress.sh", image_name])

    return render_template_string('''<!doctype html>
    <html>
        <head>
            <title>Compressed Images</title>
        </head>
        <body>
            <h1>Compressed Images</h1>
            {% for image_name in images %}
            <div>
                <h2>{{ image_name }}</h2>
                <img src="{{ url_for('compressed_image', image_name=image_name) }}" alt="{{ image_name }}">
            </div>
            {% endfor %}
            <a href="/">Back</a>
        </body>
    </html>
    ''', images=os.listdir(app.config["COMPRESS_FOLDER"]))

@app.route("/specific", methods=["POST"])
def specific():
    specific_images = ["original.png", "output.jpeg", "comparison.png"]
    return render_template_string('''<!doctype html>
    <html>
        <head>
            <title>Specific Images</title>
        </head>
        <body>
            <h1>Specific Images</h1>
            {% for image_name in images %}
            <div>
                <h2>{{ image_name }}</h2>
                <img src="{{ url_for('specific_image', image_name=image_name) }}" alt="{{ image_name }}">
            </div>
            {% endfor %}
            <a href="/">Back</a>
        </body>
    </html>
    ''', images=specific_images)


@app.route("/compressed/<image_name>", methods=["GET"])
def compressed_image(image_name):
    return send_from_directory(app.config["COMPRESS_FOLDER"], image_name)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8090)
