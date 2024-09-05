from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from cryptography.fernet import Fernet, InvalidToken
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
db = SQLAlchemy(app)

# สร้างและจัดเก็บกุญแจสำหรับการเข้ารหัส
key = os.environ.get('ENCRYPTION_KEY', b'Ip25ysJq34oozqE9rZcWexW67TJCEe3US59jZN_TXyM=')
cipher = Fernet(key)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column("name", db.LargeBinary, nullable=False)
    _surname = db.Column("surname", db.LargeBinary, nullable=False)
    _email = db.Column("email", db.LargeBinary, nullable=False)

    @property
    def name(self):
        try:
            return cipher.decrypt(self._name).decode('utf-8')
        except InvalidToken:
            return None

    @name.setter
    def name(self, value):
        self._name = cipher.encrypt(value.encode('utf-8'))

    @property
    def surname(self):
        try:
            return cipher.decrypt(self._surname).decode('utf-8')
        except InvalidToken:
            return None

    @surname.setter
    def surname(self, value):
        self._surname = cipher.encrypt(value.encode('utf-8'))

    @property
    def email(self):
        try:
            return cipher.decrypt(self._email).decode('utf-8')
        except InvalidToken:
            return None

    @email.setter
    def email(self, value):
        self._email = cipher.encrypt(value.encode('utf-8'))

# สร้าง context สำหรับแอปพลิเคชัน
with app.app_context():
    db.create_all()

@app.route('/add_user')
def add_user():
    user = User(name="John", surname="Doe", email="john.doe@example.com")
    db.session.add(user)
    db.session.commit()
    return "User added!"

@app.route('/get_user/<int:user_id>')
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if None in [user.name, user.surname, user.email]:
        return jsonify({"error": "Unable to decrypt user data"}), 500
    
    return jsonify({
        "name": user.name,
        "surname": user.surname,
        "email": user.email
    })

if __name__ == "__main__":
    app.run(debug=True, port=9000)
