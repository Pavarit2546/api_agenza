import json
import requests
import hashlib
from volcengine.auth.SignerV4 import SignerV4
from volcengine.auth.SignParam import SignParam
from volcengine.Credentials import Credentials
from collections import OrderedDict
 
def chat_query_service( app_key, version, query_text, app_conversation_id, conversation_id, creds, obs_url=None):
    
    host = "agenza.osd.co.th" 
    url_path = '/api/bypass/app/chat/v2/chat_query'
    method = 'POST'
    service = 'app'
    
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
    ])

    # 2. คำนวณ Hash ของ Body สำหรับ SignerV4
    json_body = json.dumps(data, separators=(',', ':'))
    body_hash = hashlib.sha256(json_body.encode('utf-8')).hexdigest()
    

    query = OrderedDict()
    query['Version'] = version
    
    
    # 3. เตรียม SignerV4 parameters
    sign = SignerV4()
    param = SignParam() 
    param.path = url_path
    param.method = method
    param.host = host
    param.body = body_hash
    param.query = query

    header = OrderedDict()
    header['Host'] = host
    param.header_list = header

    # 4. ลงลายเซ็น (Sign)
    cren = Credentials(creds['AK'], creds['SK'], service, creds['REGION'])
    print("cren", cren)
    resulturl = sign.sign_url(param, cren)
    print("resulturl", resulturl)
    # 4. สร้าง URL และส่ง Request
    url = f"https://{host}{url_path}?{resulturl}"
    print("url", url)
    # Headers สำหรับยิงจริง ต้องตรงกับที่ระบุใน header_list
    final_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream'
    }
    
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