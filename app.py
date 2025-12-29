# app.py (Refactored)
import os
import hashlib
from dotenv import load_dotenv
from flask import Flask

from controllers.document import document_bp
from controllers.app_center import app_bp
from controllers.dataset import dataset_bp
from controllers.img_gen import image_gen_bp


from controllers.iam import iam_bp

load_dotenv()

app = Flask(__name__)


app.config['CREDENTIALS'] = {
    'HOST': os.getenv('HOST'),
    'AK': os.getenv('AK'),
    'SK': os.getenv('SK'),
    'REGION': os.getenv('REGION'),
}
app.config['UP_VERSION'] = os.getenv('UP_VERSION', '2022-01-01')
app.config['APP_VERSION'] = os.getenv('APP_VERSION', '2023-08-01')
app.config['IAM_VERSION'] = os.getenv('IAM_VERSION', '2024-12-25')
app.config['CLIENT_ID'] = os.getenv('CLIENT_ID')
app.config['ARK_API_KEY'] = os.getenv('ARK_API_KEY')
app.config['ARK_HOST'] = os.getenv('ARK_HOST')
app.config['USERNAME'] = os.getenv('USERNAME')
app.config['PASSWORD'] = os.getenv('PASSWORD')


# Document APIs /api/document
app.register_blueprint(document_bp, url_prefix='/api/document')

# Dateset APIs /api/dataset
app.register_blueprint(dataset_bp, url_prefix='/api/dataset')

# App Center APIs /api/app
app.register_blueprint(app_bp, url_prefix='/api/app')

# Cluster APIs /api/cluster
app.register_blueprint(image_gen_bp, url_prefix='/api/image')

# IAM APIs /api/iam
app.register_blueprint(iam_bp, url_prefix='/api/iam')



if __name__ == '__main__':
    # ตรวจสอบว่ามีการติดตั้ง hashlib สำหรับ API files หรือไม่
    try:
        hashlib.sha256
    except AttributeError:
        print("Please ensure 'import hashlib' is present in the relevant API files.")

    print(f"Starting Flask App on port 5000. Host: {app.config['CREDENTIALS']['HOST']}")
    app.run(host='0.0.0.0', debug=True, port=5000)