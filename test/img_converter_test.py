import cv2
import os


def convert_to_gray(img):
    load_img = cv2.imread(img, cv2.IMREAD_GRAYSCALE)
    cv2.imwrite('Cities_18_gray.png', load_img)


if __name__ == '__main__':
    convert_to_gray(os.getcwd() + '/static/uploaded_img/Cities_11.jpg')
