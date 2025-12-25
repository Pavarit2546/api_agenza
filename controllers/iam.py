# controllers/iam.py
from unittest import result
from flask import Blueprint, request, jsonify, current_app
from api.iam.createUser import create_user_service
from api.iam.listUser import list_user_service
from api.iam.listAction import list_action_service
from api.iam.deleteUser import delete_user_service
from api.iam.getUser import get_user_service


iam_bp = Blueprint('iam', __name__)

def get_config(): 
    return {
        'CREDENTIALS': current_app.config['CREDENTIALS'],
        'IAM_VERSION': current_app.config['IAM_VERSION'],
        'HOST': current_app.config['CREDENTIALS']['HOST']
    }

# [POST] api/iam/user/create
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
        version=config['IAM_VERSION'],
        host=config['HOST']
    )

    if not result:
        return jsonify({"status": "error", "message": "No response from service"}), 500

    if not result or (isinstance(result, dict) and result.get("error") is True):
        http_code = result.get("status") if result and isinstance(result.get("status"), int) else 400
        message = result.get("message") if result else "Internal Server Error"
        return jsonify({
            "status": http_code,
            "message": message
        }), http_code

    return jsonify({
        "status": "success",
        "data": result
    }), 201

# [POST] api/iam/user/update
@iam_bp.route('/user/update', methods=['POST'])
def update_user():
    config = get_config()
    req_data = request.get_json()

    user_id = req_data.get('id')
    display_name = req_data.get('display_name', '')
    email = req_data.get('email', '')
    mobile = req_data.get('mobile', '')
    rolename = req_data.get('rolename')
    description = req_data.get('description', '')
    icon = req_data.get('icon', '')
    org_ids = req_data.get('org_ids', [])
    user_group_ids = req_data.get('user_group_ids', [])
    username = req_data.get('username', '')

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    result = create_user_service(
        username=username,
        user_id=user_id,
        mobile=mobile,
        icon=icon,
        description=description,
        org_ids=org_ids,
        user_group_ids=user_group_ids,
        display_name=display_name,
        email=email,
        rolename=rolename,
        creds=config['CREDENTIALS'],
        version=config['IAM_VERSION'],
        host=config['HOST']
    )

    if not result:
        return jsonify({"status": "error", "message": "No response from service"}), 500

    if not result or (isinstance(result, dict) and result.get("error") is True):
        http_code = result.get("status") if result and isinstance(result.get("status"), int) else 400
        message = result.get("message") if result else "Internal Server Error"
        return jsonify({
            "status": http_code,
            "message": message
        }), http_code

    return jsonify({
        "status": "success",
        "data": result
    }), 201
    
    
@iam_bp.route('/user/list', methods=['POST'])
def list_users():
    config = get_config()
    req_data = request.get_json()

    query_str = req_data.get('query', "") 
    
    # เรียกใช้ Service
    result = list_user_service(
        query=query_str,
        creds=config['CREDENTIALS'],
        version=config['IAM_VERSION'],
        host=config['HOST']
    )

    if not result:
        return jsonify({"status": "error", "message": "No response from service"}), 500

    if not result or (isinstance(result, dict) and result.get("error") is True):
        http_code = result.get("status") if result and isinstance(result.get("status"), int) else 400
        message = result.get("message") if result else "Internal Server Error"
        return jsonify({
            "status": "error",
            "message": message
        }), http_code

    return jsonify({
        "status": "success",
        "data": result
    }), 201


# [POST] api/iam/user/delete
@iam_bp.route('/user/delete', methods=['POST'])
def delete_user():
    config = get_config()
    req_data = request.get_json()

    account_id = req_data.get('id', '')
    name = req_data.get('name', '')

    if not account_id and not name:
        return jsonify({"status": "error", "message": "ID or Name is required"}), 400
    
    # ดักไว้ว่าห้ามลบ admin 
    if account_id == 'd354uijg9jlc72tdg5n0' or name == 'dev':
        return {
            "status": 403, "message": "Cannot delete admin user"
        }
    
    result = delete_user_service(
        creds=config['CREDENTIALS'],
        version=config['IAM_VERSION'], 
        host=config['HOST'],
        account_id=account_id,
        name=name
    )

    # กรณี Error
    if result.get("error"):
        return jsonify({
            "status": "error",
            "message": result.get("message"),
            "code": result.get("status")
        }), result.get("status")

    # กรณีสำเร็จ (ส่ง 200 ตามที่คุณต้องการ)
    return jsonify({
        "status": "success",
        "message": result.get("message")
    }), 200
    
    
# [POST] api/iam/user/get
@iam_bp.route('/user/get', methods=['POST'])
def get_user():
    config = get_config()
    req_data = request.get_json()

    account_id = req_data.get('id', '')
    name = req_data.get('name', '')

    if not account_id and not name:
        return jsonify({"status": "error", "message": "ID or Name is required"}), 400

    result = get_user_service(
        creds=config['CREDENTIALS'],
        version=config['IAM_VERSION'], 
        host=config['HOST'],
        account_id=account_id,
        name=name
    )

    # กรณี Error
    if result.get("error"):
        return jsonify({
            "status": "error",
            "message": result.get("message"),
            "code": result.get("status")
        }), result.get("status")

    # กรณีสำเร็จ (ส่ง 200 ตามที่คุณต้องการ)
    return jsonify({
        "status": "success",
        "message": result.get("message")
    }), 200
    
    
# [POST] api/iam/action/list
@iam_bp.route('/action/list', methods=['POST'])
def list_actions():
    config = get_config()
    req_data = request.get_json()

    page_number = req_data.get('page_number', 1)
    page_size = req_data.get('page_size', 50)

    result = list_action_service(
        creds=config['CREDENTIALS'],
        version=config['IAM_VERSION'],
        host=config['HOST'],
        page_number=page_number,
        page_size=page_size
    )

    if not result:
        return jsonify({"status": "error", "message": "No response from service"}), 500

    if not result or (isinstance(result, dict) and result.get("error") is True):
        http_code = result.get("status") if result and isinstance(result.get("status"), int) else 400
        message = result.get("message") if result else "Internal Server Error"
        return jsonify({
            "status": http_code,
            "message": message
        }), http_code

    return jsonify({
        "status": "success",
        "total": result.get("Total"),
        "actions": result.get("Actions")
    }), 200
    