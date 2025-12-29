import json
import requests
import hashlib
import hmac
import datetime
import urllib.parse
from volcengine.auth.SignerV4 import SignerV4
from volcengine.auth.SignParam import SignParam
from volcengine.Credentials import Credentials
from collections import OrderedDict

def sign_v4_header_manual(ak, sk, region, service, method, host, path, query_params, payload_hash):
    now = datetime.datetime.utcnow()
    amz_date = now.strftime('%Y%m%dT%H%M%SZ')
    datestamp = amz_date[:8]

    sorted_query = sorted(query_params.items())
    canonical_query_string = '&'.join([f"{urllib.parse.quote(k)}={urllib.parse.quote(v)}" for k, v in sorted_query])
    # canonical_query_string = "Action=ChatQueryDebug&Version=2023-08-01"
    host_to_sign = "agenza.osd.co.th:30040"
    path_to_sign = "/"
    
    # 1. จัดลำดับเนื้อหา Header ให้ถูกต้อง (c -> h -> x-c -> x-d)
    canonical_headers = (
        f"content-type:application/json\n"
        f"host:{host.strip()}\n"
        f"x-content-sha256:{payload_hash}\n"
        f"x-date:{amz_date}\n"
    )
    # 2. Signed Headers ต้องเรียงเหมือนข้างบน (คั่นด้วย ;)
    signed_headers = "content-type;host;x-content-sha256;x-date"

    # 3. สร้าง Canonical Request
    # ตรวจสอบบรรทัดว่าง (\n) ให้ดีนะครับ
    # canonical_request = (
    #     f"{method}\n"
    #     # f"{path}\n"
    #     f"{path_to_sign}\n"
    #     f"{canonical_query_string}\n"
    #     f"{canonical_headers}"  # ตรงนี้มี \n อยู่แล้วหนึ่งตัวจากบรรทัด x-date
    #     f"\n"                   # บรรทัดว่างที่หายไป (สำคัญมาก!)
    #     f"{signed_headers}\n"
    #     f"{payload_hash}"
    # )
    canonical_request = (
        "POST\n" +
        path_to_sign + "\n" +
        canonical_query_string + "\n" +
        canonical_headers + "\n" + # บรรทัดว่างก่อน signed_headers
        signed_headers + "\n" +
        payload_hash
    )

    # --- DEBUG: พิมพ์ค่านี้ออกมาดูใน Console ---
    print("--- CANONICAL REQUEST ---")
    print(canonical_request)
    print("-------------------------")

    # 4. String to Sign
    algorithm = 'HMAC-SHA256'
    credential_scope = f"{datestamp}/{region}/{service}/request"
    hashed_canonical_request = hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
    string_to_sign = f"{algorithm}\n{amz_date}\n{credential_scope}\n{hashed_canonical_request}"

    # 5. Signing Key
    def sign_hmac(key, msg):
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

    k_date = sign_hmac(('V4' + sk.strip()).encode('utf-8'), datestamp)
    k_region = sign_hmac(k_date, region)
    k_service = sign_hmac(k_region, service)
    k_signing = sign_hmac(k_service, 'request')
    
    signature = hmac.new(k_signing, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

    return {
        'Authorization': f"{algorithm} Credential={ak}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}",
        'X-Date': amz_date,
        'X-Content-Sha256': payload_hash
    }
        
# def chat_query_debug_service(
#     creds, version, host, preprompt, temperature, topP, 
#     maxtokens, tool_ids, workflow_ids, trigger_configs, 
#     knowledge_ids, qa_dataset_ids, database_ids, 
#     workspace_id, size_file, app_id, query_text, 
#     workflow_publish_id, file_name, obs_url=None, workflow_id=None):
    
#     method = 'POST'
#     action = 'ChatQueryDebug'
#     service = 'app'
#     url_path = '/'
    
#     # กรณีแนบไฟล์มาด้วย
#     query_extends = {}
#     if obs_url:
#         base_proxy_url = "http://10.128.4.6:32300/api/proxy/down"
#         full_file_url = f"{base_proxy_url}?Action=Download&Version=2022-01-01&Path={obs_url}&IsAnonymous=true"
#         query_extends = {
#             "Files": [
#                 {
#                     "Name": file_name,
#                     "Path": obs_url,            
#                     "Size": size_file,             
#                     "Url": full_file_url       
#                 }
#             ]
#         }
    
#     data = OrderedDict([
#         ("Query", str(query_text)),
#         ("WorkspaceID", str(workspace_id)),
#         ("AppID", str(app_id)),
#         ("AgentMode", "Single"),
#     ])

#     if workflow_id:
#         # --- กรณีเป็น ChatFlow / Workflow ---
#         data["ChatFlowConfig"] = {
#             "WorkflowID": workflow_id,
#             "WorkflowPublishID": workflow_publish_id,
#             "ChatAdvancedConfig": {
#                 "SpeechInteractionConfig": {},
#                 "ThoughtLanguageConfig": {"Language": "th"}
#             }
#         }
#     else:
#         # --- กรณีเป็น Chatbot ปกติ (ใช้ AppConfig ตัวเต็มที่คุณให้มา) ---
#         data["InputData"] = []
#         data["AppConfig"] = {
#             "ModelID": "d393no652vvc73d72a20",
#             "ModelConfig": {
#                 "Temperature": temperature,
#                 "TopP": topP,
#                 "MaxTokens": maxtokens,
#                 "RoundsReserved": 3,
#                 "RagNum": 3,
#                 "Strategy": "react",
#                 "MaxIterations": 5,
#                 "RagEnabled": False,
#                 "ReasoningSwitchType": "disabled",
#                 "ReasoningMode": False,
#                 "CurrentTimeEnabled": False,
#                 "ReasoningSwitch": False
#             },
#             "SummaryModelID": "",
#             "PrePrompt": preprompt,
#             "PromptConfig": {"PromptMode": "regex"},
#             "VariableConfigs": [],
#             "ToolIDs": tool_ids,
#             "WorkflowIDs": workflow_ids,
#             "TriggerConfigs": trigger_configs,
#             "KnowledgeIDs": knowledge_ids,
#             "QADatasetIDs": qa_dataset_ids,
#             "DatabaseIDs": database_ids,
#             "KnowledgeConfig": {"RetrievalSearchMethod": 0, "MatchType": "force", "TopK": 3, "Similarity": 0.5},
#             "QADatasetConfig": {"RetrievalSearchMethod": 0, "MatchType": "force", "TopK": 1, "Similarity": 0.5},
#             "ChatAdvancedConfig": {
#                 "UploadConfig": {
#                     "Enabled": True,
#                     "UploadDocumentAllowed": True,
#                     "UploadImageAllowed": True,
#                     "UploadAudioAllowed": True,
#                     "UploadVideoAllowed": True,
#                     "UploadCompressedAllowed": False
#                 },
#                 "OpeningConfig": {"OpeningQuestions": [""], "OpeningEnabled": False},
#                 "SuggestEnabled": False,
#                 "ReferenceEnabled": False,
#                 "ReviewEnabled": False,
#                 "SuggestPromptConfig": {"Prompt": "", "Enabled": False},
#                 "AdvancedReviewType": "unused",
#                 "SpeechInteractionConfig": {},
#                 "ThoughtLanguageConfig": {"Language": "th"},
#                 "ShortcutPromptConfigList": []
#             },
#             "GraphIDs": [],
#             "GraphConfig": {"MatchType": "force", "SearchDepth": 3, "SearchType": 2, "TopK": 30},
#             "TerminologyIDs": [],
#             "TerminologyConfig": {"RetrievalSearchMethod": 0, "MatchType": "force", "TopK": 3, "Similarity": 0.5}
#         }

#     # --- 3. ใส่ส่วนท้าย (QueryExtends และ Top) ---
#     data["QueryExtends"] = query_extends
#     data["Top"] = {
#         "DestService": service, # หรือตัวแปร service
#         "DestAction": action # หรือตัวแปร action
#     }


#     json_body = json.dumps(data, separators=(',', ':'))
#     body_hash = hashlib.sha256(json_body.encode('utf-8')).hexdigest()

#     # 1. เตรียม Query Parameters
#     # query = OrderedDict()
#     # query['Action'] = action
#     # query['Version'] = version
    
    
#     # 3. เตรียม SignerV4 parameters
#     ak = creds['AK'].strip()
#     sk = creds['SK'].strip()
#     region = creds['REGION'].strip() or 'cn-north-1'
#     service = 'app'
    
#     query_params = {
#         'Action': 'ChatQueryDebug',
#         'Version': '2023-08-01'
#     }

#     # เรียกใช้การ Sign แบบ Manual
#     sig_headers = sign_v4_manual(ak, sk, region, service, 'POST', host, '/', query_params, body_hash)

#     # เตรียม Headers ส่งจริง
#     headers = {
#         'Content-Type': 'application/json',
#         'X-Top-Dest-Service': service,
#         'X-Top-Dest-Action': 'ChatQueryDebug'
#     }
#     headers.update(sig_headers)

#     url = f"https://{host}/?Action=ChatQueryDebug&Version=2023-08-01"
    
#     try:
#         resp = requests.post(url, headers=headers, data=json_body, timeout=120, stream=True)
#         return resp
#     except Exception as e:
#         return {"error": True, "message": str(e)}


def chat_query_debug_service(
    creds, version, host, preprompt, temperature, topP, 
    maxtokens, tool_ids, workflow_ids, trigger_configs, 
    knowledge_ids, qa_dataset_ids, database_ids, 
    workspace_id, size_file, app_id, query_text, 
    workflow_publish_id, file_name, obs_url=None, workflow_id=None):
    
    method = 'POST'
    action = 'ChatQueryDebug'
    service = 'app'
    # url_path = '/api/bypass/app/'
    url_path = '/'
    
    # กรณีแนบไฟล์มาด้วย
    query_extends = {}
    if obs_url:
        base_proxy_url = "http://10.128.4.6:32300/api/proxy/down"
        full_file_url = f"{base_proxy_url}?Action=Download&Version=2022-01-01&Path={obs_url}&IsAnonymous=true"
        query_extends = {
            "Files": [
                {
                    "Name": file_name,
                    "Path": obs_url,            
                    "Size": size_file,             
                    "Url": full_file_url       
                }
            ]
        }
    
    # data = OrderedDict([
    #     ("WorkspaceID", str(workspace_id)),
    #     ("AppID", str(app_id)),
    #     ("Query", str(query_text)),
    #     ("AgentMode", "Single"),
    #     ("ResponseMode", "streaming"),
    #     ("Stream", True)
    # ])

    # if workflow_id:
    #     # --- กรณีเป็น ChatFlow / Workflow ---
    #     data["ChatFlowConfig"] = {
    #         "WorkflowID": workflow_id,
    #         "WorkflowPublishID": workflow_publish_id,
    #         "ChatAdvancedConfig": {
    #             "SpeechInteractionConfig": {},
    #             "ThoughtLanguageConfig": {"Language": "th"}
    #         }
    #     }
    # else:
    #     # --- กรณีเป็น Chatbot ปกติ ---
    #     data["InputData"] = []
    #     data["AppConfig"] = {
    #         "ModelID": "d393no652vvc73d72a20",
    #         "ModelConfig": {
    #             "Temperature": float(temperature), # บังคับเป็น float
    #             "TopP": float(topP),               # บังคับเป็น float
    #             "MaxTokens": int(maxtokens),       # บังคับเป็น int
    #             "RoundsReserved": 3,
    #             "RagNum": 3,
    #             "Strategy": "react",
    #             "MaxIterations": 5,
    #             "RagEnabled": False,
    #             "ReasoningSwitchType": "disabled",
    #             "ReasoningMode": False,
    #             "CurrentTimeEnabled": False,
    #             "ReasoningSwitch": False
    #         },
    #         "SummaryModelID": "",
    #         "PrePrompt": str(preprompt),
    #         "PromptConfig": {"PromptMode": "regex"},
    #         "VariableConfigs": [],
    #         "ToolIDs": tool_ids if tool_ids else [],
    #         "WorkflowIDs": workflow_ids if workflow_ids else [],
    #         "TriggerConfigs": trigger_configs if trigger_configs else [],
    #         "KnowledgeIDs": knowledge_ids if knowledge_ids else [],
    #         "QADatasetIDs": qa_dataset_ids if qa_dataset_ids else [],
    #         "DatabaseIDs": database_ids if database_ids else [],
    #         "KnowledgeConfig": {"RetrievalSearchMethod": 0, "MatchType": "force", "TopK": 3, "Similarity": 0.5},
    #         "QADatasetConfig": {"RetrievalSearchMethod": 0, "MatchType": "force", "TopK": 1, "Similarity": 0.5},
    #         "ChatAdvancedConfig": {
    #             "UploadConfig": {
    #                 "Enabled": True,
    #                 "UploadDocumentAllowed": True,
    #                 "UploadImageAllowed": True,
    #                 "UploadAudioAllowed": True,
    #                 "UploadVideoAllowed": True,
    #                 "UploadCompressedAllowed": False
    #             },
    #             "OpeningConfig": {"OpeningQuestions": [""], "OpeningEnabled": False},
    #             "SuggestEnabled": False,
    #             "ReferenceEnabled": False,
    #             "ReviewEnabled": False,
    #             "SuggestPromptConfig": {"Prompt": "", "Enabled": False},
    #             "AdvancedReviewType": "unused",
    #             "SpeechInteractionConfig": {},
    #             "ThoughtLanguageConfig": {"Language": "th"},
    #             "ShortcutPromptConfigList": []
    #         },
    #         "GraphIDs": [],
    #         "GraphConfig": {"MatchType": "force", "SearchDepth": 3, "SearchType": 2, "TopK": 30},
    #         "TerminologyIDs": [],
    #         "TerminologyConfig": {"RetrievalSearchMethod": 0, "MatchType": "force", "TopK": 3, "Similarity": 0.5}
    #     }

    # # --- 3. ส่วนเสริม (ใส่ QueryExtends และ ตัด Top ออก) ---
    # data["QueryExtends"] = query_extends if query_extends else {}
    
    # หมายเหตุ: ตัดก้อน data["Top"] ออก เนื่องจากเราส่งผ่าน X-Top-Dest-Service ใน Header แล้ว
    # การส่งซ้ำใน Body บนพอร์ต :30040 มักทำให้ Agent สับสนจนไม่ตอบกลับ

    data = OrderedDict([
        ("WorkspaceID", str(workspace_id)),
        ("AppID", str(app_id)),
        ("Query", str(query_text)),
        ("InputData", []),
        ("AgentMode", "Single"),
        ("ResponseMode", "streaming"),
        ("Stream", True),
        ("AppConfig", {
            "ModelID": "d393no652vvc73d72a20",
            "ModelConfig": {
                "Temperature": float(temperature) if temperature else 0.7,
                "TopP": float(topP) if topP else 0.9,
                "MaxTokens": int(maxtokens) if maxtokens else 1000,
                
                # --- เติมฟิลด์ที่ระบบแจ้งว่า Missing ---
                "RoundsReserved": 3, 
                "RagNum": 3,
                "Strategy": "react",
                "MaxIterations": 5,
                
                # --- ฟิลด์เสริมอื่นๆ ตามที่คุณเคยมี ---
                "RagEnabled": False,
                "ReasoningSwitchType": "disabled",
                "ReasoningMode": True,
                "CurrentTimeEnabled": True,
                "ReasoningSwitch": False,
                "IsAdvancedMode": False
            },
            "PrePrompt": str(preprompt),
            "PromptConfig": {"PromptMode": "regex"},
            "VariableConfigs": [],
            "ToolIDs": tool_ids if tool_ids else [],
            "WorkflowIDs": workflow_ids if workflow_ids else [],
            "KnowledgeIDs": knowledge_ids if knowledge_ids else [],
            "QADatasetIDs": qa_dataset_ids if qa_dataset_ids else [],
            "DatabaseIDs": database_ids if database_ids else [],
        }),
        ("QueryExtends", query_extends if query_extends else {})
    ])

    json_body = json.dumps(data, separators=(',', ':'))
    body_hash = hashlib.sha256(json_body.encode('utf-8')).hexdigest()

    # # 1. เตรียม Query Parameters
    query = OrderedDict()
    query['Action'] = action
    query['Version'] = version
    
    
    # 2. ลงลายเซ็น V4
    sign = SignerV4()
    param = SignParam()
    param.path = url_path
    param.method = method
    param.host = host
    param.body = body_hash
    
    query = OrderedDict()
    query['Action'] = action
    query['Version'] = version
    param.query = {
        'Action': action,
        'Version': version
    }

    param.header_list = OrderedDict([('Host', host)])
    # header = OrderedDict()
    # header['Host'] = host
    # param.header_list = header

    cren = Credentials(creds['AK'], creds['SK'], service, creds['REGION'])
    print("DEBUG CREDENTIAL:", cren)
    resulturl = sign.sign_url(param, cren)
    print("DEBUG RESULT URL:", resulturl)
    
    # URL สุดท้าย
    url = f"https://{host}{url_path}?{resulturl}"
    
    print("DEBUG URL:", url)

    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': 'application/json, text/event-stream',
        'X-Top-Dest-Service': service,
        'X-Top-Dest-Action': action,
        'X-Top-Dest-Version': version,
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'X-Accel-Buffering': 'no'
    }


    # headers.update(resulturl)
        
    # try:
    #     # ใช้ dynamic_headers ที่ได้รับมาจาก login_service
    #     resp = requests.post(url, headers=headers, json=data, timeout=120, stream=True)
    #     print("response status", resp.status_code)
    #     full_answer = ""
    #     for line in resp.iter_lines():
    #         if line:
    #             decoded_line = line.decode('utf-8')
    #             if decoded_line.startswith('data:data:'):
    #                 json_str = decoded_line.replace('data:data:', '').strip()
    #                 try:
    #                     data_json = json.loads(json_str)
    #                     if data_json.get("event") == "message":
    #                         chunk = data_json.get("answer", "")
    #                         full_answer += chunk
    #                         print(chunk, end='', flush=True)
    #                 except:
    #                     continue
        
    #     return {"error": False, "data": full_answer}

    # except Exception as e:
    #     return {"error": True, "message": str(e)}
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=5000, stream=True, verify=True)
        print("response status", resp.status_code)
        print("--- Header Check ---")
        print(f"Content-Type: {resp.headers.get('Content-Type')}")
        print(f"Transfer-Encoding: {resp.headers.get('Transfer-Encoding')}")
        print("resp", resp)
        # 2. ถ้า resp.content ว่างเปล่า ให้ลองอ่านทีละ Byte

        # ใช้ iter_content แบบเข้มงวดที่สุด หรืออ่านจาก raw socket
            # 1. ลองใช้ chunk_size=1 เพื่อบังคับให้ Python ไม่กักข้อมูล
        for chunk in resp.iter_content(chunk_size=1, decode_unicode=True):
            if chunk:
                    # พิมพ์ออกจอดำทันทีเพื่อดูว่ามีอะไรขยับไหม
                print(chunk, end='', flush=True) 
                    
                    # ถ้าอยากสะสมเป็นบรรทัดเพื่อแกะ ID
                    # (คุณสามารถสะสมไว้ในตัวแปร buffer แล้วเช็ค data: ได้ที่นี่)
                yield chunk 
    except Exception as e:
        print(f"\n🔴 Stream Interrupted: {e}")
    
    # sig_headers = sign_v4_header_manual(
    #     ak=creds['AK'], 
    #     sk=creds['SK'], 
    #     region='cn-north-1', 
    #     service='app', 
    #     # service='hiagent', 
    #     method='POST', 
    #     host = "agenza.osd.co.th:30040", 
    #     path='/', 
    #     query_params={'Action': 'ChatQueryDebug', 'Version': '2023-08-01'}, 
    #     payload_hash=body_hash
    # )

    # signed_headers_str = "content-type;host;x-content-sha256;x-date"
    # canonical_query_string = "Action=ChatQueryDebug&Version=2023-08-01"
    # # 3. สร้าง URL ให้สะอาดที่สุด (ไม่มี X-Signature ใน URL)
    # final_url = f"https://{host}/?Action=ChatQueryDebug&Version=2023-08-01"

    # final_headers = {
    #     'Content-Type': 'application/json',
    #     'Host': host, # ต้องตรงกับ host_to_sign เป๊ะๆ
    #     'X-Top-Dest-Service': 'app',
    #     'X-Top-Dest-Action': 'ChatQueryDebug',
    # }
    # final_headers.update(sig_headers)

    # print("DEBUG FINAL URL:", final_headers)
    # print("DEBUG HEADERS:", final_headers)


    #     # 5. ยิงแบบ Stream และส่ง Body ที่เป็น bytes
    # resp = requests.post(
    #         final_url, 
    #         headers=final_headers, 
    #         data=json_body.encode('utf-8'), 
    #         stream=True, 
    #         timeout=120
    #     )
    # print("response status code:", resp.status_code)
    # return resp