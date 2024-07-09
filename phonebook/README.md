# Phone Book

## โปรแกรมค้นข้อมูลจาก csv ไฟล์ ซึ่งเป็นข้อมูลสมุดโทรศัพท์ โดยสามารถค้นหาได้จาก ชื่อ ชื่อหน่วยงาน email หรือ หมายเลขโทรศัพท์

-   ทำงานร่วมกับ telegram bot

-   สามารถลงทะเบียนด้วย email ผ่านทาง telegram bot (/register email
    โปรแกรมจะส่ง activate code ไปทาง email)

-   ผู้ใช้ยืนยัน code ผ่านทาง telegram bot (/activate code)

-   คำสั่งสร้าง bot ด้วย BotFather `/newbot - create a new bot`
จากนั้นก็ทำตามที่ BotFather แนะนำ (ตั้งชื่อ bot, ตั้งชื่อ username ของ bot โดยชื่อต้องไม่ซ้ำ, BotFather จะสร้าง bot ให้และกำหนด token ที่ใช้สำหรับเข้าถึง HTTP API ของ telegram)
                                  
การกำหนด web hook ให้กับ telegram bot ทำได้โดย

-   <https://api.telegram.org/botYOUR_TELEGRAM_BOT_TOKEN/setWebhook?url=YOUR_WEB_APP_URL>

### รายละเอียดไฟล์ .env

```
YOUR_TELEGRAM_BOT_TOKEN=xxxxx token ที่ได้จากการสร้าง telegram bot ใน BotFather
YOUR_CSV_FILE=Phonebook.csv
DEBUG_MODE=false
EMAIL_USER=user@domain.com 
EMAIL_PASS=xxxxx รหัสผ่านของ email ที่จะใช้ส่ง
WEBHOOK_URL=xxxxxxxxxx ใช้เป็น uuid ก็ได้
```

-    `app.js`: โปรแกรมที่ทำด้วย NodeJS
-    `main.py`: โปรแกรมที่ทำด้วย Flask
-    ที่เหลือไม่ได้ใช้ เป็นแค่โปรแกรมตัวอย่าง

# Phone Book

## A CSV-based phone book search program that allows searching by name, department, email, or phone number.

-   Integrated with a Telegram bot for user interaction.

-   User registration via Telegram bot using email (`/register email`) to receive an activation code.

-   User activation through the Telegram bot (`/activate code`).
-   Create a bot using BotFather: `/newbot` - create a new bot. Then follow the instructions from BotFather (set the bot's name, set a unique username for the bot. BotFather will create the bot and assign a token used for accessing the Telegram HTTP API).

### Setting up a Webhook for the Telegram Bot

-   Use the following URL: `https://api.telegram.org/botYOUR_TELEGRAM_BOT_TOKEN/setWebhook?url=YOUR_WEB_APP_URL`

### .env File Details

```
YOUR_TELEGRAM_BOT_TOKEN=xxxxx (token obtained from creating a Telegram bot in BotFather)
YOUR_CSV_FILE=Phonebook.csv
DEBUG_MODE=false
EMAIL_USER=user@domain.com
EMAIL_PASS=xxxxx (password of the email used for sending)
WEBHOOK_URL=xxxxxxxxxx (can use a UUID)
```

- `app.js`: NodeJS program.
- `main.py`: Flask program.
- The rest are unused, they are just example programs.


                                                                                        
```                                                                                        
                                                                        
                                                                        
     telegram         https://host.domain.com/webhook/xxxxx             
     server           nginx for reverse proxy                           
     ┌──────┐        ┌──────┐          ┌──────┐                         
     │      │        │      │          │      │                         
     │      │◄──────►│      │          │      │ http://127.0.0.1:8080   
     │      │        │      │◄────────►│      │ Web hook server         
     └──────┘        └──────┘          └───┬──┘ NodeJS or Flask         
         ▲                                 │                            
         │                                 │                            
         │                                 │                            
         │                                 │                            
         │                                 ▼                            
         │                             ┌──────┐                         
         │                             │      │                         
         │                             │      │ mail.server             
         │                             │      │                         
         │                             └───┬──┘                         
         │                                 │                            
         │                                 │                            
         │                                 │                            
         │                                 │                            
         │                                 │                            
         │                                 │                            
         ▼telegram app                     │                            
      ┌──────┐                             │                            
      │      │                             │                            
      │      │  BotFather                  │                            
      │      │  /newbot - create a new bot │                            
      └──────┘                             │                            
           /register email@address         │                            
           /activate code  ◄───────────────┘                            
                                                                        
                             
```                                                                                        
- config for nginx reverse proxy
```
upstream node_app {
        server localhost:8181;  # พอร์ตของแอปพลิเคชัน Node.js or Flask phonebook
}

server {
    listen 443 ssl;
    
    server_name host.domain.com;
    ssl_certificate_key /etc/letsencrypt/live/host.domain.com/privkey.pem; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/host.domain.com/fullchain.pem; # managed by Certbot
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;


    location /webhook/xxxxx {
            proxy_pass http://node_app;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
    }

}

```

-    Phonebook.csv

```
| ชื่อ-นามสกุล             | คำนำชื่อ-อังกฤษ | ชื่อ-อังกฤษ | นามสกุล-อังกฤษ | ตำแหน่งเต็ม        | ตำแหน่ง     | ต.บริหาร | ส่วนงาน  | ชื่อเต็มส่วนงาน              | e-mail            | โทรศัพท์      |
|-----------------------|--------------|----------|--------------|-----------------|------------|---------|---------|--------------------------|-------------------|-------------|
| นายบัพ ฟาโล            | Mr.          | Buf      | Falo         | กรรมการผู้จัดการใหญ่ | CEO        | CEO     | ขายขำ     | บริษัท ขายขำ จำกัด (มหาชน)  | user1@domain.com  | 02xxxxxxx   |
| นางสาว งามไส้ ในปฐพี    | Miss.        | Ngamsai  | Naipattaphe  | นักการตลาด        | Marketing  |         | การตลาด | บริษัท ขายขำ จำกัด (มหาชน)  | user2@domain.com  | 02xxxxxxx   |
| นาย สุดหล่อ ในจักรวาล    | Mr.          | Sudlor   | Naijakaval   | นักบัญชี            | Accountant |         | บัญชี     | บริษัท ขายขำ จำกัด (มหาชน)  | user3@domain.com  | 02xxxxxxx   |
```
