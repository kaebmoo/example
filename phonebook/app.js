require('dotenv').config();
const express = require('express');
const bodyParser = require('body-parser');
const fs = require('fs');
const csv = require('csv-parser');
const axios = require('axios');
const path = require('path');
const nodemailer = require('nodemailer');
const writeFileAtomic = require('write-file-atomic');
const rateLimit = require('express-rate-limit');

const app = express();
app.use(bodyParser.json());


const registeredUsersFile = path.join(__dirname, 'registeredUsers.json');

const limiter = rateLimit({
  windowMs: 1 * 60 * 1000, // 15 minutes
  max: 2400, // limit each IP to 2400 requests per windowMs
});
/* 
สำหรับผู้ใช้งาน 12,000 คน โอกาสในการใช้งานต่อนาทีเท่ากับ 20%
จำนวนผู้ใช้ที่ใช้งานในหนึ่งนาที = 12,000 * 0.2 = 2,400 คน 
สมมติว่าผู้ใช้แต่ละคนสามารถส่งคำขอได้ 1 ครั้งในหนึ่งนาที (สามารถปรับได้ตามความเป็นจริง) ดังนั้น จำนวนคำขอทั้งหมดในหนึ่งนาที = 2,400 * 1 = 2,400 requests
windowMs เป็น 1 นาที (60 * 1000 ms), จำนวน requests ที่เหมาะสมต่อ 1 นาที = 2,400 requests
*/
app.use(limiter); // apply to all requests

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// ฟังก์ชันอ่านข้อมูลจากไฟล์ JSON
function loadRegisteredUsers() {
  try {
      if (fs.existsSync(registeredUsersFile)) {
          const data = fs.readFileSync(registeredUsersFile, 'utf8');
          if (data.trim() === '') {
              return new Map(); // ถ้าไฟล์ JSON ว่างเปล่า ให้คืนค่า Map ว่าง
          }
          return new Map(JSON.parse(data));
      } else {
          return new Map(); // ถ้าไฟล์ JSON ไม่มีอยู่ ให้คืนค่า Map ว่าง
      }
  } catch (error) {
      console.error(`Error reading JSON file: ${error}`);
      return new Map(); // หรือสามารถเพิ่มการจัดการข้อผิดพลาดเพิ่มเติมตามที่ต้องการ
  }
}

// ฟังก์ชันเขียนข้อมูลลงไฟล์ JSON อย่างปลอดภัย
function saveRegisteredUsers() {
  writeFileAtomic(registeredUsersFile, JSON.stringify([...registeredUsers]), (err) => {
    if (err) {
      console.error('Error writing file:', err);
    } else {
      console.log('File saved successfully.');
    }
  });
}


// โหลดข้อมูลผู้ใช้ที่ลงทะเบียนเมื่อเริ่มต้นแอปพลิเคชัน
const registeredUsers = loadRegisteredUsers();

// ฟังก์ชันสำหรับสร้างรหัสสุ่ม
function generateRandomCode(length) {
  const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += characters.charAt(Math.floor(Math.random() * characters.length));
  }
  return result;
}

// ฟังก์ชันสำหรับส่งอีเมล
async function sendActivationEmail(email, activationCode) {
    // กำหนดค่าการเชื่อมต่อกับเซิร์ฟเวอร์ SMTP ของคุณ
    const transporter = nodemailer.createTransport({
      host: 'smtp-relay.gmail.com', // ระบุ hostname ของเซิร์ฟเวอร์ SMTP ของคุณ
      port: 25, // หรือ port ที่เซิร์ฟเวอร์ SMTP ของคุณใช้
      secure: false, // ใช้ true หากต้องการเชื่อมต่อแบบ SSL/TLS
      auth: {
        user: process.env.EMAIL_USER, // อีเมลที่ใช้ส่ง
        pass: process.env.EMAIL_PASS // รหัสผ่านของอีเมล
      }
    });
  
    // ตั้งค่าเนื้อหาอีเมล
    const mailOptions = {
      from: 'noreply@example.com',
      to: email,
      subject: 'Activation Code for Your Telegram Bot',
      text: `Your activation code is: ${activationCode} (สามารถใช้คำสั่งใน bot ดังนี้: /activate ${activationCode})`
    };
  
    // ส่งอีเมล 
    try {
      const info = await transporter.sendMail(mailOptions);
      console.log('Email sent: ' + info.response);
    } catch (error) {
      console.error('Error sending email: ', error);
      throw error; // โยนข้อผิดพลาดเพื่อให้การส่งข้อความไปยัง Telegram ว่ามีปัญหา
    }
  }


const file = process.env.YOUR_CSV_FILE;

// อ่านข้อมูลจาก CSV
let contacts = [];
fs.createReadStream(file)
  .pipe(csv())
  .on('data', (row) => {
    contacts.push(row);
  })
  .on('end', () => {
    console.log('CSV file successfully processed');
  })
  .on('error', (error) => {
    console.error('Error reading CSV:', error); 
  });

// ฟังก์ชันค้นหาข้อมูล
function searchContact(query) {
  return contacts.filter(contact => {
    return contact['ชื่อ-นามสกุล'].includes(query) ||
           contact['e-mail'].includes(query) ||
           contact['โทรศัพท์'].includes(query) ||
           contact['มือถือ'].includes(query) ||
           contact['ต.บริหาร'].includes(query) ||
           contact['ส่วนงาน'].includes(query) ||
           contact['ชื่อเต็มส่วนงาน'].includes(query);
  });
}

// ฟังก์ชันส่งข้อความไปยัง Telegram Bot
async function sendToTelegram(chatId, text) {
    if (!isDebugMode) {
        const token = process.env.YOUR_TELEGRAM_BOT_TOKEN; // อ่านค่า token จาก environment variable
        const url = `https://api.telegram.org/bot${token}/sendMessage`;
    
        try {
        const response = await axios.post(url, {
            chat_id: chatId,
            text: text
        });
        console.log('Message sent: ', response.data);
        } catch (error) {
        console.error('Error sending message: ', error);
        }
    } else {
        console.log(`Debug message to ${chatId}: \n${text}`);
    }
  }

// Define an async function to send messages with delay
async function sendMessagesWithDelay(chatId, messages) {
  for (const message of messages) {
    sendToTelegram(chatId, message);
    await sleep(200); // Delay for 200 milliseconds
  }
}

// ฟังก์ชันแบ่งข้อความเป็นส่วนย่อย
function splitMessage(text, maxLength) {
    const parts = [];
    let currentPart = '';
  
    text.split('\n').forEach(line => {
      if ((currentPart + line).length > maxLength) {
        if (currentPart) {
          parts.push(currentPart.trim());
        }
        currentPart = line + '\n';
        // ถ้า line ยาวเกิน maxLength ให้แยก line ออกเป็นหลายส่วน
        while (currentPart.length > maxLength) {
          parts.push(currentPart.slice(0, maxLength));
          currentPart = currentPart.slice(maxLength);
        }
      } else {
        currentPart += line + '\n';
      }
    });
  
    if (currentPart.trim().length > 0) {
      parts.push(currentPart.trim());
    }
  
    return parts;
  }
  
  

// กำหนดตัวแปรสภาพแวดล้อมสำหรับ debug mode
const isDebugMode = process.env.DEBUG_MODE === 'true';

const webhookUrl = process.env.WEBHOOK_URL;

app.post(`/webhook/${webhookUrl}`, async (req, res) => {
  const query = req.body.message.text;  // ดึงข้อความจาก Telegram

  const message = req.body.message;
  const chatId = message.chat.id;
  const userId = message.from.id;
  const text = message.text.trim();

  if (text === '/start') {
    await sendToTelegram(chatId, 'ยินดีต้อนรับสู่ bot ของเรา! \n/register email - เพื่อลงทะเบียน, \n/activate code - เพื่อยืนยันการลงทะเบียนตามรหัสที่ได้รับจาก email');
  }

  if (text.startsWith('/register ')) {
    const email = text.split(' ')[1];
    if (!email || !email.endsWith('@example.com')) {
      await sendToTelegram(chatId, 'กรุณาใส่อีเมลที่ถูกต้องและใช้ domain @example.com เท่านั้น');
      return res.sendStatus(200);
    }

    if (registeredUsers.has(userId.toString()) && registeredUsers.get(userId.toString()).activated) {
      await sendToTelegram(chatId, 'คุณได้ลงทะเบียนและยืนยันแล้ว สามารถใช้งาน bot ได้เลย');
      return res.sendStatus(200);
    }

    const activationCode = generateRandomCode(6);
    registeredUsers.set(userId.toString(), { email, activationCode, activated: false });
    saveRegisteredUsers();

    sendActivationEmail(email, activationCode)
      .then(() => {
        sendToTelegram(chatId, `อีเมลยืนยันได้ถูกส่งไปยัง ${email} กรุณาเช็ครหัสยืนยันจากอีเมลของคุณ`);
      })
      .catch(error => {
        console.error('Error sending email:', error);
        sendToTelegram(chatId, 'เกิดข้อผิดพลาดในการส่งอีเมลยืนยัน');
      });

    return res.sendStatus(200);
  }

  if (text.startsWith('/activate ')) {
    const code = text.split(' ')[1];
    const user = registeredUsers.get(userId.toString());

    if (!user) {
      await sendToTelegram(chatId, 'คุณยังไม่ได้ลงทะเบียน: \nสามารถลงทะเบียนโดยใช้ email ของคุณด้วยคำสั่ง /register email@address');
      return res.sendStatus(200);
    }

    if (user.activationCode === code) {
      user.activated = true;
      registeredUsers.set(userId.toString(), user);
      saveRegisteredUsers();
      await sendToTelegram(chatId, 'การยืนยันสำเร็จ คุณสามารถใช้งาน bot ได้แล้ว');
    } else {
      await sendToTelegram(chatId, 'รหัสยืนยันไม่ถูกต้อง');
    }

    return res.sendStatus(200);
  }

  const user = registeredUsers.get(userId.toString());
  if (!user || !user.activated) {
    await sendToTelegram(chatId, "คุณต้องลงทะเบียนและยืนยันด้วยรหัสที่ได้รับทาง email ก่อนจึงจะสามารถใช้งาน bot นี้ได้: \nด้วยคำสั่ง /register email@address\nและยืนยันด้วย code ที่ได้รับทาง email ด้วยคำสั่ง /activate code");
    return res.sendStatus(200);
  }

   // เพิ่มการตรวจสอบความยาวของ query
   if (text.length < 2) {
    await sendToTelegram(chatId, "กรุณาป้อนข้อความค้นหาที่มีความยาวอย่างน้อย 2 ตัวอักษร");
    return res.sendStatus(200);
  }

  if (/^\d+$/.test(text) && text.length < 9) {
    await sendToTelegram(chatId, "กรุณาป้อนหมายเลขที่มีความยาวอย่างน้อย 9 ตัวอักษร");
    return res.sendStatus(200);
  }

  if (text.includes("@example.com")) {
    await sendToTelegram(chatId, "ผลการค้นหามีมากเกินไป. กรุณาป้อนข้อความค้นหาที่เฉพาะเจาะจงมากขึ้น.");
    return res.sendStatus(200);
  }

  console.log('Received query:', text);
  let results;
  /* ขำ ขำ เอาฮา */
  if (text === "สุดหล่อ") {
    results = searchContact("นิวัตยะกุล");
  }
  else {
    results = searchContact(text);
  }
  
  const MAX_RESULTS = 100;
  if (results.length > MAX_RESULTS) {
    await sendToTelegram(chatId, `ผลการค้นหามีมากเกินไป (${results.length} รายการ). กรุณาป้อนข้อความค้นหาที่เฉพาะเจาะจงมากขึ้น.`);
    return res.sendStatus(200);
  }

  let responseText = "";

  if (results.length > 0) {
    results.forEach(row => {
      responseText += `ชื่อ: ${row['ชื่อ-นามสกุล']}\n`;
      responseText += `ชื่อ-อังกฤษ: ${row['ชื่อ-อังกฤษ']} ${row['นามสกุล-อังกฤษ']}\n`;
      responseText += `ตำแหน่ง: ${row['ตำแหน่ง']}\n`;
      responseText += `อีเมล: ${row['e-mail']}\n`;
      responseText += `ส่วนงาน: ${row['ชื่อเต็มส่วนงาน']}, ${row['ส่วนงาน']}\n`;
      responseText += `mobile: ${row['มือถือ']}\n`;
      responseText += `โทรศัพท์: ${row['โทรศัพท์']}\n\n`;
    });
    responseText += `พบข้อมูลที่ตรงกัน ${results.length} รายการ.\n\n`;
  } else {
    responseText = "ไม่พบข้อมูลที่ตรงกัน";
  }

  const messages = splitMessage(responseText, 4096);
  /*
  messages.forEach(message => {
    sendToTelegram(chatId, message);
  });
  */

  // Call the function with your chatId and messages. sendToTelegram
  sendMessagesWithDelay(chatId, messages);

  res.sendStatus(200);
});

app.listen(8181, () => {
  console.log('Server is running on port 8181');
});
