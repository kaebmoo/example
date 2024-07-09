การสร้างแอปพลิเคชัน Flutter ที่มีฟอร์มล็อกอินและการจัดการผู้ใช้โดยใช้ SQLite สามารถทำได้ตามขั้นตอนต่อไปนี้:

1. **ติดตั้ง dependencies**:
   คุณต้องเพิ่ม `sqflite` และ `path` dependencies ในไฟล์ `pubspec.yaml` ของโปรเจคของคุณ:

   ```yaml
   dependencies:
     flutter:
       sdk: flutter
     sqflite: ^2.0.0+4
     path: ^1.8.0
   ```

2. **สร้างฐานข้อมูล**:
   สร้างไฟล์ `database_helper.dart` สำหรับการจัดการ SQLite:

   ```dart
   import 'package:sqflite/sqflite.dart';
   import 'package:path/path.dart';

   class DatabaseHelper {
     static final DatabaseHelper _instance = DatabaseHelper.internal();
     factory DatabaseHelper() => _instance;

     static Database? _db;

     Future<Database> get db async {
       if (_db != null) {
         return _db!;
       }
       _db = await initDb();
       return _db!;
     }

     DatabaseHelper.internal();

     initDb() async {
       String databasesPath = await getDatabasesPath();
       String path = join(databasesPath, 'users.db');
       
       var db = await openDatabase(path, version: 1, onCreate: _onCreate);
       return db;
     }

     void _onCreate(Database db, int newVersion) async {
       await db.execute(
         'CREATE TABLE User(id INTEGER PRIMARY KEY, username TEXT, password TEXT)'
       );
     }

     // CRUD operations here...
   }
   ```

3. **เพิ่มฟังก์ชันสำหรับการจัดการผู้ใช้**:
   เพิ่มฟังก์ชันสำหรับการเพิ่มและตรวจสอบผู้ใช้ใน `database_helper.dart`:

   ```dart
   class DatabaseHelper {
     // ... existing code ...

     Future<int> saveUser(Map<String, dynamic> user) async {
       var dbClient = await db;
       int res = await dbClient.insert("User", user);
       return res;
     }

     Future<Map<String, dynamic>?> getUser(String username, String password) async {
       var dbClient = await db;
       List<Map> res = await dbClient.query(
         "User",
         where: "username = ? AND password = ?",
         whereArgs: [username, password],
       );
       if (res.isNotEmpty) {
         return res.first as Map<String, dynamic>;
       }
       return null;
     }
   }
   ```

4. **สร้างฟอร์มล็อกอิน**:
   สร้างไฟล์ `login_page.dart` สำหรับฟอร์มล็อกอิน:

   ```dart
   import 'package:flutter/material.dart';
   import 'database_helper.dart';

   class LoginPage extends StatefulWidget {
     @override
     _LoginPageState createState() => _LoginPageState();
   }

   class _LoginPageState extends State<LoginPage> {
     final TextEditingController _usernameController = TextEditingController();
     final TextEditingController _passwordController = TextEditingController();
     final DatabaseHelper _databaseHelper = DatabaseHelper();

     void _login() async {
       String username = _usernameController.text;
       String password = _passwordController.text;

       var user = await _databaseHelper.getUser(username, password);
       if (user != null) {
         // Handle successful login
         ScaffoldMessenger.of(context).showSnackBar(
           SnackBar(content: Text('Login Successful')),
         );
       } else {
         // Handle login error
         ScaffoldMessenger.of(context).showSnackBar(
           SnackBar(content: Text('Invalid Username or Password')),
         );
       }
     }

     @override
     Widget build(BuildContext context) {
       return Scaffold(
         appBar: AppBar(title: Text('Login')),
         body: Padding(
           padding: const EdgeInsets.all(16.0),
           child: Column(
             children: [
               TextField(
                 controller: _usernameController,
                 decoration: InputDecoration(labelText: 'Username'),
               ),
               TextField(
                 controller: _passwordController,
                 decoration: InputDecoration(labelText: 'Password'),
                 obscureText: true,
               ),
               SizedBox(height: 20),
               ElevatedButton(
                 onPressed: _login,
                 child: Text('Login'),
               ),
             ],
           ),
         ),
       );
     }
   }
   ```

5. **สร้างหน้า register สำหรับผู้ใช้ใหม่**:
   คุณสามารถสร้างหน้า register เช่นเดียวกันกับหน้า login:

   ```dart
   import 'package:flutter/material.dart';
   import 'database_helper.dart';

   class RegisterPage extends StatefulWidget {
     @override
     _RegisterPageState createState() => _RegisterPageState();
   }

   class _RegisterPageState extends State<RegisterPage> {
     final TextEditingController _usernameController = TextEditingController();
     final TextEditingController _passwordController = TextEditingController();
     final DatabaseHelper _databaseHelper = DatabaseHelper();

     void _register() async {
       String username = _usernameController.text;
       String password = _passwordController.text;

       Map<String, dynamic> user = {
         'username': username,
         'password': password,
       };

       int id = await _databaseHelper.saveUser(user);
       if (id != null) {
         // Handle successful registration
         ScaffoldMessenger.of(context).showSnackBar(
           SnackBar(content: Text('Registration Successful')),
         );
       } else {
         // Handle registration error
         ScaffoldMessenger.of(context).showSnackBar(
           SnackBar(content: Text('Registration Failed')),
         );
       }
     }

     @override
     Widget build(BuildContext context) {
       return Scaffold(
         appBar: AppBar(title: Text('Register')),
         body: Padding(
           padding: const EdgeInsets.all(16.0),
           child: Column(
             children: [
               TextField(
                 controller: _usernameController,
                 decoration: InputDecoration(labelText: 'Username'),
               ),
               TextField(
                 controller: _passwordController,
                 decoration: InputDecoration(labelText: 'Password'),
                 obscureText: true,
               ),
               SizedBox(height: 20),
               ElevatedButton(
                 onPressed: _register,
                 child: Text('Register'),
               ),
             ],
           ),
         ),
       );
     }
   }
   ```

6. **แก้ไข main.dart**:
   สุดท้ายให้แก้ไขไฟล์ `main.dart` เพื่อให้สามารถเรียกใช้หน้า login และ register ได้:

   ```dart
   import 'package:flutter/material.dart';
   import 'login_page.dart';
   import 'register_page.dart';

   void main() => runApp(MyApp());

   class MyApp extends StatelessWidget {
     @override
     Widget build(BuildContext context) {
       return MaterialApp(
         title: 'Flutter Login',
         theme: ThemeData(
           primarySwatch: Colors.blue,
         ),
         home: LoginPage(),
         routes: {
           '/login': (context) => LoginPage(),
           '/register': (context) => RegisterPage(),
         },
       );
     }
   }
   ```

เพียงเท่านี้คุณก็จะได้แอปพลิเคชัน Flutter ที่มีฟอร์มล็อกอินและการจัดการผู้ใช้โดยใช้ SQLite แล้วครับ หากมีข้อสงสัยหรือต้องการคำแนะนำเพิ่มเติม โปรดแจ้งให้ทราบได้ครับ
