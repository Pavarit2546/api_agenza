# api/iam/listAction.py
import json
import requests
import hashlib
from volcengine.auth.SignerV4 import SignerV4
from volcengine.auth.SignParam import SignParam
from volcengine.Credentials import Credentials
from collections import OrderedDict


def list_action_service(creds, version, host, page_number=1, page_size=10):
    method = "POST"
    action = "ListAction"
    service = "iam"
    url_path = '/api/iam'

    # เตรียม Body Data
    data = {
        "PageNumber": page_number,
        "PageSize": page_size,
        "Top": {
            "DestService": service,
            "DestAction": action
        }          
    }

    json_body = json.dumps(data)
    body_hash = hashlib.sha256(json_body.encode('utf-8')).hexdigest()

    # ลงลายเซ็น V4
    sign = SignerV4()
    param = SignParam()
    param.path = url_path
    param.method = method
    param.host = host
    param.body = body_hash
    
    query = OrderedDict()
    query['Action'] = action
    query['Version'] = version
    param.query = query


    header = OrderedDict()
    header['Host'] = host
    header['service'] = service
    param.header_list = header

    cren = Credentials(creds['AK'], creds['SK'], service, creds['REGION'])
    resulturl = sign.sign_url(param, cren)
    
    # 3. สร้าง URL สุดท้าย
    url = f"https://{host}{url_path}?{resulturl}"
    print("Requesting ListAction URL:", url)
    print("Body Data:", json_body)

    try:
        headers = {
            'Content-Type': 'application/json',
            'service': service,
            'X-Top-Dest-Service': service,
            'X-Top-Dest-Action': action,
            'X-Top-Tenant-Id': 'd354uijg9jlc72tdg5n0'
        }
        
        resp = requests.request(method, url=url, headers=headers, data=json_body, verify=True)
        
        # แสดงผลลัพธ์เพื่อ Debug
        print(f"Response Status: {resp.status_code}")
        print(f"Response Text: {resp.text}")
        
        response_data = resp.json()

        if resp.status_code != 200:
            error_status=resp.status_code
            error_info = response_data.get("ResponseMetadata", {}).get("Error", {})
            return {
                "error": True,
                "status": error_status,
                "message": error_info.get("Message", "No message provided")
            }

        # ถ้าสำเร็จ ส่งเฉพาะ Result กลับไป
        result = response_data.get("Result")
        if result is not None:
            result["error"] = False
        return result

    except Exception as e:
        print(f"ListAction Request failed: {e}")
        return {"error": True, "status": "RequestFailed", "message": str(e)}