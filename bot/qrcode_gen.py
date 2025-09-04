from qrcodegen import QrCode

def generate_qr_code(data):
    qr = QrCode.encode_text(data, QrCode.Ecc.QUARTILE)
    size = qr.get_size()
    scale = 8
    img_size = size * scale
    img = Image.new('1', (img_size, img_size), 'white')

    # วาด QR Code ลงในภาพ
    for y in range(size):
        for x in range(size):
            if qr.get_module(x, y):
                for dy in range(scale):
                    for dx in range(scale):
                        img.putpixel((x * scale + dx, y * scale + dy), 0)

    # ระบุ path ของโลโก้ใน Flask app
    logo_path = os.path.join(current_app.root_path, 'static', '01_NT-Logo.png')
    logo = Image.open(logo_path)

    # รักษาอัตราส่วนของโลโก้
    logo_width, logo_height = logo.size
    logo_ratio = logo_width / logo_height
    max_logo_size = img_size // 5  # ขยายพื้นที่ตรงกลางให้ใหญ่ขึ้น

    if logo_width > logo_height:
        new_logo_width = max_logo_size
        new_logo_height = int(max_logo_size / logo_ratio)
    else:
        new_logo_height = max_logo_size
        new_logo_width = int(max_logo_size * logo_ratio)

    logo = logo.resize((new_logo_width, new_logo_height))

    # ขยายพื้นที่รอบโลโก้ (ขยายพื้นที่ตรงกลางของ QR Code)
    padding = 10  # ขยายขนาด padding รอบโลโก้
    logo_position = ((img_size - new_logo_width - padding) // 2,
                     (img_size - new_logo_height - padding) // 2)

    draw = ImageDraw.Draw(img)
    draw.rectangle([(logo_position[0] - padding, logo_position[1] - padding),
                    (logo_position[0] + new_logo_width + padding,
                     logo_position[1] + new_logo_height + padding)],
                   fill="white")

    # วางโลโก้ตรงกลาง QR Code
    img = img.convert("RGB")
    img.paste(logo, logo_position, mask=logo)

    # แปลงภาพเป็น Base64
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    return img_str