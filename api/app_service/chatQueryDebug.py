import json
import requests
import hashlib
from volcengine.auth.SignerV4 import SignerV4
from volcengine.auth.SignParam import SignParam
from volcengine.Credentials import Credentials
from collections import OrderedDict

def chat_query_debug_service(creds, version, host, workspace_id, app_id, query_text):
    method = 'POST'
    action = 'ChatQueryDebug'
    service = 'app'
    url_path = '/'
    #url_path = '/api/bypass/app/'

    # 1. เตรียม Body Data
    data = OrderedDict([
        ("WorkspaceID", str(workspace_id)),
        ("AppID", str(app_id)),
        ("Query", str(query_text)),
        # ("ChatFlowConfig", { "WorkflowID" : "d4b9573es25s72ttmi20"})
        # ("ResponseMode", mode)
        ("Top" ,{
            "DestService": service,
            "DestAction": method
        })
    ])

    json_body = json.dumps(data, separators=(',', ':'))
    body_hash = hashlib.sha256(json_body.encode('utf-8')).hexdigest()

    # 1. เตรียม Query Parameters
    query = OrderedDict()
    query['Action'] = action
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
    resulturl = sign.sign_url(param, cren)
    use_https = True

    # 5. สร้าง URL และส่ง Request
    url = f"{'https' if use_https else 'http'}://{host}{url_path}?{resulturl}"
    headers = {'Content-Type': 'application/json'}
    print("url", url)

    try:
        resp = requests.post(url, headers=headers, data=json_body.encode('utf-8'), verify=True, timeout=120)
        print("resp.text", resp.text)
        print("resp.status_code", resp.status_code)
        if not resp.text.strip():
            return {"error": True, "status_code": resp.status_code, "message": "Empty response"}

        # ถ้าเป็นโหมด blocking จะได้ JSON กลับมาตรงๆ
        response_json = resp.json()
        print("response_json", response_json)
        print("Response Status Code:", resp.status_code)
        error_data = response_json.get("ResponseMetadata", {}).get("Error")

        if resp.status_code != 200 or error_data:
            return {
                "error": True,
                "status_code": resp.status_code,
                "message": error_data.get('Message') if error_data else "Chat failed"
            }

        return {
            "error": False,
            "data": response_json.get("Result", {}).get("Data")
        }

    except Exception as e:
        return {"error": True, "status_code": 500, "message": str(e)}