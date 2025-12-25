# controllers/app_center.py
from flask import Blueprint, jsonify, current_app, request, send_file, Response, stream_with_context, json
import io
import base64
# Import utility functions
from api.app_service.login_service.login_service import login_service
from api.app_service.listApp import list_app_center
from api.app_service.createApp import create_app_service
from api.app_service.publishApp import publish_app_service
from api.app_service.deleteApp import delete_app_service
from api.app_service.updateApp import update_app_service
from api.app_service.copyApp import copy_app_service
from api.app_service.getAppCopyCheckList import get_copy_check_list_service
from api.app_service.appCopyTo import app_copy_to_service
from api.app_service.copyAppFromAppCenter import copy_app_from_app_center_service
from api.app_service.checkPublishVersion import check_publish_version_service
from api.app_service.getAppBrief import get_app_brief_service
from api.app_service.listAppBriefs import list_app_briefs_service
from api.app_service.exportAppConfig import export_app_config_service
from api.app_service.createExportAppTask import create_export_zip_task_service
from api.app_service.chatQueryDebug import chat_query_debug_service
from api.app_service.chatQueryHomeBot import chat_query_homebot_service
from api.app_service.chatQuery import chat_query_service
from api.app_service.createConversation import create_conversation_service




# สร้าง Blueprint สำหรับ App Center Group
app_bp = Blueprint('app', __name__)

# เพื่อดึง Config จาก App Context
def get_config():
    """ ดึงค่า Config จาก current_app (Global context) """
    return {
        'CREDENTIALS': current_app.config['CREDENTIALS'],
        'APP_VERSION': current_app.config['APP_VERSION'],
        'HOST': current_app.config['CREDENTIALS']['HOST'],
        'USERNAME':current_app.config['USERNAME'],
        'PASSWORD':current_app.config['PASSWORD']
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
    

# [POST] api/app/create
@app_bp.route('/create', methods=['POST'])
def create_app():
    config = get_config()
    req_data = request.get_json()

    workspace_id = req_data.get('workspace_id')
    name = req_data.get('name')
    description = req_data.get('description')
    app_type = req_data.get('app_type') # "Chatbot", "ChatFlow", "WorkFlow"

    if not name or not workspace_id:
        return jsonify({
            "status": "error",
            "message": "Name and WorkspaceID are required"
        }), 400

    result = create_app_service(
        creds=config['CREDENTIALS'],
        version=config['APP_VERSION'],
        host=config['HOST'],
        workspace_id=workspace_id,
        name=name,
        description=description,
        app_type=app_type
    )

    if result:
        return jsonify({
            "status": "success",
            "message": "Application created successfully",
            "data": result
        }), 201
    
    return jsonify({
        "status": "error", 
        "message": "Failed to create application. Check server logs for details."
    }), 500
    
    
# [POST] api/app/publish
@app_bp.route('/publish', methods=['POST'])
def publish_app():
    config = get_config()
    req_data = request.get_json()

    workspace_id = req_data.get('workspace_id')
    app_id = req_data.get('app_id')
    workflow_id = req_data.get('workflow_id', '')

    if not app_id or not workspace_id:
        return jsonify({
            "status": "error",
            "message": "AppID and WorkspaceID are required"
        }), 400

    result = publish_app_service(
        creds=config['CREDENTIALS'],
        version=config['APP_VERSION'],
        host=config['HOST'],
        workspace_id=workspace_id,
        app_id=app_id,
        workflow_id=workflow_id
    )

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
    

# [POST] api/app/check-version
@app_bp.route('/check-version', methods=['POST'])
def check_version_app():
    config = get_config()
    req_data = request.get_json()

    workspace_id = req_data.get('workspace_id')
    app_id = req_data.get('app_id')
    check_version=req_data.get('version')

    if not app_id or not workspace_id or not check_version:
        return jsonify({
            "status": "error",
            "message": "AppID and WorkspaceID are required"
        }), 400

    result = check_publish_version_service(
        creds=config['CREDENTIALS'],
        version=config['APP_VERSION'],
        host=config['HOST'],
        workspace_id=workspace_id,
        app_id=app_id,
        check_version=check_version
    )

    if result.get("error"):
        return jsonify({
            "status": "error",
            "message": result.get("message"),
            "code": result.get("status")
        }), result.get("status")

    # กรณีสำเร็จ (ส่ง 200 ตามที่คุณต้องการ)
    return jsonify({
        "status": "success",
        "message": result
    }), 200
    
    
# [POST] api/app/delete
@app_bp.route('/delete', methods=['POST'])
def delete_app():
    config = get_config()
    req_data = request.get_json()

    workspace_id = req_data.get('workspace_id')
    app_id = req_data.get('app_id')

    if not app_id or not workspace_id:
        return jsonify({
            "status": "error",
            "message": "app_id and WorkspaceID are required"
        }), 400

    success = delete_app_service(
        creds=config['CREDENTIALS'],
        version=config['APP_VERSION'],
        host=config['HOST'],
        workspace_id=workspace_id,
        app_id=app_id,
    )

    if success:
        return jsonify({
            "status": "success",
            "message": f"App ID {app_id} deleted successfully."
        }), 200
    else:
        return jsonify({"error": "Failed to delete app. Check server logs."}), 500
    
    
# [POST] api/app/update
@app_bp.route('/update', methods=['POST'])
def update_app():
    config = get_config()
    req_data = request.get_json()

    workspace_id = req_data.get('workspace_id')
    app_id = req_data.get('app_id')
    name= req_data.get('name', '')
    description= req_data.get('description', '')

    if not app_id or not workspace_id:
        return jsonify({
            "status": "error",
            "message": "app_id and WorkspaceID are required"
        }), 400

    result = update_app_service(
        creds=config['CREDENTIALS'],
        version=config['APP_VERSION'],
        host=config['HOST'],
        workspace_id=workspace_id,
        app_id=app_id,
        name=name,
        description=description,
    )

    if result:
        return jsonify({"status": "success", "message": f"App {app_id} updated"}), 200
    return jsonify({"error": "Update failed"}), 500

# [POST] api/app/copy
@app_bp.route('/copy', methods=['POST'])
def copy_app():
    config = get_config()
    req_data = request.get_json()

    workspace_id = req_data.get('workspace_id')
    from_app_id = req_data.get('from_app_id')

    if not from_app_id or not workspace_id:
        return jsonify({
            "status": "error",
            "message": "FromAppID and WorkspaceID are required"
        }), 400

    result = copy_app_service(
        creds=config['CREDENTIALS'],
        version=config['APP_VERSION'],
        host=config['HOST'],
        workspace_id=workspace_id,
        from_appId=from_app_id
    )

    if result.get("error"):
        return jsonify({
            "status": "error",
            "message": result.get("error_message"),
            "code": result.get("status_code")
        }), result.get("status_code")

    # กรณีสำเร็จ (ส่ง 200 ตามที่คุณต้องการ)
    return jsonify({
        "status": "success",
        "message": result
    }), 200

# [POST] api/app/copy-from-app-center
@app_bp.route('/copy-from-app-center', methods=['POST'])
def copy_app_from_app_center():
    config = get_config()
    req_data = request.get_json()

    workspace_id = req_data.get('workspace_id')
    from_app_id = req_data.get('from_app_id')
    name = req_data.get('name')

    if not from_app_id or not workspace_id or not name:
        return jsonify({
            "status": "error",
            "message": "FromAppID, WorkspaceID, and Name are required"
        }), 400

    result = copy_app_from_app_center_service(
        creds=config['CREDENTIALS'],
        version=config['APP_VERSION'],
        host=config['HOST'],
        workspace_id=workspace_id,
        from_appId=from_app_id,
        name=name
    )

    if result.get("error"):
        return jsonify({
            "status": "error",
            "message": result.get("error_message"),
            "code": result.get("status_code")
        }), result.get("status_code")

    # กรณีสำเร็จ (ส่ง 200 ตามที่คุณต้องการ)
    return jsonify({
        "status": "success",
        "message": result
    }), 200
    
# [POST] api/app/copy-check
@app_bp.route('/copy-check', methods=['POST'])
def get_copy_check():
    config = get_config()
    req_data = request.get_json()

    src_app_id = req_data.get('src_app_id')
    target_workspace_id = req_data.get('target_workspace_id')
    scene = req_data.get('scene', 'WorkspaceAppList')

    if not src_app_id or not target_workspace_id:
        return jsonify({
            "status": "error",
            "message": "SrcAppID and TargetWorkspaceID are required"
        }), 400

    # เรียกใช้ Service
    result = get_copy_check_list_service(
        creds=config['CREDENTIALS'],
        version=config['APP_VERSION'],
        host=config['HOST'],
        src_app_id=src_app_id,
        target_workspace_id=target_workspace_id,
        scene=scene
    )

    if not result:
        return jsonify({"status": "error", "message": "Internal Service Error"}), 500

    if result.get("error"):
        return jsonify({
            "status": "error",
            "message": result.get("error_message")
        }), result.get("status_code", 400)

    # หากสำเร็จ
    return jsonify({
        "status": "success",
        "checklist": result.get("data")
    }), 200
    
# [POST] api/app/copy-to 
@app_bp.route('/copy-to', methods=['POST'])
def copy_app_to():
    config = get_config()
    req_data = request.get_json()

    # ดึงค่าที่จำเป็นจาก request
    source_ws_id = req_data.get('source_workspace_id')
    target_ws_id = req_data.get('target_workspace_id')
    src_app_id = req_data.get('src_app_id')
    dst_app_name = req_data.get('dst_app_name') # ชื่อแอปใหม่
    scene = req_data.get('scene', 'WorkspaceAppList')
    model_replace = req_data.get('model_replace', {})

    if not all([source_ws_id, target_ws_id, src_app_id, dst_app_name]):
        return jsonify({
            "status": "error",
            "message": "Missing required fields: source_workspace_id, target_workspace_id, src_app_id, or dst_app_name"
        }), 400

    # เรียกใช้งาน Service
    result = app_copy_to_service(
        creds=config['CREDENTIALS'],
        version=config['APP_VERSION'],
        host=config['HOST'],
        source_ws_id=source_ws_id,
        target_ws_id=target_ws_id,
        src_app_id=src_app_id,
        dst_app_name=dst_app_name,
        scene=scene,
        model_replace=model_replace
    )

    if not result:
        return jsonify({"status": "error", "message": "Service returned no response"}), 500

    if result.get("error"):
        return jsonify({
            "status": "error",
            "message": result.get("error_message")
        }), result.get("status_code", 400)

    # กรณีสำเร็จ
    return jsonify({
        "status": "success",
        "message": "App copied to target workspace successfully",
        "data": result.get("data")
    }), 200
    

# [POST] api/app/brief
@app_bp.route('/get-brief', methods=['POST'])
def get_app_brief():
    config = get_config()
    req_data = request.get_json()

    workspace_id = req_data.get('workspace_id')
    app_id = req_data.get('app_id')

    if not workspace_id or not app_id:
        return jsonify({
            "status": "error",
            "message": "WorkspaceID and AppID are required"
        }), 400

    result = get_app_brief_service(
        creds=config['CREDENTIALS'],
        version=config['APP_VERSION'],
        host=config['HOST'],
        workspace_id=workspace_id,
        app_id=app_id
    )

    if result is None:
        return jsonify({"status": "error", "message": "Internal error"}), 500

    if result.get("error"):
        return jsonify({
            "status": "error",
            "message": result.get("error_message")
        }), result.get("status_code", 400)

    return jsonify({
        "status": "success",
        "data": result.get("data")
    }), 200
    
# [POST] api/app/list-briefs 
@app_bp.route('/list-briefs', methods=['POST'])
def list_briefs():
    config = get_config()
    req_data = request.get_json()

    workspace_id = req_data.get('workspace_id')
    app_name = req_data.get('app_name', "")

    if not workspace_id:
        return jsonify({
            "status": "error",
            "message": "WorkspaceID is required"
        }), 400

    result = list_app_briefs_service(
        creds=config['CREDENTIALS'],
        version=config['APP_VERSION'],
        host=config['HOST'],
        workspace_id=workspace_id,
        app_name=app_name
    )

    if result is None:
        return jsonify({"status": "error", "message": "Service internal error"}), 500

    if result.get("error"):
        return jsonify({
            "status": "error",
            "message": result.get("error_message")
        }), result.get("status_code", 400)

    return jsonify({
        "status": "success",
        "items": result.get("data", {}).get("items"),
        "total": result.get("data", {}).get("total")
    }), 200
    

# [POST] api/app/export-app-config
@app_bp.route('/export-app-config', methods=['POST'])
def export_config():
    config = get_config()
    req_data = request.get_json()

    workspace_id = req_data.get('workspace_id')
    app_id = req_data.get('app_id')

    if not workspace_id or not app_id:
        return jsonify({"status": "error", "message": "Missing parameters"}), 400

    result = export_app_config_service(
        creds=config['CREDENTIALS'],
        version=config['APP_VERSION'],
        host=config['HOST'],
        workspace_id=workspace_id,
        app_id=app_id
    )

    if result.get("error"):
        return jsonify({
            "status": "error",
            "message": result.get("error_message")
        }), result.get("status_code", 400)

    # แปลง Base64 กลับเป็น Binary เพื่อส่งให้ผู้ใช้ดาวน์โหลด
    try:
        file_content = base64.b64decode(result.get("content"))
        file_name = result.get("file_name", "config.json")
        
        return send_file(
            io.BytesIO(file_content),
            mimetype='application/octet-stream',
            as_attachment=True,
            download_name=file_name
        )
    except Exception as e:
        return jsonify({"status": "error", "message": f"File processing error: {str(e)}"}), 500
    

# [POST] api/app/create-export-task
@app_bp.route('/export-zip-task', methods=['POST'])
def export_zip_task():
    config = get_config()
    req_data = request.get_json()

    workspace_id = req_data.get('workspace_id')
    app_id = req_data.get('app_id')

    if not workspace_id or not app_id:
        return jsonify({"status": "error", "message": "Missing WorkspaceID or AppID"}), 400

    result = create_export_zip_task_service(
        creds=config['CREDENTIALS'],
        version=config['APP_VERSION'],
        host=config['HOST'],
        workspace_id=workspace_id,
        app_id=app_id,
    )

    if result.get("error"):
        return jsonify({
            "status": "error",
            "message": result.get("message")
        }), result.get("status_code", 400)

    return jsonify({
        "status": "success",
        "message": "Export task created",
        "task_id": result.get("data", {}).get("TaskID")
    }), 202 
    

# [POST] api/app/chat-query-debug
@app_bp.route('/chat-query-debug', methods=['POST'])
def chat_query_debug():
    config = get_config()
    req_data = request.get_json()

    workspace_id = req_data.get('workspace_id')
    app_id = req_data.get('app_id')
    query_text = req_data.get('query')
    # mode= req_data.get('mode', 'blocking')  # 'blocking' หรือ 'streaming'

    if not all([workspace_id, app_id, query_text]):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    result = chat_query_debug_service(
        creds=config['CREDENTIALS'],
        version=config['APP_VERSION'],
        host=config['HOST'],
        workspace_id=workspace_id,
        app_id=app_id,
        query_text=query_text,
        # mode=mode
    )

    if result.get("error"):
        return jsonify({
            "status": "error",
            "message": result.get("message")
        }), result.get("status_code", 400)

    return jsonify({
        "status": "success",
        "answer": result.get("data")
    }), 200
    
    

# [POST] api/app/chat-query-homebot
@app_bp.route('/chat-query-homebot', methods=['POST'])
def chat_query_homebot():
    config = get_config()
    req_data = request.get_json()

    # conversation_id = req_data.get('conversation_id', '')
    app_id = req_data.get('app_id', '')
    query_text = req_data.get('query', '')
    # mode= req_data.get('mode', 'blocking')  # 'blocking' หรือ 'streaming'

    result = chat_query_homebot_service(
        creds=config['CREDENTIALS'],
        version=config['APP_VERSION'],
        host=config['HOST'],
        # conversation_id=conversation_id,
        app_id=app_id,
        query_text=query_text,
        # mode=mode
    )

    if result.get("error"):
        return jsonify({
            "status": "error",
            "message": result.get("message")
        }), result.get("status_code", 400)

    return jsonify({
        "status": "success",
        "answer": result.get("data")
    }), 200
    
    
# [POST] api/app/chat-query
@app_bp.route('/chat-query', methods=['POST'])
def chat_query():
    config = get_config()
    req_data = request.get_json()
    
    # conversation_id = req_data.get('conversation_id', '')
    app_conversation_id = req_data.get('app_conversation_id')
    query_text = req_data.get('query')
    app_key = req_data.get('app_key' )
    conversation_id = req_data.get('conversation_id').strip().replace(" ", "")
    obs_url = req_data.get('obs_url')

    result = chat_query_service(
        app_conversation_id=app_conversation_id,
        app_key=app_key,
        query_text=query_text,
        conversation_id=conversation_id,
        obs_url=obs_url,
        creds=config['CREDENTIALS'],
    )

    if result.get("error"):
        yield f"data: {json.dumps({'error': result.get('message')})}\n\n"
    else:
            # ส่งข้อมูลคำตอบที่ได้จาก Service (ซึ่ง Service ควรส่งเป็นตัวอักษรหรือ chunks)
        yield f"data: {json.dumps({'answer': result.get('data')})}\n\n"
            
    return Response(stream_with_context(result.get("data")), mimetype='text/event-stream')

# [POST] api/app/create-conversaation
@app_bp.route('/create-conversation', methods=['POST'])
def create_conversation():
    config = get_config()
    req_data = request.get_json()
    
    app_key = req_data.get('app_key')
    inputs = req_data.get('inputs', {})
    conversation_name = req_data.get('conversation_name', 'New conversation')
    
    result = create_conversation_service(
        app_key=app_key,
        inputs=inputs,
        conversation_name=conversation_name
    )
    
    if result.get("error"):
        return jsonify({
            "status": "error",
            "message": result.get("message")
        }), result.get("status_code", 400)

    return jsonify({
        "status": "success",
        "answer": result
    }), 200