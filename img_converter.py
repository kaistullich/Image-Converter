import logging
import os
from datetime import datetime
from logging import FileHandler, Formatter

import cv2
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename


def check_img_folder(path):
    """
    Checking to see if the folder "uploaded_img" is in the path. If
    the folder is not in the path it will be created

    :param path: path to folder
    :return: the path to the directory
    """
    if not os.path.exists(path):
        os.makedirs(path)
        return path
    return path


UPLOAD_FOLDER = check_img_folder(os.path.join(os.getcwd(), 'static', 'uploaded_img'))
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = os.urandom(24)


def allowed_file(filename):
    """
    Checks if there is a '.' in the file name and if the
    file extension matches one of the allowed extensions

    :param filename: the name of the image uploaded
    :return: True or False
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def convert_to_grey(img):
    """
    Takes the incoming image and converts the image to greyscale.

    :param img: the image name
    :return: True or False
    """
    try:
        load_img = cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], img), cv2.IMREAD_GRAYSCALE)
        cv2.imwrite(os.path.join(app.config["UPLOAD_FOLDER"], img), load_img)
        return True
    except (cv2.error, Exception) as e:
        app.logger.error('%s ', e)
        return False


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    """
    This route allows for files to be uploaded to the server
    for processing. There are multiple checks along the way
    to make sure the files are safe for processing.

    :return: redirect to uploaded_file route to view image
    """
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            # TODO: make the flash message appear (create flash templ. check Flask Doc)
            flash('No file part')
            return redirect(request.url)
        # get file from the request
        file = request.files['file']
        # if file name is empty
        if file.filename == '':
            # TODO: make the flash message appear (create flash templ. check Flask Doc)
            flash('No selected file')
            return redirect(request.url)
        # all checks passed
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # convert the image to greyscale
            convert_success = convert_to_grey(filename)
            if convert_success:
                return redirect(url_for('uploaded_file', filename=filename))
            else:
                return render_template('error.html')
    return render_template('index.html')


@app.route('/uploads/<string:img_name>')
def uploaded_file(img_name):
    """
    This route will allow the user to see their converted image

    :param img_name: name of the image
    :return: render template, with image filename passed along
    """
    return render_template('upload_complete.html', img_name=img_name)


def delete_old_images():
    """
    Variables:
        - img_folder
        - today
        - dt_mod
        - day_convert

    Explanations:
        • img_folder: holds the path to where all the images are stored
        • today: datetime.now() returns a datetime obj that represent the current
                 datetime. It parses out the year with the 1st split(), then continues
                 to split by the "-" (i.e. 2017-01-22) and grabs the day. It converts
                 to an int for comparison between day_convert
        • dt_mod: checks the last time the img was modified. Returns a UNIX timestamp
        • day_converted: takes the `dt_mod` and converts it into a datetime obj. It then
                         goes through the same process as `today` to parse out the day
                         from the year
    :return: None
    """

    img_folder = UPLOAD_FOLDER
    today = int(str(datetime.now()).split()[0].split('-')[2])
    for img in os.listdir(img_folder):
        dt_mod = os.path.getmtime(os.path.join(UPLOAD_FOLDER, img))
        day_convert = int(str(datetime.fromtimestamp(dt_mod)).split()[0].split('-')[2])
        # FIXME: does not take into account that if today=1 & day_convert=30/31 it will not work (END of month)
        if today > day_convert:
            os.remove(os.path.join(UPLOAD_FOLDER, img))


if __name__ == '__main__':
    file_handler = FileHandler('error_log.log')
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(
        Formatter('%(asctime)s,%(msecs)d %(levelname)-5s [%(filename)s:%(lineno)d] %(message)s',
                  datefmt='%d-%m-%Y:%H:%M:%S'
                  )
    )
    app.logger.addHandler(file_handler)
    app.run(debug=True)
