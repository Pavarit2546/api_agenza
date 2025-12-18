import json
import requests
import hashlib
from volcengine.auth.SignerV4 import SignerV4
from volcengine.auth.SignParam import SignParam
from volcengine.Credentials import Credentials
from collections import OrderedDict

def list_user_admin_service(query,creds, version, host):
    method = "POST"
    action = "ListUserForAdmin" # [cite: 903]
    service = "iam" # [cite: 344]
    url_path = '/'

    # 1. เตรียม Body Data (ส่งเฉพาะฟิลด์บังคับหรือค่าว่าง)
    # ในเอกสารระบุว่า Top เป็น true (ต้องส่ง) [cite: 907]
    data = OrderedDict([
        ("Query", query),
        ("Top", {}), # ส่ง Object ว่างตามที่เคยทำ [cite: 907]
    ])

    json_body = json.dumps(data, separators=(',', ':'))
    body_hash = hashlib.sha256(json_body.encode('utf-8')).hexdigest()

    # 2. ลงลายเซ็น V4
    sign = SignerV4()
    param = SignParam()
    param.path = url_path
    param.method = method
    param.host = host
    param.body = body_hash
    param.query = OrderedDict([('Action', action), ('Version', version)])
    
    # รวม Header 'service' เข้าไปใน Signature List
    header = OrderedDict()
    header['Host'] = host
    header['service'] = service 
    param.header_list = header

    cren = Credentials(creds['AK'], creds['SK'], service, creds['REGION'])
    resulturl = sign.sign_url(param, cren)
    url = f"https://{host}{url_path}?{resulturl}"
    print("URL:", url)

    try:
        headers = {
            'Content-Type': 'application/json',
            'service': 'iam',                    # 
            'X-Top-Dest-Service': 'iam',         # ระบุบริการปลายทาง 
            'X-Top-Dest-Action': 'ListUserForAdmin', # ระบุ Action ปลายทาง 
            'X-Top-Region': 'cn-north-1'         # ระบุ Region ตามเอกสาร 
        }
        
        resp = requests.request(method, url=url, headers=headers, data=json_body, verify=True)
        
        print(f"ListUser Response Status: {resp.status_code}")
        
        if resp.status_code != 200:
            print(f"ListUser API Error Detail: {resp.text}")
            return None

        return resp.json().get("Result") # คืนค่า Items และ Total 
        
    except Exception as e:
        print(f"ListUser Request failed: {e}")
        return None