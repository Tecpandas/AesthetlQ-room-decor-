from flask import Flask, render_template, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
from PIL import Image, ImageOps
import numpy as np
from sklearn.cluster import KMeans

app = Flask(__name__)
app.secret_key = "your_secret_key"  # For flash messages

# Ensure the uploads folder exists
UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to extract dominant colors from an image
def extract_dominant_colors(image_path, num_colors=3):
    image = Image.open(image_path)
    image = image.resize((100, 100))  # Resize for faster processing
    image_np = np.array(image)
    pixels = image_np.reshape(-1, 3)

    kmeans = KMeans(n_clusters=num_colors, random_state=0)
    kmeans.fit(pixels)
    dominant_colors = kmeans.cluster_centers_.astype(int)

    return dominant_colors

# Function to suggest complementary colors
def suggest_complementary_colors(dominant_colors):
    complementary_colors = []
    for color in dominant_colors:
        # Calculate complementary color: invert RGB values
        comp_color = [255 - c for c in color]
        complementary_colors.append(comp_color)
    return complementary_colors

# Function to apply complementary colors to the image
def apply_complementary_colors(image_path, complementary_colors):
    image = Image.open(image_path).convert("RGB")
    image_np = np.array(image)
    h, w, _ = image_np.shape
    output_image = np.zeros_like(image_np)

    for i in range(h):
        for j in range(w):
            pixel = image_np[i, j]
            distances = [np.linalg.norm(pixel - color) for color in complementary_colors]
            closest_color = complementary_colors[np.argmin(distances)]
            output_image[i, j] = closest_color

    output_image = Image.fromarray(output_image.astype('uint8'), 'RGB')
    output_path = os.path.splitext(image_path)[0] + '_complementary.jpg'
    output_image.save(output_path)
    return output_path

# Function to suggest furniture based on dominant colors
def suggest_furniture(dominant_colors):
    furniture_suggestions = []
    for color in dominant_colors:
        if color[0] > 200 and color[1] < 100 and color[2] < 100:
            furniture_suggestions.append("Modern Red Sofa")
        elif color[0] < 100 and color[1] > 200 and color[2] < 100:
            furniture_suggestions.append("Elegant Green Chair")
        elif color[0] < 100 and color[1] < 100 and color[2] > 200:
            furniture_suggestions.append("Blue Accent Table")
        else:
            furniture_suggestions.append("Wooden Coffee Table")
    return furniture_suggestions

# Function to suggest plates based on dominant colors
def suggest_plates(dominant_colors):
    plate_suggestions = []
    for color in dominant_colors:
        if color[0] > 200 and color[1] > 200 and color[2] > 200:
            plate_suggestions.append("White Ceramic Plate")
        elif color[0] < 100 and color[1] < 100 and color[2] < 100:
            plate_suggestions.append("Black Stone Plate")
        else:
            plate_suggestions.append("Colorful Artistic Plate")
    return plate_suggestions

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash("No file selected!")
        return redirect(url_for('home'))

    file = request.files['file']
    if file.filename == '':
        flash("No file selected!")
        return redirect(url_for('home'))

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Extract dominant colors
        dominant_colors = extract_dominant_colors(filepath)
        colors_hex = ["#{:02x}{:02x}{:02x}".format(*color) for color in dominant_colors]

        # Suggest complementary colors
        complementary_colors = suggest_complementary_colors(dominant_colors)
        complementary_colors_hex = ["#{:02x}{:02x}{:02x}".format(*color) for color in complementary_colors]

        # Apply complementary colors to the image
        complementary_image_path = apply_complementary_colors(filepath, complementary_colors)
        complementary_image_url = complementary_image_path.replace('./', '/')

        # Suggest furniture and plates based on dominant colors
        furniture_suggestions = suggest_furniture(dominant_colors)
        plate_suggestions = suggest_plates(dominant_colors)

        return render_template('results.html', 
                             colors=colors_hex, 
                             complementary_colors=complementary_colors_hex, 
                             complementary_image=complementary_image_url, 
                             furniture=furniture_suggestions, 
                             plates=plate_suggestions)

if __name__ == '__main__':
    app.run(debug=True)
