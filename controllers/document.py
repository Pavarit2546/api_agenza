# controllers/document.py
from flask import Blueprint, request, jsonify, current_app
import tempfile
import os

# Import utility functions จาก api/
from api.documents.uploadRaw import upload_raw_file
from api.documents.createDocument import create_document
from api.documents.getDocument import get_document
from api.documents.deleteDocument import delete_document
from api.documents.listDocument import list_document
from api.documents.updateDocument import update_document

# สร้าง Blueprint สำหรับ Document Group
document_bp = Blueprint('document', __name__)

# ดึง Config จาก App Context
def get_config(): 
    """ ดึงค่า Config จาก current_app (Global context) """
    return {
        'CREDENTIALS': current_app.config['CREDENTIALS'],
        'APP_VERSION': current_app.config['APP_VERSION'],
        'UP_VERSION': current_app.config['UP_VERSION'],
        'CLIENT_ID': current_app.config['CLIENT_ID'],
        'HOST': current_app.config['CREDENTIALS']['HOST']
    }

# [POST] /api/document/upload-and-create
@document_bp.route('/upload-and-create', methods=['POST'])
def upload_and_create():
    
    config = get_config()
    
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    dataset_id = request.form.get('dataset_id')
    doc_name = request.form.get('doc_name')
    workspace_id = request.form.get('workspace_id')
    
    if not dataset_id or not doc_name or not workspace_id:
        return jsonify({"error": "Missing required parameters: dataset_id, doc_name, or workspace_id"}), 400

    file = request.files['file']
    filename = file.filename
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, filename) 
    
    try:
        file.save(temp_path)
    except Exception as e:
        return jsonify({"error": f"Failed to save temporary file: {e}"}), 500

    # 1. UploadRaw
    obs_url = upload_raw_file(
        file_path=temp_path,
        workspace_id=workspace_id,
        client_id=config['CLIENT_ID'],
        creds=config['CREDENTIALS'],
        version=config['UP_VERSION'],
        host=config['HOST']
    )
    
    try:
        os.remove(temp_path)
    except Exception as e:
        print(f"Warning: Failed to remove temporary file {temp_path}: {e}")

    if not obs_url:
        return jsonify({"error": "UploadRaw failed", "step": 1}), 500

    # 2. CreateDocument
    doc_id = create_document(
        obs_url=obs_url,
        workspace_id=workspace_id,
        filename=filename,
        creds=config['CREDENTIALS'],
        version=config['APP_VERSION'],
        dataset_id=dataset_id, 
        doc_name=doc_name,
        host=config['HOST']
    )

    if not doc_id:
        return jsonify({"error": "CreateDocument failed", "step": 2}), 500

    return jsonify({
        "status": "success",
        "message": "File uploaded and document created successfully.",
        "obs_url": obs_url,
        "document_id": doc_id,
        "filename": filename
    }), 200

# [POST] /api/document/get
@document_bp.route('/get', methods=['POST'])
def get_document_info():
    config = get_config()
    
    try:
        data = request.get_json()
        doc_id = data.get('document_id')
        dataset_id = data.get('dataset_id')
        workspace_id = data.get('workspace_id')
    except:
        return jsonify({"error": "Invalid JSON or missing body."}), 400
    
    if not doc_id or not dataset_id or not workspace_id:
        return jsonify({"error": "Missing required parameters: document_id, dataset_id, or workspace_id"}), 400

    document_info = get_document(
        doc_id=doc_id,
        dataset_id=dataset_id,
        workspace_id=workspace_id,
        creds=config['CREDENTIALS'],
        version=config['APP_VERSION'],
        host=config['HOST']
    )

    if document_info is None or not document_info:
        return jsonify({"error": "Failed to retrieve document info or Document not found."}), 500

    return jsonify({
        "status": "success",
        "document_info": document_info
    }), 200

# [POST] /api/document/list
@document_bp.route('/list', methods=['POST'])
def list_document_info():
    config = get_config()
    
    try:
        data = request.get_json()
        dataset_id = data.get('dataset_id')
        workspace_id = data.get('workspace_id')
        # ไม่ต้องรับ filter/doc_id/filename เพื่อให้ ListDocument ดึงมาทั้งหมดตามที่คุณต้องการ
    except:
        return jsonify({"error": "Invalid JSON or missing body."}), 400
    
    if not dataset_id or not workspace_id:
        return jsonify({"error": "Missing required parameters: dataset_id or workspace_id"}), 400
    
    # Assumption: list_document in api/ is updated to take only these args
    document_info = list_document(
        dataset_id=dataset_id,
        workspace_id=workspace_id,
        creds=config['CREDENTIALS'],
        version=config['APP_VERSION'],
        host=config['HOST']
    )

    if document_info is None:
        return jsonify({"error": "Failed to retrieve document list."}), 500

    return jsonify({
        "status": "success",
        "total_documents": document_info.get('Total', 0),
        "documents": document_info.get('Items', [])
    }), 200

# [POST] /api/document/delete
@document_bp.route('/delete', methods=['POST'])
def del_document_info():
    config = get_config()
    
    try:
        data = request.get_json()
        doc_id = data.get('document_id')
        dataset_id = data.get('dataset_id')
        workspace_id = data.get('workspace_id')
    except:
        return jsonify({"error": "Invalid JSON or missing body."}), 400
    
    if not doc_id or not dataset_id or not workspace_id:
        return jsonify({"error": "Missing required parameters: document_id, dataset_id, or workspace_id"}), 400

    success = delete_document(
        doc_id=doc_id,
        dataset_id=dataset_id,
        workspace_id=workspace_id,
        creds=config['CREDENTIALS'],
        version=config['APP_VERSION'],
        host=config['HOST']
    )

    if success:
        return jsonify({
            "status": "success",
            "message": f"Document ID {doc_id} deleted successfully."
        }), 200
    else:
        return jsonify({"error": "Failed to delete document. Check server logs."}), 500
    
# [POST] /api/document/update
@document_bp.route('/update', methods=['POST'])
def update_doc():
    config = get_config()
    try:
        data = request.get_json()
        doc_id = data.get('document_id')
        dataset_id = data.get('dataset_id')
        workspace_id = data.get('workspace_id')
    except:
        return jsonify({"error": "Invalid JSON or missing body."}), 400
    
    if not doc_id or not dataset_id or not workspace_id:
        return jsonify({"error": "Missing required parameters: document_id, dataset_id, or workspace_id"}), 400
    
    success = update_document(
        doc_id=data.get('document_id'),
        dataset_id=data.get('dataset_id'),
        workspace_id=data.get('workspace_id'),
        filename=data.get('filename'),
        creds=config['CREDENTIALS'],
        version=config['APP_VERSION'],
        host=config['HOST'],
    )
    
    if success:
        return jsonify({"status": "success", "message": f"Document {doc_id} updated"}), 200
    return jsonify({"error": "Update failed"}), 500