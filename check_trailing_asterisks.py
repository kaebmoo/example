import re

def has_trailing_asterisks(url_key: str) -> bool:
    """ตรวจสอบว่า url_key มีเครื่องหมาย * ต่อท้ายหรือไม่

    Args:
        url_key (str): สตริงที่ต้องการตรวจสอบ

    Returns:
        bool: True ถ้ามีเครื่องหมาย * ต่อท้าย, False ถ้าไม่มี
    """

    # ตัวอย่าง Regex ที่ยืดหยุ่น:
    # - \*$: ตรวจสอบเครื่องหมาย * หนึ่งตัวขึ้นไปที่ท้ายสตริง
    # - .*:\*: อนุญาตให้มีตัวอักษรหรือตัวเลขใดๆ ก่อนเครื่องหมาย *
    # ปรับเปลี่ยน Regex ตามความต้องการ
    pattern = r'\*$'  # ตรวจสอบ * หนึ่งตัวขึ้นไปที่ท้ายสตริง
    return re.search(pattern, url_key) is not None

def remove_trailing_asterisks(url_key: str) -> str:
    """ลบเครื่องหมาย * ทั้งหมดที่อยู่ท้ายของ url_key

    Args:
        url_key (str): สตริงที่ต้องการลบเครื่องหมาย *

    Returns:
        str: สตริงที่ลบเครื่องหมาย * ออกแล้ว
    """

    # ตัวอย่าง Regex ที่ครอบคลุม:
    # - \*+: ตรวจสอบเครื่องหมาย * หนึ่งตัวขึ้นไปที่ท้ายสตริง
    pattern = r'\*+'
    return re.sub(pattern, '', url_key)

# ตัวอย่างการใช้งาน
has_wildcard = False
url_key = "my_url_key****"
clean_url_key = remove_trailing_asterisks(url_key)
print(clean_url_key)  # ผลลัพธ์: my_url_key

if has_trailing_asterisks(url_key):
    has_wildcard = True
    
print(has_wildcard)
url_key = remove_trailing_asterisks(url_key)
print(url_key)
