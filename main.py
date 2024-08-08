import os

import numpy as np
from PIL import Image  # for reading image files

from flask import Flask, flash, request, redirect, url_for, render_template
from flask_bootstrap import Bootstrap5
from numpy import asarray
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = './static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

Bootstrap5(app)


# convert rbg to hex
def rgb_to_hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)


# Todo: convert the image, get its colors and return it
def get_colors(image: str):
    # Opening the image with Pillow
    img = Image.open(f'./static/uploads/{image}')
    # Converting the pillow image to a numpy ndarray
    numpy_image = asarray(img)

    # Firs i will get the different RGB colors
    red_channel = numpy_image[:, :, 0]
    green_channel = numpy_image[:, :, 1]
    blue_channel = numpy_image[:, :, 2]

    # Second I will combine then
    combined_channels = np.dstack((red_channel, green_channel, blue_channel))

    # Finally get unique values
    unique_colors, counts = np.unique(combined_channels.reshape(-1, 3), axis=0, return_counts=True)

    # Getting the top 10 colors
    top_10_indices = np.argsort(counts)[::-1][:10]
    top_10_colors = unique_colors[top_10_indices]

    # Calculating the size of the image to later get the percentage
    total_pixels = combined_channels.size // 3

    # compute the percentage for each of the top 10 colors
    color_percentages = (counts[top_10_indices] / total_pixels) * 100

    # transform the colors to hexa
    hexa_colors = []
    for color in top_10_colors:
        hexa_colors.append(rgb_to_hex(color[0], color[1], color[2]))

    # Rounding the numbers
    percent_whole_numbers = [round(percent) for percent in color_percentages]

    # Finally creating an array with objects with color and percent of color
    hexa_objects = []
    for i in range(10):
        hexa_objects.append({'value': hexa_colors[i], 'percent': percent_whole_numbers[i]})

    return hexa_objects


# This will validate the extensions add more to the ALLOWED_EXTENSIONS IF NEEDED
def allowed_file(filename):
    if '.' in filename:
        extension = filename.rsplit('.', 1)[1].lower()
        if extension in ALLOWED_EXTENSIONS:
            return True
    return False


# All the program will happen here, it show the image to upload
# then if there is an image show it and get its colors
@app.route('/', methods=['GET', 'POST'])
def home():
    image = ''
    error = ''

    # After load the image I must treat it
    if request.method == 'POST':
        # check if the post request has the file part, that is the name of the input
        if 'upload' not in request.files:
            error = 'No file part'

        # get image by the name of the input
        file = request.files['upload']

        # if user does not select file, browser also
        # submit empty part without filename
        if file.filename == '':
            error = 'No selected file'

        # the file exists and the extensions is permitted
        if file and allowed_file(file.filename):
            # secure the name using werkzeug
            filename = secure_filename(file.filename)
            image = file.filename
            # creating the full path where the image will be stored
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            # Saving
            file.save(file_path)

        # Now if I got the image i can treat it with numpy, this will happen in another function
        if image:
            colors = get_colors(image=image)
            return render_template('index.html', image=image, error=error, colors=colors)

    return render_template('index.html', image=image, error=error)


if __name__ == "__main__":
    app.run(debug=True, port=5003)
