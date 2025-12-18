# controllers/app_center.py
from flask import Blueprint, jsonify, current_app

# Import utility functions
from api.listApp import list_app_center

# สร้าง Blueprint สำหรับ App Center Group
app_bp = Blueprint('app', __name__)

# เพื่อดึง Config จาก App Context
def get_config():
    """ ดึงค่า Config จาก current_app (Global context) """
    return {
        'CREDENTIALS': current_app.config['CREDENTIALS'],
        'APP_VERSION': current_app.config['APP_VERSION'],
        'HOST': current_app.config['CREDENTIALS']['HOST']
    }

# [POST] /api/app/list
@app_bp.route('/list', methods=['POST'])
def list_app():
    config = get_config()
    
    app_list = list_app_center(
        creds=config['CREDENTIALS'],
        version=config['APP_VERSION'],
        host=config['HOST']
    )
    
    if not app_list:
        return jsonify({"error": "Failed to list applications"}), 500
        
    return jsonify({
        "status": "success",
        "app_list": app_list
    }), 200