# controllers/dataset.py
from flask import Blueprint, request, jsonify, current_app
from api.datasets.createDataset import create_dataset_service
from api.datasets.getDataset import get_dataset_service
from api.datasets.deleteDataset import delete_dataset_service
from api.datasets.updateDataset import update_dataset_service
from api.datasets.listDataset import list_dataset_service
from api.datasets.batchGetDataset import batch_get_dataset_service
from api.datasets.verifyDataset import verify_dataset_exists_service

dataset_bp = Blueprint('dataset', __name__)

def get_config(): 
    """ ดึงค่า Config จาก current_app (Global context) """
    return {
        'CREDENTIALS': current_app.config['CREDENTIALS'],
        'APP_VERSION': current_app.config['APP_VERSION'],
        'UP_VERSION': current_app.config['UP_VERSION'],
        'CLIENT_ID': current_app.config['CLIENT_ID'],
        'HOST': current_app.config['CREDENTIALS']['HOST']
    }

# [POST] /api/dataset/create
@dataset_bp.route('/create', methods=['POST'])
def create_dataset():
    config = get_config()
    req_data = request.get_json()

    # รับค่าที่จำเป็น
    name = req_data.get('name')
    workspace_id = req_data.get('workspace_id')

    if not name or not workspace_id:
        return jsonify({"error": "Missing name or workspace_id"}), 400

    dataset_id = create_dataset_service(
        name=req_data.get('name'),
        workspace_id=req_data.get('workspace_id'),
        desc=req_data.get('description'),
        creds=config['CREDENTIALS'],
        version=config['APP_VERSION'],
        host=config['CREDENTIALS']['HOST']
    )

    if dataset_id:
        return jsonify({
            "status": "success",
            "dataset_id": dataset_id,
            "message": "Knowledge base created successfully."
        }), 201
    
    return jsonify({"error": "Failed to create dataset"}), 500


# [POST] /api/dataset/update
@dataset_bp.route('/update', methods=['POST'])
def update_dataset():
    config = get_config()
    req_data = request.get_json()

    # รับค่าที่จำเป็น
    workspace_id = req_data.get('workspace_id')
    dataset_id = req_data.get('dataset_id')

    if not dataset_id or not workspace_id:
        return jsonify({"error": "Missing dataset_id or workspace_id"}), 400

    success = update_dataset_service(
        name=req_data.get('name'),
        workspace_id=req_data.get('workspace_id'),
        desc=req_data.get('description'),
        dataset_id=req_data.get('dataset_id'),
        creds=config['CREDENTIALS'],
        version=config['APP_VERSION'],
        host=config['CREDENTIALS']['HOST']
    )

    if success:
        return jsonify({"status": "success", "message": f"Dataset {dataset_id} updated"}), 200
    return jsonify({"error": "Update failed"}), 500

# [POST] api/dataset/get
@dataset_bp.route('/get', methods=['POST'])
def get_dataset_info():
    config = get_config()
    req_data = request.get_json()

    dataset_id = req_data.get('dataset_id')
    workspace_id = req_data.get('workspace_id')

    if not dataset_id or not workspace_id:
        return jsonify({"error": "Missing dataset_id or workspace_id"}), 400

    dataset_detail = get_dataset_service(
        dataset_id=dataset_id,
        workspace_id=workspace_id,
        creds=config['CREDENTIALS'],
        version=config['APP_VERSION'],
        host=config['HOST']
    )

    if dataset_detail:
        return jsonify({
            "status": "success",
            "data": dataset_detail
        }), 200
    
    return jsonify({"error": "Dataset not found or failed to retrieve data"}), 404


# [POST] api/dataset/list
@dataset_bp.route('/list', methods=['POST'])
def list_dataset_info():
    config = get_config()
    req_data = request.get_json()

    workspace_id = req_data.get('workspace_id')

    if not workspace_id:
        return jsonify({"error": "Missing workspace_id"}), 400

    dataset_detail = list_dataset_service(
        workspace_id=workspace_id,
        creds=config['CREDENTIALS'],
        version=config['APP_VERSION'],
        host=config['HOST']
    )

    if dataset_detail:
        return jsonify({
            "status": "success",
            "total_datasets": dataset_detail.get('Total', 0),
            "datasets": dataset_detail.get('Items', [])
    }), 200
    
    return jsonify({"error": "Dataset not found or failed to retrieve data"}), 404

# [POST] api/dataset/delete
@dataset_bp.route('/delete', methods=['POST'])
def delete_dataset_info():
    config = get_config()
    req_data = request.get_json()

    dataset_id = req_data.get('dataset_id')
    workspace_id = req_data.get('workspace_id')

    if not dataset_id or not workspace_id:
        return jsonify({"error": "Missing dataset_id or workspace_id"}), 400

    dataset_detail = delete_dataset_service(
        dataset_id=dataset_id,
        workspace_id=workspace_id,
        creds=config['CREDENTIALS'],
        version=config['APP_VERSION'],
        host=config['HOST']
    )

    if dataset_detail:
        return jsonify({
            "status": "success",
            "data": dataset_detail
        }), 200
    
    return jsonify({"error": "Dataset not found or failed to retrieve data"}), 404

# [POST] api/dataset/batch-get
@dataset_bp.route('/batch-get', methods=['POST'])
def batch_get_datasets():
    config = get_config()
    req_data = request.get_json()

    dataset_ids = req_data.get('Ids') # คาดหวังเป็น Array/List
    workspace_id = req_data.get('workspace_id')

    if not isinstance(dataset_ids, list) or not workspace_id:
        return jsonify({"error": "dataset_ids must be a list and workspace_id is required"}), 400

    items = batch_get_dataset_service(
        dataset_ids=dataset_ids,
        workspace_id=workspace_id,
        creds=config['CREDENTIALS'],
        version=config['APP_VERSION'],
        host=config['HOST']
    )

    if items is not None:
        return jsonify({
            "status": "success",
            "count": len(items),
            "items": items
        }), 200
    
    return jsonify({"error": "Failed to retrieve datasets"}), 500

# [POST] api/dataset/verify
@dataset_bp.route('/verify', methods=['POST'])
def verify_dataset():
    config = get_config()
    req_data = request.get_json()

    name = req_data.get('name')
    workspace_id = req_data.get('workspace_id')

    if not name or not workspace_id:
        return jsonify({"error": "Knowledge base name and workspace_id are required"}), 400

    exists = verify_dataset_exists_service(
        name=name,
        workspace_id=workspace_id,
        creds=config['CREDENTIALS'],
        version=config['APP_VERSION'],
        host=config['HOST']
    )

    return jsonify({
        "status": "success",
        "name": name,
        "exists": exists
    }), 200