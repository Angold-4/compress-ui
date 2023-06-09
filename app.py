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
            <title>COMPS456F FYP DEMO Wyman</title>
        </head>
        <body>
            <h1>Learned Image Compression</h1>
            <h2>1. Variable Rate Lossy Image Compression with LSTM RNN</h1>
            <form action="/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="image">
                <input type="submit" value="Compress">
            </form>
            <br>
            <br>
            <h2>2. End-to-end learned Image Compression</h1>
            <form action="/upload_compress" method="post" enctype="multipart/form-data">
                <input type="file" name="image">
                <input type="submit" value="Compress">
            </form>
            <br>
            <form action="/upload_decompress" method="post" enctype="multipart/form-data">
                <input type="file" name="image">
                <input type="submit" value="Decompress">
            </form>
            <br>
            <br>
            <h1>Image Dehazing</h1>
            <h2>3. Image dehazing gunet</h2>
            <form action="/upload_dehazing" method="post" enctype="multipart/form-data">
                <input type="file" name="image">
                <input type="submit" value="Upload">
            </form>
            <br>
            <form action="/clear_dehazing" method="post">
                <input type="submit" value="Clear">
            </form>
            <br>
            <form action="/run_dehazing" method="post">
                <input type="submit" value="Dehaze">
            </form>
            <br>
            <br>
            <h1>Deraindrop</h1>
            <h2>4. Deraindrop</h2>
            <form action="/upload_deraindrop" method="post" enctype="multipart/form-data">
                <input type="file" name="image">
                <input type="submit" value="Upload">
            </form>
            <br>
            <form action="/clear_deraindrop" method="post">
                <input type="submit" value="Clear">
            </form>
            <br>
            <form action="/run_deraindrop" method="post">
                <input type="submit" value="Deraining">
            </form>
            <br>
            <br>
            <h1>Image Deraining</h1>
            <h2>5. Image Deraining PReNet</h2>
            <form action="/upload_deraining_prenet" method="post" enctype="multipart/form-data">
                <input type="file" name="image">
                <input type="submit" value="Derain">
            </form>
        </body>
    </html>

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


@app.route("/upload_dehazing", methods=["POST"])
def upload_dehazing():
    image = request.files["image"]
    image_name = image.filename

    if image_name is None:
        return "No image provided", 400

    image_path = os.path.join("scripts", "gunet", "data", "trial", image_name)
    image.save(image_path)

    return redirect(url_for("index"))


@app.route("/clear_dehazing", methods=["POST"])
def clear_dehazing():
    trial_folder = os.path.join("scripts", "gunet", "data", "trial")
    for file in os.listdir(trial_folder):
        file_path = os.path.join(trial_folder, file)
        if os.path.isfile(file_path):
            os.unlink(file_path)

    trial_folder = os.path.join("scripts", "gunet", "results", "trial", "reside-in", "gunet_b", "imgs")
    for file in os.listdir(trial_folder):
        file_path = os.path.join(trial_folder, file)
        if os.path.isfile(file_path):
            os.unlink(file_path)

    return redirect(url_for("index"))

@app.route("/display_dehazed_images", methods=["GET"])
def display_dehazed_images():
    results_folder = os.path.join("scripts", "gunet", "results", "trial", "reside-in", "gunet_b", "imgs")
    images = sorted(os.listdir(results_folder))

    return render_template_string('''
    <!doctype html>
    <html>
        <head>
            <title>Dehazed Images</title>
        </head>
        <body>
        <h1>Dehazed Images</h1>
        {% for image_name in images %}
        <img src="{{ url_for('dehazed_image', image_name=image_name) }}" alt="Dehazed Image" style="max-width: 300px;">
        <br><br>
        {% endfor %}
        <a href="/">Back</a>
        </body>
    </html>
    ''', images=images)

@app.route("/upload_deraindrop", methods=["POST"])
def upload_deraindrop():
    image = request.files["image"]
    image_name = image.filename

    if image_name is None:
        return "No image provided", 400

    image_path = os.path.join("scripts", "cyclegan", "datasets", "raindrop2clear", "testA", image_name)
    image.save(image_path)

    return redirect(url_for("index"))

@app.route("/clear_deraindrop", methods=["POST"])
def clear_deraindrop():
    folder = os.path.join("scripts", "cyclegan", "datasets", "raindrop2clear", "testA")
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path):
            os.unlink(file_path)

    folder = os.path.join("scripts", "cyclegan", "results", "raindrop2clear", "test_latest", "images")
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path):
            os.unlink(file_path)

    return redirect(url_for("index"))

@app.route("/run_deraindrop", methods=["POST"])
def run_deraindrop():
    subprocess.run(["sh", "deraindrop.sh"])

    fake_images = []
    real_images = []
    results_folder = os.path.join("scripts", "cyclegan", "results", "raindrop2clear", "test_latest", "images")
    for filename in os.listdir(results_folder):
        if "fake_B" in filename:
            fake_images.append(filename)
        if "real_A" in filename:
            real_images.append(filename)

    fake_images = sorted(fake_images)
    real_images = sorted(real_images)

    return render_template_string('''
    <!doctype html>
    <html>
        <head>
            <title>Deraindrop Results</title>
        </head>
        <body>
            <h1>Deraindrop Results</h1>
            {% for image in real_images %}
                <img src="{{ url_for('deraindrop_image', image_name=image) }}" width="400">
            {% endfor %}
            <br>
            <br>
            {% for image in fake_images %}
                <img src="{{ url_for('deraindrop_image', image_name=image) }}" width="400">
            {% endfor %}
            <br><br>
            <a href="/">Back</a>
        </body>
    </html>
    ''', fake_images=fake_images, real_images=real_images)

@app.route("/upload_deraining_prenet", methods=["POST"])
def upload_deraining_prenet():
    image = request.files["image"]
    image_name = image.filename

    if image_name is None:
        return "No image provided", 400


    rainy_image_path_ = os.path.join("scripts", "prenet", "datasets", "demo", "rainy")
    rainy_image_path = os.path.join("scripts", "prenet", "datasets", "demo", "rainy", image_name)

    for filename in os.listdir(rainy_image_path_):
        file_path = os.path.join(rainy_image_path_, filename)
        if os.path.isfile(file_path):
            os.unlink(file_path)

    image.save(rainy_image_path)

    results_folder = os.path.join("scripts", "prenet", "results", "demo_result")
    
    for filename in os.listdir(results_folder):
        file_path = os.path.join(results_folder, filename)
        if os.path.isfile(file_path):
            os.unlink(file_path)

    subprocess.run(["sh", "deraining.sh", image_name])

    result_images = []
    for filename in os.listdir(results_folder):
        result_images.append(filename)

    return render_template_string('''
    <!doctype html>
    <html>
        <head>
            <title>Deraining Results</title>
        </head>
        <body>
            <h1>Deraining Results</h1>
            {% for image in result_images %}
                <img src="{{ url_for('deraining_image', image_name=image) }}" width="300">
            {% endfor %}
            <br><br>
            <a href="/">Back</a>
        </body>
    </html>
    ''', result_images=result_images)


@app.route("/dehazed_image/<image_name>")
def dehazed_image(image_name):
    return send_from_directory(os.path.join("scripts", "gunet", "results", "trial", "reside-in", "gunet_b", "imgs"), image_name)

@app.route("/deraindrop_image/<image_name>")
def deraindrop_image(image_name):
    return send_from_directory(os.path.join("scripts", "cyclegan", "results", "raindrop2clear", "test_latest", "images"), image_name)

@app.route("/deraining_image/<image_name>")
def deraining_image(image_name):
    return send_from_directory(os.path.join("scripts", "prenet", "results", "demo_result"), image_name)

@app.route("/run_dehazing", methods=["POST"])
def run_dehazing():
    subprocess.run(["sh", "dehazing.sh"])
    return redirect(url_for("display_dehazed_images"))

@app.route("/compressed/<image_name>", methods=["GET"])
def compressed_image(image_name):
    return send_from_directory(app.config["COMPRESS_FOLDER"], image_name)

@app.route("/download/<path:subpath>/<filename>")
def download(subpath, filename):
    return send_from_directory(os.path.join("compress", subpath), filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8090)
