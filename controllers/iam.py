# controllers/iam.py
from unittest import result
from flask import Blueprint, request, jsonify, current_app
from api.iam.createUser import create_user_service
from api.iam.listUser import list_user_service
from api.iam.listAction import list_action_service
from api.iam.deleteUser import delete_user_service
from api.iam.getUser import get_user_service
from api.iam.updateUser import update_user_service
from api.iam.updateUserStatus import update_user_status_service
from api.iam.ResetUserPassword import Reset_user_password_service
from api.iam.listWorkspace import list_workspace_service




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

    result = update_user_service(
        username=username,
        user_id=user_id,
        mobile=mobile,
        icon=icon,
        description=description,
        org_ids=org_ids,
        user_group_ids=user_group_ids,
        display_name=display_name,
        email=email,
        role_name=rolename,
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
    
    
# [POST] api/iam/user/update-status   
@iam_bp.route('/user/update-status', methods=['POST'])
def update_user_status():
    config = get_config()
    req_data = request.get_json()

    user_id = req_data.get('id')
    status = req_data.get('status', '1')

    if not user_id or not status:
        return jsonify({"error": "User ID and Status is required"}), 400

    result = update_user_status_service(
        id=user_id,
        status=status,
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
    
    
# [POST] api/iam/user/reset-password
@iam_bp.route('/user/reset-password', methods=['POST'])
def reset_user_password():
    config = get_config()
    req_data = request.get_json()

    password = req_data.get('password')
    tanant_id = req_data.get('tanant_id')
    username = req_data.get('username')
    
    if not password or not tanant_id or not username:
        return jsonify({"error": "Password, Tenant ID, and Username are required"}), 400
    
    result = Reset_user_password_service(
        password=password,
        tanant_id=tanant_id,
        username=username,
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
    }), 200
    
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

    # if not account_id or not name:
    #     return jsonify({"status": "error", "message": "ID or Name is required"}), 400
    
    # ดักไว้ว่าห้ามลบ admin 
    if account_id == 'd54f6sj5efk17iahevipvc' or name == 'dev' or account_id == 'd55lcif9k09c72tvh48g' or name == 'osd_admin':
        return jsonify({
            "status": "error", "message": "Cannot delete admin user"
        }), 403
    
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
    
    
# [POST] api/iam/workspace/list
@iam_bp.route('/workspace/list', methods=['POST'])
def list_workspaces():
    config = get_config()

    result = list_workspace_service(
        creds=config['CREDENTIALS'],
        version=config['IAM_VERSION'],
        host=config['HOST'],
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
        "result": result.get("message")
    }), 200
    