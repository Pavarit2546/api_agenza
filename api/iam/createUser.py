import json
import requests
import hashlib
from volcengine.auth.SignerV4 import SignerV4
from volcengine.auth.SignParam import SignParam
from volcengine.Credentials import Credentials
from collections import OrderedDict

def create_user_service(username, password, display_name, email, rolename, creds, version, host):
    method = "POST"
    action = "CreateUser"
    service = "iam"
    # url_path = '/'
    url_path = '/iam/'

    # 1. เตรียม Body Data ตามโครงสร้าง user.CreateUserRequest
    # data = OrderedDict([
    #     ("UserName", str(username)),
    #     ("Password", str(password)),
    #     ("DisplayName", str(display_name)),
    #     ("RoleName", str(rolename)),
    #     ("Email", str(email)),
    #     ("Top", {
    #         "RequestID": "dsfmregdf66",
    #         "TenantID": "d354uijg9jlc72tdg5n0",
    #         "UserID": "9999",
    #         "RegionKey": "cn-north-1",
    #         "DestService": service,
    #         "DestAction": action,
    #         "Version": version,
    #         "IdentityType": "user"
    #     })
    # ])
    data = OrderedDict([
        ("UserName", str(username)),
        ("Password", str(password)),
        ("DisplayName", str(display_name)),
        ("RoleName", str(rolename)),
        ("Email", str(email)),
        ("Top", {
            "DestService": service, # ระบุปลายทางใน Body [cite: 135, 17]
            "DestAction": action # ระบุ Action จริงใน Body [cite: 135, 17]
        })
    ])
    print("Body Data:", data)
    # ทำ Compact JSON เพื่อความแม่นยำของ Signature
    json_body = json.dumps(data, separators=(',', ':'))
    body_hash = hashlib.sha256(json_body.encode('utf-8')).hexdigest()

    # 2. ลงลายเซ็น V4
    sign = SignerV4()
    param = SignParam()
    param.path = url_path
    param.method = method
    param.host = host
    param.body = body_hash
    
    # *** ลองเพิ่มพารามิเตอร์ปลายทางเข้าไปใน Query ตรงๆ ***
    query = OrderedDict()
    query['Action'] = action
    query['Version'] = version
    query['Service'] = service # ระบุปลายทางใน Query ด้วย
    param.query = query

    # บังคับรวม Header ที่จำเป็นในการ Routing
    header = OrderedDict()
    header['Host'] = host
    header['service'] = service # [cite: 345]
    param.header_list = header

    cren = Credentials(creds['AK'], creds['SK'], service, creds['REGION'])
    resulturl = sign.sign_url(param, cren)
    url = f"https://{host}{url_path}?{resulturl}"
    print("URL:", url)
    try:
        headers = {
            'Content-Type': 'application/json',
            'service': service, # [cite: 345]
            'X-Top-Dest-Service': service, # 
            'X-Top-Dest-Action': action, # 
            'X-Top-Tenant-Id': 'd354uijg9jlc72tdg5n0' # 
        }
        
        resp = requests.request(method, url=url, headers=headers, data=json_body, verify=True)
        
        if resp.status_code != 200:
            print(f"CreateUser API Error: {resp.text}")
            return None

        return resp.json().get("Result")
        
    except Exception as e:
        print(f"CreateUser Request failed: {e}")
        return None