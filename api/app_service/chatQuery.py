import json
import requests
import hashlib
from volcengine.auth.SignerV4 import SignerV4
from volcengine.auth.SignParam import SignParam
from volcengine.Credentials import Credentials
from collections import OrderedDict
 
def chat_query_service( app_key, query_text, app_conversation_id, conversation_id, creds, obs_url=None):
    host = "agenza.osd.co.th" 
    url_path = '/api/bypass/app/chat/v2/chat_query'
    method = 'POST'
    service = 'iam'
    
    query_extends = {}
    if obs_url:
        base_proxy_url = "http://10.128.4.6:32300/api/proxy/down"
        full_file_url = f"{base_proxy_url}?Action=Download&Version=2022-01-01&Path={obs_url}&IsAnonymous=true"
        query_extends = {
            "Files": [
                {
                    "Name": "1763261509123.jpg",
                    "Path": obs_url,            
                    "Size": 139527,             
                    "Url": full_file_url       
                }
            ]
        }
    # 1. เตรียม Body Data
    data = OrderedDict([
        ("AppKey", str(app_key)),
        ("Query", str(query_text)),
        ("AppConversationID" , str(app_conversation_id)),
        ("ConversationID", str(conversation_id)),
        ("QueryExtends", query_extends)
        # ("responseMode", "ChatResponseModeBlock"),
    ])

    # 2. คำนวณ Hash ของ Body สำหรับ SignerV4
    json_body = json.dumps(data, separators=(',', ':'))
    body_hash = hashlib.sha256(json_body.encode('utf-8')).hexdigest()

    # 3. เตรียม SignerV4 parameters
    sign = SignerV4()
    param = SignParam() 
    param.path = url_path
    param.method = method
    param.host = host
    param.body = body_hash
    param.query = OrderedDict()
    param.headers = {
        "Content-Type": "application/json; charset=utf-8"
    }
    # 4. ลงลายเซ็นด้วย AK/SK
    cren = Credentials(creds['AK'], creds['SK'], service, creds['REGION'])
    signature_headers = sign.sign(param, cren)

    if signature_headers is None:
        print("Error: SignerV4 returned None. Please check your AK/SK and Region.")
        return {"error": True, "message": "Signature generation failed"}
    
    
    # 5. รวม Headers (รวมลายเซ็นเข้ากับ Content-Type)
    final_headers = {
        "Accept": "application/json, text/event-stream"
    }
    if hasattr(param, 'headers'):
        final_headers.update(param.headers)
    
    final_headers.update(signature_headers) # ตอนนี้จะไม่เกิด TypeError แล้ว
    
    use_https = True
    
    url = f"{'https' if use_https else 'http'}://{host}{url_path}"
    print ("url", url)
    try:
        # ใช้ dynamic_headers ที่ได้รับมาจาก login_service
        resp = requests.post(url, headers=final_headers, json=data, timeout=120, stream=True)
        print("response status", resp.status_code)
        full_answer = ""
        for line in resp.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith('data:data:'):
                    json_str = decoded_line.replace('data:data:', '').strip()
                    try:
                        data_json = json.loads(json_str)
                        if data_json.get("event") == "message":
                            chunk = data_json.get("answer", "")
                            full_answer += chunk
                            print(chunk, end='', flush=True)
                    except:
                        continue
        
        return {"error": False, "data": full_answer}

    except Exception as e:
        return {"error": True, "message": str(e)}