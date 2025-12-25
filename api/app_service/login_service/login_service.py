import requests
def login_service(username, password):
    host = "agenza.osd.co.th"
    base_url = f"https://{host}"
    session = requests.Session()

    # 1. GET หน้าแรกเพื่อเอา Cookie _csrf และ x-csrf-token เบื้องต้นมาใช้ในการ Login
    # ถ้าไม่ทำขั้นตอนนี้ ระบบจะฟ้องว่า Missing CSRF Token ตอนยิง Login
    initial_resp = session.get(f"{base_url}/login")
    
    # ดึง x-csrf-token ชุดแรก (มักจะอยู่ใน cookie หรือแฝงใน html)
    # ใน log ของคุณ x-csrf-token เริ่มต้นคือ "WN02h5i8-..."
    init_csrf = session.cookies.get('x-csrf-token') or ""

    # 2. เตรียม Payload และ Headers สำหรับ Login
    login_payload = {
        "username": username,
        "password": password
    }
    
    login_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "x-csrf-token": init_csrf, # ใช้ token ตัวเริ่มต้น
        "Origin": base_url,
        "Referer": f"{base_url}/login",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        # 3. ยิง Login (POST /api/auth/login)
        resp = session.post(f"{base_url}/api/auth/login", json=login_payload, headers=login_headers)
        
        if resp.status_code == 201:
            # 4. ดึง x-csrf-token ตัวใหม่จาก Response Header (Set-Cookie)
            # ตัวนี้คือตัวที่ระบบบอกว่า "DeMcQkTg-..." ซึ่งสำคัญมากสำหรับการแชท
            final_csrf = session.cookies.get('x-csrf-token')
            
            # 5. รวบรวม Cookie ทั้งหมดมาเป็น String
            cookie_str = "; ".join([f"{k}={v}" for k, v in session.cookies.items()])
            
            # 6. สร้าง Dynamic Headers ชุดที่พร้อมใช้ยิง chat_query
            headers = {
                "Accept": "application/json, text/event-stream",
                "Content-Type": "application/json; charset=utf-8",
                "app-visitor-key": "d55lbedqme7s72pormgg", # ค่านี้อาจจะ fix หรือหาจากหน้าเว็บ
                "x-csrf-token": final_csrf,
                "Cookie": cookie_str,
                "Origin": base_url,
                "Referer": f"{base_url}/product/llm/chat",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            print("Login Successful! Headers are ready.")
            return headers
        else:
            print(f"Login failed: {resp.status_code} - {resp.text}")
            return None

    except Exception as e:
        print(f"Login error: {e}")
        return None