import json
import hashlib
import requests
from collections import OrderedDict
from volcengine.auth.SignerV4 import SignerV4
from volcengine.auth.SignParam import SignParam
from volcengine.Credentials import Credentials

def get_message_info_debug(creds, host, version, workspace_id, message_id):
    method = 'POST'
    action = 'GetMessageInfoDebug'
    version = '2023-08-01'
    service = 'app'
    url_path = '/api/app'

    # 1. เตรียม Body Data
    data = OrderedDict([
        ("MessageID", str(message_id)),
        ("WorkspaceID", str(workspace_id)),
        ("Top", {
            "DestService": service,
            "DestAction": action
        })
    ])

    json_body = json.dumps(data, separators=(',', ':'))
    body_hash = hashlib.sha256(json_body.encode('utf-8')).hexdigest()
    
    query = OrderedDict()
    query['Action'] = action
    query['Version'] = version

    # 2. เตรียม Signature
    sign = SignerV4()
    param = SignParam()
    param.method = method
    param.host = host
    param.path = url_path
    param.body = body_hash
    param.query = query

    header = OrderedDict()
    header['Host'] = host
    param.header_list = header

    cren = Credentials(creds['AK'], creds['SK'], service, creds['REGION'])
    resulturl = sign.sign_url(param, cren)
    
    url = f"https://{host}{url_path}?{resulturl}"
    
    print("Requesting PubilshApp URL:", url)
    print("Body Data:", json_body)

    try:
        headers = {
            'Content-Type': 'application/json',
            'X-Top-Dest-Service': service,
            'X-Top-Dest-Action': action,
        }
        
        resp = requests.request(method, url=url, headers=headers, data=json_body, verify=True)
        
        # แสดงผลลัพธ์เพื่อ Debug
        print(f"Response Status: {resp.status_code}")
        print(f"Response Text: {resp.text}")
        
        response_data = resp.json()

        if resp.status_code != 200:
            error_info = response_data.get("ResponseMetadata", {}).get("Error", {})
            return {
                "error": True,
                "status": resp.status_code,
                "message": error_info.get("Message", "GetMessageInfoDebug failed"),
                "data": error_info.get("Data", {})
            }

        return {"error": False, "status": 200, "message": response_data.get("Result")}

    except Exception as e:
        return {"error": True, "status": 500, "message": str(e)}