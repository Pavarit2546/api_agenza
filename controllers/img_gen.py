from flask import Blueprint, request, jsonify, current_app
from api.generate.image_generate import generate_image

image_gen_bp = Blueprint('image_gen', __name__)

def get_config(): 
    """ ดึงค่า Config (เช่น ARK_API_KEY) จาก current_app """
    return {
        'ARK_API_KEY': current_app.config.get('ARK_API_KEY'),
        'ARK_HOST': current_app.config.get('ARK_HOST')
    }

# [POST] /api/image/generate
@image_gen_bp.route('/generate', methods=['POST'])
def generate_image_route():
    config = get_config()
    req_data = request.get_json()

    prompt = req_data.get('prompt')
    size = req_data.get('size','1024x1024')

    if not prompt:
        return jsonify({"error": "Missing prompt"}), 400

    # เรียกใช้ Service โดยส่งค่าที่จำเป็นเข้าไป
    result = generate_image(
        prompt=prompt,
        size=size,
        api_key=config['ARK_API_KEY'],
        host=config['ARK_HOST']
    )

    if result and 'data' in result:
        return jsonify({
            "status": "success",
            "image_url": result['data'][0]['url'],
            "data": result
        }), 200
    
    return jsonify({"error": "Failed to generate image"}), 500