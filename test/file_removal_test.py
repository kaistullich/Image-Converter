import os
from datetime import datetime

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploaded_img')


def delete_old_images():
    img_folder = UPLOAD_FOLDER
    today = int(str(datetime.now()).split()[0].split('-')[2])
    for img in os.listdir(img_folder):
        dt_mod = os.path.getmtime(os.path.join(UPLOAD_FOLDER, img))
        day_convert = int(str(datetime.fromtimestamp(dt_mod)).split()[0].split('-')[2])
        if today > day_convert:
            os.remove(os.path.join(UPLOAD_FOLDER, img))


if __name__ == '__main__':
    delete_old_images()
