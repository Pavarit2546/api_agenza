# controllers/iam.py
from flask import Blueprint, request, jsonify, current_app
from api.iam.createUser import create_user_service
from api.iam.listUser import list_user_admin_service


iam_bp = Blueprint('iam', __name__)

def get_config(): 
    return {
        'CREDENTIALS': current_app.config['CREDENTIALS'],
        'APP_VERSION': current_app.config['APP_VERSION'],
        'HOST': current_app.config['CREDENTIALS']['HOST']
    }

@iam_bp.route('/user/create', methods=['POST'])
def create_user():
    config = get_config()
    req_data = request.get_json()

    username = req_data.get('username')
    password = req_data.get('password')
    display_name = req_data.get('display_name', '')
    email = req_data.get('email', '')
    rolename = req_data.get('rolename')

    if not username or not password:
        return jsonify({"error": "Username, Password, Display Name, and Role Name are required"}), 400

    result = create_user_service(
        username=username,
        password=password,
        display_name=display_name,
        email=email,
        rolename=rolename,
        creds=config['CREDENTIALS'],
        version=config['APP_VERSION'],
        host=config['HOST']
    )

    if result:
        return jsonify({
            "status": "success",
            "data": result
        }), 201
    
    return jsonify({"error": "Failed to create user"}), 500

@iam_bp.route('/user/list', methods=['POST'])
def list_users():
    config = get_config()
    req_data = request.get_json()

    # รับพารามิเตอร์เสริมสำหรับกรองข้อมูล (Optional) [cite: 907]
    # query: ค้นหาจาก username หรือ displayname [cite: 907]
    query_str = req_data.get('query', "") 
    
    # เรียกใช้ Service
    result = list_user_admin_service(
        query=query_str,
        creds=config['CREDENTIALS'],
        version=config['APP_VERSION'],
        host=config['HOST']
    )

    if result is not None:
        # ผลลัพธ์ที่คาดหวังคือ { "Items": [...], "Total": 123 } [cite: 909]
        return jsonify({
            "status": "success",
            "data": result
        }), 200
    
    return jsonify({
        "status": "error",
        "message": "ไม่สามารถดึงข้อมูลผู้ใช้งานได้ โปรดตรวจสอบการ Routing หรือ Signature"
    }), 500