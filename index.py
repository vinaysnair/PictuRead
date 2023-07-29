import os
from flask import Flask, render_template, request, url_for
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract
import cv2
import numpy as np

def ocr(filename):
    img = np.array(Image.open(filename))
    norm_img = np.zeros((img.shape[0], img.shape[1]))
    img = cv2.normalize(img, norm_img, 0, 255, cv2.NORM_MINMAX)
    img = cv2.threshold(img, 100, 255, cv2.THRESH_BINARY)[1]
    img = cv2.GaussianBlur(img, (1, 1), 0)
    text = pytesseract.image_to_string(img)
    text = text.replace("-\n", "")

    return text

EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
os.makedirs(os.path.join('static'), exist_ok=True)

def allowed(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_page():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', msg='No file selected')
        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', msg='No file selected')

        if file and allowed(file.filename):
            extracted_text = ocr(file)
            file.seek(0)
            file.save(os.path.join('static', secure_filename(file.filename)))

            return render_template('index.html',
                                   msg='Successfully processed',
                                   extracted_text=extracted_text,
                                   img_src=os.path.join('static', secure_filename(file.filename))
                                   )

    elif request.method == 'GET':
        return render_template('index.html')

if __name__ == '__main__':
    app.run()