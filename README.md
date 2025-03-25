Flask API with JWT Authentication & 2FA 🔒
A secure REST API built with Flask featuring:

User registration/login

Two-Factor Authentication (2FA) via Google Authenticator

JWT token-based authorization

Protected CRUD operations for products

Technologies Used 🛠️
Python 

Flask

MySQL (XAMPP)

PyOTP (2FA)

JWT (Authentication)

QRcode (for 2FA setup)

Prerequisites 📋
XAMPP (for MySQL database)

Python 3.x

Google Authenticator App (iOS/Android)

Setup Instructions ⚙️

1. Create a Virtual Environment (Recommended)
bash
Copy
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
2.install Dependencies
bash
Copy
pip install -r requirements.txt
3. Database Setup
Start XAMPP and run Apache + MySQL.

Create a database named secure_api in phpMyAdmin (http://localhost/phpmyadmin).

Execute these SQL queries:

sql
Copy
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE products (
    pid INT AUTO_INCREMENT PRIMARY KEY,
    pname VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
4. Configure Environment Variables
Create a .env file:

env

JWT_SECRET_KEY=your_super_secret_key
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=secure_api
How to Run 🚀
bash

python app.py
The API will start at http://localhost:5000.

API Endpoints 🌐
Endpoint	Method	Description	Auth Required
/register	POST	Register a new user	❌
/login	POST	Login with username/password + 2FA	❌
/generate-2fa/<username>	GET	Generate QR code for 2FA setup	❌
/products	GET	Get all products	✅
/products	POST	Add a new product	✅
/products/<pid>	PUT	Update a product	✅
/products/<pid>	DELETE	Delete a product	✅
Usage Examples 📖
1. Register a User
bash
Copy
curl -X POST http://localhost:5000/register \
-H "Content-Type: application/json" \
-d '{"name": "John Doe", "username": "johndoe", "password": "password123"}'
2. Set Up 2FA
Generate QR code:

bash
Copy
curl -X GET http://localhost:5000/generate-2fa/johndoe --output qrcode.png
Scan the QR code in Google Authenticator.

3. Login (with 2FA)
bash
Copy
curl -X POST http://localhost:5000/login \
-H "Content-Type: application/json" \
-d '{"username": "johndoe", "password": "password123", "code": "123456"}'
Response includes a JWT token for authenticated requests.

4. Get All Products (Authenticated)
bash
Copy
curl -X GET http://localhost:5000/products \
-H "Authorization: Bearer YOUR_JWT_TOKEN"
Testing with Postman 🧪
Import the included Flask-JWT-2FA-API.postman_collection.json.

Set environment variables for:

base_url: http://localhost:5000

jwt_token: (from login)

Troubleshooting 🔧
MySQL Connection Issues: Ensure XAMPP's MySQL is running.

ModuleNotFoundError: Run pip install -r requirements.txt.

405 Method Not Allowed: Check if you're using the correct HTTP method.
