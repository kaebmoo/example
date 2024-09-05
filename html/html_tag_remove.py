from bs4 import BeautifulSoup

def remove_span_tags_bs4(html):
    """
    ฟังก์ชันนี้ใช้ BeautifulSoup เพื่อลบ tag span ออกจาก HTML ที่กำหนด

    Args:
        html: HTML ที่ต้องการลบ tag span

    Returns:
        HTML ที่ tag span ถูกนำออกแล้ว
    """
    soup = BeautifulSoup(html, 'html.parser')
    for span_tag in soup.find_all('span'):
        span_tag.unwrap()
    return str(soup)

# ตัวอย่างการใช้งาน
html_with_spans = '''<h5 id="bkmrk-%E0%B9%82%E0%B8%9B%E0%B8%A3%E0%B9%81%E0%B8%81%E0%B8%A3%E0%B8%A1%E0%B8%99%E0%B8%B5%E0%B9%89%E0%B8%AD%E0%B8%AD%E0%B8%81%E0%B9%81%E0%B8%9A%E0%B8%9A%E0%B8%A1%E0%B8%B2%E0%B9%80%E0%B8%9E" style="text-align: justify;">โปรแกรมนี้ออกแบบมาเพื่อคัดกรองข้อมูลตามเงื่อนไขที่กำหนด โดยผู้ใช้สามารถเพิ่มและปรับแต่งเงื่อนไขได้ด้วยการใช้ Regular Expression<br></h5>
<h5 id="bkmrk-%E0%B8%A1%E0%B8%B5%E0%B8%A7%E0%B8%B1%E0%B8%95%E0%B8%96%E0%B8%B8%E0%B8%9B%E0%B8%A3%E0%B8%B0%E0%B8%AA%E0%B8%87%E0%B8%84%E0%B9%8C%E0%B9%80%E0%B8%9E%E0%B8%B7%E0%B9%88%E0%B8%AD%E0%B8%84" style="text-align: justify;">มีวัตถุประสงค์เพื่อคัดแยกข้อมูลค่าใช้จ่ายที่มีการบันทึกไม่สอดคล้องกับรหัสบัญชี หรือบันทึกไม่สอดคล้องกับรหัสกิจกรรม หรือกรณีอื่น ๆ ตามที่กำหนด ซึ่งถือว่าเป็นการบันทึกข้อมูลค่าใช้จ่ายที่ไม่ถูกตามเงื่อนไขที่ออกแบบไว้ เพื่อที่จะได้ทำการแก้ไขรายการดังกล่าวให้ถูกต้อง</h5>
<h5 id="bkmrk-%E0%B8%84%E0%B8%A7%E0%B8%B2%E0%B8%A1%E0%B8%95%E0%B9%89%E0%B8%AD%E0%B8%87%E0%B8%81%E0%B8%B2%E0%B8%A3%E0%B8%82%E0%B8%B1%E0%B9%89%E0%B8%99%E0%B8%9E%E0%B8%B7%E0%B9%89%E0%B8%99%E0%B8%90">ความต้องการขั้นพื้นฐาน</h5>
<p id="bkmrk-%C2%A0-%C2%A0-1.1-%E0%B9%82%E0%B8%9B%E0%B8%A3%E0%B9%81%E0%B8%81%E0%B8%A3%E0%B8%A1-visu">&nbsp; &nbsp; 1.1 โปรแกรม Visual Studio Code<br>&nbsp; &nbsp; 1.2 Python version 3.12 ขึ้นไป<br>&nbsp; &nbsp; 1.3 ติดตั้ง Library</p>
<ul id="bkmrk-pandas-%E0%B8%94%E0%B9%89%E0%B8%A7%E0%B8%A2%E0%B8%84%E0%B8%B3%E0%B8%AA%E0%B8%B1%E0%B9%88%E0%B8%87-py">
<li class="null">Pandas ด้วยคำสั่ง py -m pip install pandas</li>
<li class="null">Openpyxl ด้วยคำสั่ง py -m pip install openpyxl</li>
</ul>
<h5 id="bkmrk-%E0%B8%81%E0%B8%B2%E0%B8%A3%E0%B9%83%E0%B8%8A%E0%B9%89%E0%B9%82%E0%B8%9B%E0%B8%A3%E0%B9%81%E0%B8%81%E0%B8%A3%E0%B8%A1-filter">การใช้โปรแกรม filtering_program.py</h5>
<p id="bkmrk-%E0%B9%82%E0%B8%9B%E0%B8%A3%E0%B9%81%E0%B8%81%E0%B8%A3%E0%B8%A1%E0%B8%99%E0%B8%B5%E0%B9%89%E0%B8%AD%E0%B8%AD%E0%B8%81%E0%B9%81%E0%B8%9A%E0%B8%9A%E0%B8%A1%E0%B8%B2%E0%B9%80%E0%B8%9E-1">โปรแกรมนี้ออกแบบมาเพื่อคัดกรองข้อมูลตามเงื่อนไขที่กำหนด โดยผู้ใช้สามารถเพิ่มและปรับแต่งเงื่อนไขได้ด้วยการใช้ Regular Expression</p>
<h5 id="bkmrk-%E0%B9%84%E0%B8%9F%E0%B8%A5%E0%B9%8C%E0%B9%80%E0%B8%AD%E0%B8%81%E0%B8%AA%E0%B8%B2%E0%B8%A3%E0%B8%97%E0%B8%B5%E0%B9%88%E0%B8%95%E0%B9%89%E0%B8%AD%E0%B8%87%E0%B9%80%E0%B8%95%E0%B8%A3">ไฟล์เอกสารที่ต้องเตรียมก่อนเริ่มโปรแกรม</h5>
<ul id="bkmrk-%E0%B9%80%E0%B8%AD%E0%B8%81%E0%B8%AA%E0%B8%B2%E0%B8%A3%E0%B8%97%E0%B8%B5%E0%B9%88%E0%B8%95%E0%B9%89%E0%B8%AD%E0%B8%87%E0%B8%81%E0%B8%B2%E0%B8%A3%E0%B8%88%E0%B8%B0%E0%B8%81%E0%B8%A3">
<li class="null">เอกสารที่ต้องการจะกรองข้อมูล โดยให้ใช้ชื่อว่า data.csv ซึ่งเป็นไฟล์ข้อมูลที่ได้จาก SAP</li>
<li class="null">เอกสาร Excel ที่ใช้เพื่อระบุเงื่อนไข โดยใช้ชื่อว่า <a href="https://centraldigital.cattelecom.com:40000/attachments/4" target="_blank" rel="noopener">condition.xlsx</a><br></li>
<li class="null">เอกสาร <a href="https://centraldigital.cattelecom.com:40000/attachments/5" target="_blank" rel="noopener">รหัสศูนย์ต้นทุน-รหัสบัญชี.xlsx</a><br></li>
</ul>
<p id="bkmrk-%E0%B9%84%E0%B8%9F%E0%B8%A5%E0%B9%8C%E0%B8%97%E0%B8%B1%E0%B9%89%E0%B8%87%E0%B8%AB%E0%B8%A1%E0%B8%94%E0%B8%88%E0%B8%B0%E0%B8%95%E0%B9%89%E0%B8%AD%E0%B8%87%E0%B8%AD%E0%B8%A2%E0%B8%B9"><br>ไฟล์ทั้งหมดจะต้องอยู่ในโฟลเดอร์เดียวกับ filtering_program.py</p>
<h5 id="bkmrk-%E0%B8%81%E0%B8%B2%E0%B8%A3%E0%B9%83%E0%B8%8A%E0%B9%89%E0%B8%87%E0%B8%B2%E0%B8%99-condition.">การใช้งาน condition.xlsx</h5>
<p id="bkmrk-%E0%B8%81%E0%B8%B2%E0%B8%A3%E0%B9%80%E0%B8%82%E0%B8%B5%E0%B8%A2%E0%B8%99%E0%B9%80%E0%B8%87%E0%B8%B7%E0%B9%88%E0%B8%AD%E0%B8%99%E0%B9%84%E0%B8%82-%E0%B8%AA%E0%B8%B2%E0%B8%A1">การเขียนเงื่อนไข สามารถดูตัวอย่างเงื่อนไขเบื้องต้นได้ในไฟล์ example_condition.xlsx</p>
<ul id="bkmrk-%E0%B8%A3%E0%B8%B0%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%AB%E0%B8%B1%E0%B8%AA%E0%B8%97%E0%B8%B5%E0%B9%88%E0%B8%95%E0%B9%89%E0%B8%AD%E0%B8%87%E0%B8%81%E0%B8%B2%E0%B8%A3%E0%B8%84%E0%B9%89">
<li class="null">ระบุรหัสที่ต้องการค้นหาลงในคอลัมน์ รหัส โดยสามารถเปลี่ยนตัวเลยเป็น X เพื่อให้เป็นตัวเลขใดก็ได้</li>
<li class="null">เขียนเงื่อนไขที่ต้องการกรองลงในคอลัมน์ find ในรูปแบบ Regular expression โดยโปรแกรมจะทำการกรองข้อมูลที่ตรงกับ Regular expression ออกมา</li>
<li class="null">หากมีรหัส G/L ที่ไม่ต้องการให้กรอง สามารถใส่รหัส G/L ได้ในคอลัมน์ exclude G/L</li>
</ul>
<h5 id="bkmrk-%E0%B9%80%E0%B8%87%E0%B8%B7%E0%B9%88%E0%B8%AD%E0%B8%99%E0%B9%84%E0%B8%82%E0%B8%9E%E0%B8%B4%E0%B9%80%E0%B8%A8%E0%B8%A9"><br>เงื่อนไขพิเศษ</h5>
<p id="bkmrk-%E2%80%9Cact-%E2%80%9D-%E0%B8%95%E0%B8%B2%E0%B8%A1%E0%B8%94%E0%B9%89%E0%B8%A7%E0%B8%A2%E0%B8%A3%E0%B8%AB%E0%B8%B1%E0%B8%AA%E0%B8%81%E0%B8%B4">&ldquo;act &rdquo; ตามด้วยรหัสกิจกรรมที่ต้องการตรวจสอบ เช่น act N0301 และ รหัส 51XXXXXX จะค้นหารหัสกิจกรรม N0301 ที่ไม่ใช่รหัสบัญชี 51XXXXXX<br>&ldquo;segment &rdquo; ตามด้วยรหัสผลิตภัณฑ์ที่ต้องการตรวจสอบ โปรแกรมจะค้นหารหัสเซกเมนต์ที่มีรหัส G/L ไม่ตรงกับที่กำหนดและ G/L ที่มีรหัสเซกเมนต์ไม่ตรงกับที่กำหนด<br>&ldquo;cancel_product&rdquo; โปรแกรมจะค้นหาข้อมูลที่มีรหัสผลิตภัณฑ์ยกเลิก<br>&ldquo;cancel_act&rdquo; โปรแกรมจะค้นหาข้อมูลที่มีรหัสกิจกรรมยกเลิก</p>
<p id="bkmrk-%E0%B9%80%E0%B8%A1%E0%B8%B7%E0%B9%88%E0%B8%AD%E0%B9%80%E0%B8%95%E0%B8%A3%E0%B8%B5%E0%B8%A2%E0%B8%A1%E0%B9%84%E0%B8%9F%E0%B8%A5%E0%B9%8C%E0%B8%97%E0%B8%B1%E0%B9%89%E0%B8%87%E0%B8%AB"><br>เมื่อเตรียมไฟล์ทั้งหมดแล้ว ผู้ใช้สามารถเปิดไฟล์ filtering_program.py ผ่าน Visual Studio Code และเริ่มการทำงานได้โดยการกด run หรือปุ่ม ctrl+F5</p>
<p id="bkmrk-%E0%B8%AB%E0%B8%A5%E0%B8%B1%E0%B8%87%E0%B8%88%E0%B8%B2%E0%B8%81%E0%B8%97%E0%B8%B5%E0%B9%88%E0%B9%82%E0%B8%9B%E0%B8%A3%E0%B9%81%E0%B8%81%E0%B8%A3%E0%B8%A1%E0%B8%97%E0%B8%B3%E0%B8%87">หลังจากที่โปรแกรมทำงานเสร็จสิ้น ผลลัพธ์ทั้งหมดจะถูกเก็บไว้ในโฟลเดอร์ Program/ Filter_result โดยจำนวนผลลัพธ์จะขึ้นอยู่กับจำนวนแถวของเงื่อนไขใน condition.xlsx เรียงจากบนลงล่าง ผลลัพธ์ที่ได้จะเป็นข้อมูลที่ตรงกับเงื่อนไข Regular Expression</p>
<p id="bkmrk-%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%99-%E0%B8%96%E0%B9%89%E0%B8%B2%E0%B9%80%E0%B8%87%E0%B8%B7%E0%B9%88%E0%B8%AD%E0%B8%99%E0%B9%84%E0%B8%82%E0%B8%A3%E0%B8%B0%E0%B8%9A%E0%B8%B8">เช่น ถ้าเงื่อนไขระบุว่า รหัส 5X604XXX ต้องมีการบันทึกรหัสกระบวนการทางธุรกิจ</p>
<p id="bkmrk-%E0%B8%9C%E0%B8%A5%E0%B8%A5%E0%B8%B1%E0%B8%9E%E0%B8%98%E0%B9%8C%E0%B8%97%E0%B8%B5%E0%B9%88%E0%B9%84%E0%B8%94%E0%B9%89%E0%B8%81%E0%B9%87%E0%B8%88%E0%B8%B0%E0%B9%80%E0%B8%9B%E0%B9%87">ผลลัพธ์ที่ได้ก็จะเป็นข้อมูล รหัส 5X604XXX ที่ไม่ได้บันทึกรหัสกระบวนการทางธุรกิจ ซึ่งเป็นการหาข้อมูลที่บันทึกผิดพลาดออกมานั่นเอง</p>
<p id="bkmrk-%E0%B8%81%E0%B8%B2%E0%B8%A3%E0%B9%80%E0%B8%82%E0%B8%B5%E0%B8%A2%E0%B8%99-regular-exp"><br><a href="https://medium.com/@siwat.s/%E0%B8%81%E0%B8%B2%E0%B8%A3%E0%B9%80%E0%B8%82%E0%B8%B5%E0%B8%A2%E0%B8%99-regular-expression-regex-192d1559bf50" target="_blank" rel="noopener">การเขียน Regular expression เบื้องต้น</a> &nbsp;</p>
<pre id="bkmrk-import-pandas-as-pd-"><code class="language-python">import pandas as pd
import shutil
import os
import re
from pathlib import Path

# ตารางเงื่อนไข
condition_table = pd.read_excel('./Program/condition.xlsx', dtype=str)

# ข้อมูลที่ต้องการนำมากรอง
main_df = pd.read_csv('./Program/data.csv', dtype=str)

# ตารางรหัสศูนย์ต้นทุน-รหัสบัญชี
account_name = pd.read_excel('./Program/รหัสศูนย์ต้นทุน-รหัสบัญชี.xlsx', 'G L', dtype=str)
cost_center = pd.read_excel('./Program/รหัสศูนย์ต้นทุน-รหัสบัญชี.xlsx', dtype=str)

# ตารางชื่อผลิตภัณฑ์
product_name = pd.read_excel('./Program/product_code.xlsx', dtype=str)

# ตารางรวมรหัส กิจกรรม, Product ยกเลิก
cancel_product = pd.read_excel('./Program/condition.xlsx', 'รหัส Product ยกเลิก', dtype=str)['รหัส']
cancel_act = pd.read_excel('./Program/condition.xlsx', 'รหัสกิจกรรมยกเลิก')['Act']

# ---------------------------------------------------------------------------------------------------#

# สำหรับใส่ชื่อ G/L ในคอลัมน์ stat
main_df = pd.merge(main_df.drop(columns=['Stat']), account_name, on='G/L', how='left')
col = main_df.pop('Stat')
main_df.insert(1, col.name, col)

# ใส้ชื่อชื่อศ.ต้นทุน
main_df = pd.merge(main_df, cost_center, left_on='ศ.ต้นทุน', right_on='รหัสศูนย์ต้นทุน', how='left')
main_df = main_df.drop(columns=['รหัสศูนย์ต้นทุน'])
main_df = main_df.rename(columns={'ชื่อตามโครงสร้าง NT ':'ชื่อศ.ต้นทุน'})

# ใส่ชื่อ Product
main_df = pd.merge(main_df, product_name, left_on='ผลิตภัณฑ์/', right_on='รหัสผลิตภัณฑ์', how='left')
main_df = main_df.drop(columns=['รหัสผลิตภัณฑ์'])

def setup_output_directory(directory_path):
    shutil.rmtree(directory_path, ignore_errors=True)
    Path(directory_path).mkdir(parents=True, exist_ok=True)

# เปลี่ยน X,x ในตารางเงื่อนไขเป็น \d เพื่อใช้ใน regex
condition_table['รหัส'] = condition_table['รหัส'].apply(lambda x: re.sub(r'[Xx]', r'\\d', x))

def apply_conditions(main_df, condition_table, cancel_product, cancel_act, output_directory):
    write_header = True
    for index, row in condition_table.iterrows():
        find_pattern = row['find']
        exclude_pattern = row['exclude G/L']
        filtered_df = main_df.loc[main_df['G/L'].str.contains(row['รหัส'], na=False, regex=True)]

        if pd.notna(exclude_pattern):
            filtered_df = filtered_df.loc[~filtered_df['G/L'].str.contains(exclude_pattern, na=False)]

        if pd.notna(find_pattern):
            if 'segment ' in find_pattern.lower():
                segment_code = ''.join(filter(str.isdigit, find_pattern))
                filtered_segment = main_df.loc[main_df['เซกเมนต์'].str.contains(segment_code, na=False)]
                filtered_segment = filtered_segment.loc[~filtered_segment['G/L'].str.contains(row['รหัส'], na=False, regex=True)]
                filtered_df = filtered_df.loc[~filtered_df['เซกเมนต์'].str.contains(segment_code, na=False)]
                filtered_df = pd.concat([filtered_segment, filtered_df])

            elif 'act ' in find_pattern.lower():
                act_code = find_pattern.split()[1]
                filtered_act = main_df.loc[main_df['Bus. Process'].str.contains(act_code, na=False)]
                filtered_df = filtered_act.loc[~filtered_act['G/L'].str.contains(row['รหัส'], na=False, regex=True)]

            elif 'cancel_product' in find_pattern.lower():
                filtered_df = filtered_df.loc[filtered_df['ผลิตภัณฑ์/'].str.contains('|'.join(cancel_product), na=False)]
            elif 'cancel_act' in find_pattern.lower():
                filtered_df = filtered_df.loc[filtered_df['Bus. Process'].str.contains('|'.join(cancel_act), na=False)]
            else:
                filtered_df = filtered_df.loc[filtered_df['Bus. Process'].str.contains(find_pattern, na=False, regex=True)]
        else:
            filtered_df = filtered_df.loc[filtered_df['Bus. Process'].isna()]

        #เพิ่มคอลัมน์ 'เงื่อนไข' ลงใน DataFrame ที่กรองแล้ว
        filtered_df = filtered_df.assign(เงื่อนไข1 = row['เงื่อนไข 1'])
        filtered_df = filtered_df.assign(เงื่อนไข2 = row['เงื่อนไข 2'])

        output_path = os.path.join(output_directory, f'result_{index + 1}.csv')
        output_path_combine = os.path.join(output_directory, f'combine_result.csv')
        filtered_df.to_csv(output_path, index=False)
        filtered_df.to_csv(output_path_combine, mode='a', index = False, header=write_header)
        write_header = False

def main():
    #ตั้งค่าโฟลเดอร์ผลลัพธ์
    output_directory = './Program/Filter_result'
    setup_output_directory(output_directory)
    apply_conditions(main_df, condition_table, cancel_product, cancel_act, output_directory)
    print("Filtering and saving completed.")

if __name__ == "__main__":
    main()
</code></pre>
<p id="bkmrk-%C2%A0"></p>'''
cleaned_html = remove_span_tags_bs4(html_with_spans)
print(cleaned_html) 
