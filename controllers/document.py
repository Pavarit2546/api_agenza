# controllers/document.py
from flask import Blueprint, request, jsonify, current_app , Response
import tempfile
import os

# Import utility functions จาก api/
from api.documents.up.uploadRaw import upload_raw_file
from api.documents.app_service.createDocument import create_document
from api.documents.app_service.getDocument import get_document
from api.documents.app_service.deleteDocument import delete_document
from api.documents.app_service.listDocument import list_document
from api.documents.app_service.updateDocument import update_document
from api.documents.up.getDownloadKey import get_download_key
from api.documents.up.downloadFile import download_file


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

# [POST] /api/document/upload 
# สำหรับ Upload file เพื่อเอาแค่ obs_url (ใช้กรณีต้องการ path ไปทำอย่างอื่น)
@document_bp.route('/upload', methods=['POST'])
def upload_only():
    config = get_config()
    
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    filename = file.filename
    temp_path = os.path.join(tempfile.gettempdir(), filename) 
    
    try:
        file.save(temp_path)

        obs_url = upload_raw_file(
            file_path=temp_path,
            client_id=config['CLIENT_ID'],
            creds=config['CREDENTIALS'],
            version=config['UP_VERSION'],
            host=config['HOST'],
            workspace_id=None, # ไม่ใส่เพื่อเอา path ทั่วไป
            is_proxy=True      # ใช้ path /api/proxy/up
        )
        return jsonify({"status": "success", "obs_url": obs_url, "filename": filename}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
    
    
    
# [POST] /api/document/upload-and-create 
#สำหรับ Upload และผูกเข้า Dataset ทันที (ต้องส่ง workspace_id, dataset_id มาด้วย)
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
    

@document_bp.route('/download-document', methods=['POST'])
def download_document():
    config = get_config()
    data = request.get_json()
    
    obs_url = data.get('obs_url') # รับ Path ไฟล์จาก Client เช่น upload/full/...
    filename = data.get('filename', 'downloaded_file.bin')

    if not obs_url:
        return jsonify({"error": "Missing obs_url"}), 400

    # 1. ขอ Download Key (ต้องทำภายใน 10 วินาที)
    download_key = get_download_key(
        file_path_obs=obs_url,
        client_id=config['CLIENT_ID'],
        creds=config['CREDENTIALS'],
        version=config['UP_VERSION'],
        host=config['HOST']
    )

    if not download_key:
        return jsonify({"error": "Failed to get download key"}), 500

    # 2. ดาวน์โหลดไฟล์จริง
    download_resp = download_file(
        file_path_obs=obs_url,
        download_key=download_key,
        creds=config['CREDENTIALS'],
        version=config['UP_VERSION'], # หรือเวอร์ชันที่เกี่ยวข้อง
        host=config['HOST']
    )

    if not download_resp:
        return jsonify({"error": "Download failed"}), 500


    def generate():
        for chunk in download_resp.iter_content(chunk_size=8192):
            yield chunk

    return Response(
        generate(),
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": download_resp.headers.get('Content-Type', 'application/octet-stream')
        }
    )

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