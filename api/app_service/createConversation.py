import json
import requests
import hashlib
from volcengine.auth.SignerV4 import SignerV4
from volcengine.auth.SignParam import SignParam
from volcengine.Credentials import Credentials
from collections import OrderedDict

def create_conversation_service(
    # creds, version, host, 
    app_key, inputs, conversation_name):
    # method = 'POST'
    # action = 'chat_query'
    url_path = 'https://agenza.osd.co.th/api/bypass/app/chat/v2/create_conversation'
    # service = 'app'
    # service = 'bypass'

    # 1. เตรียม Body Data
    data = OrderedDict([
        ("AppKey", str(app_key)),
        ("Inputs", {}),
        ("ConversationName" , str(conversation_name)),
    ])

    # json_body = json.dumps(data, separators=(',', ':'))
    # body_hash = hashlib.sha256(json_body.encode('utf-8')).hexdigest()

    # # 1. เตรียม Query Parameters
    # query = OrderedDict()
    # # query['Action'] = action
    # # query['Version'] = version
    
    
    # # 3. เตรียม SignerV4 parameters
    # sign = SignerV4()
    # param = SignParam() 
    # param.path = url_path
    # param.method = method
    # param.host = host
    # param.body = body_hash
    # param.query = query

    # header = OrderedDict()
    # header['Host'] = host
    # param.header_list = header

    # # 4. ลงลายเซ็น (Sign)
    # cren = Credentials(creds['AK'], creds['SK'], service, creds['REGION'])
    # resulturl = sign.sign_url(param, cren)
    use_https = True

    # 5. สร้าง URL และส่ง Request
    # url = f"{'https' if use_https else 'http'}://{host}{url_path}?{resulturl}"
    headers = {
    "Accept": "application/json, text/event-stream",
    "Content-Type": "application/json; charset=utf-8",
    "app-visitor-key": "d55lbedqme7s72pormgg", # <--- ตัวสำคัญที่ขาดไป
    "x-csrf-token": "GUUsFKtq-m0mIz6Kp3V6Q6-GEVuzjOe6j0u4",
    "Cookie": "I18nextLngHiagent=th-TH; tenant=s%3Avv1AnH-WTykYNm9s1mavhUExCTNmiIrA.ZFx4N%2F9XPgMwqRvM8xVdkpE3so0GtCGKAc%2Bnp0Q5aFA; _csrf=4itLgnsvxcSVRuJGtQWSx-ic; x-csrf-token=GUUsFKtq-m0mIz6Kp3V6Q6-GEVuzjOe6j0u4",
    "Origin": "https://agenza.osd.co.th",
    "Referer": "https://agenza.osd.co.th/product/llm/chat/d52i5hg4m41s72t2ii6g",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
    }
    # print("url", url)
    print("data", data)
    print("url_path", url_path)
    print("headers", headers)

    try:
        # 1. ต้องเพิ่ม stream=True ใน requests.post
        resp = requests.post(url_path, headers=headers, json=data, timeout=120, stream=True)
        
        print("Create Conversation Status:", resp.status_code)
        print("Create Conversation Response:", resp.text)
        
        result = resp.json()
        if resp.status_code == 200:
            # ข้อมูลห้องแชทจะอยู่ใน Result.Conversation
            return {
                "error": False,
                "data": result.get("Conversation", {})
            }
        else:
            error = result.get("ResponseMetadata", {}).get("Error")
            print(f"Create App Failed: {error.get('Code')} - {error.get('Message')}")
            return {
                "error": True,
                "message": f"{error.get('Code')} - {error.get('Message')}"
            }
            
            
    except Exception as e:
        return {"error": True, "message": str(e)}