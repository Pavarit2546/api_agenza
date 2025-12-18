import json

from volcengine.auth.SignerV4 import SignerV4
from volcengine.auth.SignParam import SignParam
from volcengine.Credentials import Credentials
from collections import OrderedDict
import requests

method = 'POST'

action = 'ListAppCenter'
version = '2023-08-01'
host = "agenza.osd.co.th:30040"
ak = "HIAKZDM5NTBrdDR0aWlzY0hROUl5WGdaZVBONzJ2M2dlNzA"
sk = "W0F/EFez9itTgwA5aTfa+f/tSD9KQEBSbhB3FGF/ZHpYMNt/TRBnL0ogLg=="
region = 'cn-north-1'
service = 'app'
if __name__ == '__main__':

    sign = SignerV4()

    headers = {
        'Content-Type': 'application/json'
    }

    param = SignParam()
    param.path = '/'
    param.method = method
    param.host = host
    param.body = ''

    query = OrderedDict()
    query['Action'] = action
    query['Version'] = version
    param.query = query

    header = OrderedDict()
    header['Host'] = host
    param.header_list = header

    data = {
        "App": True
    }

    cren = Credentials(ak, sk, service, region)
    resulturl = sign.sign_url(param, cren)
    use_https = True

    url = f"{'https' if use_https else 'http'}://{host}/?{resulturl}"
    print(f"Request URL: {url}")
    # For local dev with self-signed cert: set verify=False (NOT for production)
    verify_ssl = True  # set False to skip verification temporarily

    try:
        resp = requests.request(method, url=url, headers={'Content-Type': 'application/json'}, data=json.dumps(data), verify=verify_ssl, timeout=10)
        print(resp.status_code)
        print(resp.text)
    except requests.exceptions.SSLError as e:
        print("SSL error:", e)
        print("If this is a local server with self-signed cert, try setting verify_ssl = False (dev only).")
    except Exception as e:
        print("Request failed:", type(e), e)