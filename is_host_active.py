import socket
from urllib.parse import urlparse

def is_host_active(target_url):
    try:
        # แยก hostname และ port จาก URL
        parsed_url = urlparse(target_url)
        hostname = parsed_url.hostname
        port = parsed_url.port

        # ถ้าไม่มี port ใน URL ให้กำหนดค่า default ตาม scheme
        if port is None:
            if parsed_url.scheme == "https":
                port = 443
            else:
                port = 80

        # สร้าง socket และเชื่อมต่อ
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)  # กำหนด timeout
        sock.connect((hostname, port))
        sock.close()  # ปิด socket หลังจากเชื่อมต่อสำเร็จ
        return True
    except (socket.timeout, socket.error):
        return False

# ตัวอย่างการใช้งาน
target_url = "https://centraldigital.cattelecom.com:40000"
if is_host_active(target_url):
    print("Host ปลายทาง active!")
else:
    print("Host ปลายทางไม่ active")