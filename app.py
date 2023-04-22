from flask import Flask, request, send_from_directory, jsonify, render_template_string, session, redirect, url_for, send_from_directory
from flask_cors import CORS
from PIL import Image
import os
import subprocess

app = Flask(__name__)
CORS(app)
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["COMPRESS_FOLDER"] = "compress"
app.config["SPECIFIC_FOLDER"] = "specific"

app.secret_key = 'super secret key'

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["COMPRESS_FOLDER"], exist_ok=True)
os.makedirs(app.config["SPECIFIC_FOLDER"], exist_ok=True)

@app.route("/", methods=["GET"])
def index():
    return '''
    <!doctype html>
    <html>
        <head>
            <title>Learned Image Compression</title>
        </head>
        <body>
            <h1>Variable Rate Lossy Image Compression with LSTM RNN</h1>
            <form action="/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="image">
                <input type="submit" value="Compress">
            </form>
            <br>
            <br>
            <h1>End-to-end learned Image Compression</h1>
            <form action="/upload_compress" method="post" enctype="multipart/form-data">
                <input type="file" name="image">
                <input type="submit" value="Compress">
            </form>
            <br>
            <form action="/upload_decompress" method="post" enctype="multipart/form-data">
                <input type="file" name="image">
                <input type="submit" value="Decompress">
            </form>
        </body>
    </html>
    '''

@app.route("/select", methods=["GET"])
def select():
    return render_template_string('''
    <!doctype html>
    <html>
        <head>
            <title>Select Compressed Image</title>
        </head>
        <body>
            <h1>Select Compressed Image</h1>
            <form action="/display" method="post">
                <select name="image_name">
                    {% for image_name in images %}
                        <option value="{{ image_name }}">{{ image_name }}</option>
                    {% endfor %}
                </select>
                <input type="submit" value="Display">
            </form>
            <a href="/">Back</a>
        </body>
    </html>
    ''', images=sorted(os.listdir(app.config["COMPRESS_FOLDER"])))

@app.route("/upload", methods=["POST"])
def upload():
    image = request.files["image"]
    image_name = image.filename

    if image_name is None:
        return "No image provided", 400

    image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_name)
    image.save(image_path)
    session['original_image_path'] = image_path

    subprocess.run(["sh", "compress.sh", image_name])

    return redirect(url_for("select"))

@app.route("/display", methods=["POST"])
def display():
    image_name = request.form["image_name"]
    original_image_path = session.get('original_image_path')
    compressed_image_path = os.path.join(app.config["COMPRESS_FOLDER"], image_name)

    compressed_size = os.path.getsize(compressed_image_path)
    original_size = os.path.getsize(original_image_path)
    compression_ratio = round(compressed_size / original_size, 2)

    return render_template_string('''
    <!doctype html>
    <html>
        <head>
            <title>Image Details</title>
        </head>
        <body>
            <h1>Image Details</h1>
            <h2>Compressed Image</h2>
            <img src="{{ url_for('compressed_image', image_name=image_name) }}" alt="Compressed Image">
            <h2>Compression Ratio: {{ compression_ratio }}</h2>
            <h2>File Size: {{ compressed_size }} bytes</h2>
            <h2>Original File Size: {{ original_size }} bytes</h2>
            <a href="#" onclick="window.history.back();">Back</a>
        </body>
    </html>
    ''', image_name=image_name, compression_ratio=compression_ratio, compressed_size=compressed_size, original_size=original_size, original_image_path=original_image_path)


@app.route("/upload_compress", methods=["POST"])
def upload_compress():
    image = request.files["image"]
    image_name = image.filename

    if image_name is None:
        return "No image provided", 400

    image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_name)
    image.save(image_path)

    # Run the compression script
    subprocess.run(["sh", "aecompress.sh", image_name])

    return redirect(url_for("compression_result"))

@app.route("/upload_decompress", methods=["POST"])
def upload_decompress():
    image = request.files["image"]
    image_name = image.filename

    if image_name is None:
        return "No image provided", 400

    image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_name)
    image.save(image_path)

    # Run the decompression script
    subprocess.run(["sh", "decompress.sh", image_name])

    return redirect(url_for("decompression_result"))

@app.route("/compression_result", methods=["GET"])
def compression_result():
    compressed_file = "compressed.tfci"
    subpath = "aec"
    compressed_file_path = os.path.join("compress", subpath, compressed_file)
    compressed_size = os.path.getsize(compressed_file_path)
    download_url = url_for('download', subpath=subpath, filename=compressed_file)

    return render_template_string('''
    <!doctype html>
    <html>
        <head>
            <title>Compression Result</title>
        </head>
        <body>
            <h1>Compression Result</h1>
            <h2>Compressed File Size: {{ compressed_size }} bytes</h2>
            <a href="{{ download_url }}">Download compressed file</a>
            <br><br>
            <a href="/">Back</a>
        </body>
    </html>
    ''', compressed_size=compressed_size, download_url=download_url)

@app.route("/decompression_result", methods=["GET"])
def decompression_result():
    decompressed_file = "decompress.png"
    download_url = url_for('download', subpath="decompressed", filename=decompressed_file)

    return render_template_string('''
    <!doctype html>
    <html>
        <head>
            <title>Decompression Result</title>
        </head>
        <body>
            <h1>Decompression Result</h1>
            <h2>Decompressed Image</h2>
            <img src="{{ download_url }}" alt="Decompressed Image">
            <br><br>
            <a href="/">Back</a>
        </body>
    </html>
    ''', decompressed_file=decompressed_file, download_url=download_url)

@app.route("/compressed/<image_name>", methods=["GET"])
def compressed_image(image_name):
    return send_from_directory(app.config["COMPRESS_FOLDER"], image_name)

@app.route("/download/<path:subpath>/<filename>")
def download(subpath, filename):
    return send_from_directory(os.path.join("compress", subpath), filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8090)
