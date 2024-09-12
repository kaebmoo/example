import qrcode
from PIL import Image, ImageDraw

# ข้อความหรือ URL ที่จะใช้สร้าง QR Code
data = "https://pypi.org/project/qrcode/"

# สร้าง QR Code
qr = qrcode.QRCode(
    version=4,  # ขนาดของ QR Code (1 คือเล็กที่สุด)
    error_correction=qrcode.constants.ERROR_CORRECT_H,  # ระดับการแก้ไขข้อผิดพลาด (H สูงสุด)
    box_size=10,  # ขนาดของแต่ละกล่อง (หน่วยเป็นพิกเซล)
    border=4,  # ขนาดของขอบ (หน่วยเป็นจำนวนกล่อง)
)

qr.add_data(data)
qr.make(fit=True)

# สร้าง QR Code ในรูปแบบภาพ
qr_image = qr.make_image(fill_color="black", back_color="white").convert('RGB')

# ขนาดของ QR Code
qr_width, qr_height = qr_image.size

# โหลดโลโก้
logo = Image.open("01_NT-Logo.png")

# กำหนดขนาดของโลโก้ให้อยู่กลาง QR Code โดยรักษาอัตราส่วนเดิม
logo_width, logo_height = logo.size
logo_ratio = logo_width / logo_height

# คำนวณขนาดใหม่ของโลโก้โดยรักษาอัตราส่วน
logo_size = qr_width // 4  # ขนาดความกว้างสูงสุดของโลโก้ (1/4 ของ QR Code)
if logo_width > logo_height:
    new_width = logo_size
    new_height = int(logo_size / logo_ratio)
else:
    new_height = logo_size
    new_width = int(logo_size * logo_ratio)

logo = logo.resize((new_width, new_height))

# สร้างพื้นที่ว่างตรงกลางเพื่อใส่โลโก้
logo_position = ((qr_width - new_width) // 2, (qr_height - new_height) // 2)
draw = ImageDraw.Draw(qr_image)
draw.rectangle(
    [logo_position, (logo_position[0] + new_width, logo_position[1] + new_height)],
    fill="white"
)

# วางโลโก้ตรงกลาง QR Code
qr_image.paste(logo, logo_position, mask=logo)

# บันทึกภาพ QR Code ที่มีโลโก้
qr_image.save("qrcode_with_logo.png")

qr_image.show()  # แสดงภาพ QR Code
