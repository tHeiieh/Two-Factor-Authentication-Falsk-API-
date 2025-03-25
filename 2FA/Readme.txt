📌 Required Libraries (Install Before Running)
Run the following command in your terminal to install all required libraries:

bash
Copy
Edit
pip install flask flask_sqlalchemy flask_bcrypt flask_jwt_extended pymysql
📌 How to Run the Flask App
Ensure MySQL is running (if using phpMyAdmin, start Apache and MySQL from XAMPP).
Create the database by running:
sql
Copy
Edit
CREATE DATABASE crud;
Update database connection in crud.py (if needed).
Run the Flask app:
bash
Copy
Edit
python crud.py
The API will start at http://127.0.0.1:5000.
📌 Database Schema (MySQL)
sql
Copy
Edit
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE products (
    pid INT AUTO_INCREMENT PRIMARY KEY,
    pname VARCHAR(100) NOT NULL,
    description TEXT,
    price FLOAT NOT NULL,
    stock INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
📌 Using Postman to Test API
1️⃣ User Signup
URL: http://127.0.0.1:5000/signup
Method: POST
Headers:
pgsql
Copy
Edit
Content-Type: application/json
Body (JSON):
json
Copy
Edit
{
  "name": "John Doe",
  "username": "johndoe",
  "password": "password123"
}
Response:
json
Copy
Edit
{
  "message": "User registered successfully"
}
2️⃣ User Login
URL: http://127.0.0.1:5000/login
Method: POST
Headers:
pgsql
Copy
Edit
Content-Type: application/json
Body (JSON):
json
Copy
Edit
{
  "username": "johndoe",
  "password": "password123"
}
Response (with Token):
json
Copy
Edit
{
  "token": "your_jwt_token_here"
}
3️⃣ Add Product (Requires JWT)
URL: http://127.0.0.1:5000/products
Method: POST
Headers:
pgsql
Copy
Edit
Content-Type: application/json
Authorization: Bearer your_jwt_token_here
Body (JSON):
json
Copy
Edit
{
  "pname": "Laptop",
  "description": "Gaming laptop with 16GB RAM",
  "price": 1200.50,
  "stock": 10
}
Response:
json
Copy
Edit
{
  "message": "Product added successfully"
}
4️⃣ Get All Products (Requires JWT)
URL: http://127.0.0.1:5000/products
Method: GET
Headers:
makefile
Copy
Edit
Authorization: Bearer your_jwt_token_here
Response:
json
Copy
Edit
[
  {
    "id": 1,
    "name": "Laptop",
    "price": 1200.50,
    "stock": 10
  }
]
5️⃣ Update Product (Requires JWT)
URL: http://127.0.0.1:5000/products/1
Method: PUT
Headers:
pgsql
Copy
Edit
Content-Type: application/json
Authorization: Bearer your_jwt_token_here
Body (JSON):
json
Copy
Edit
{
  "pname": "Gaming Laptop",
  "description": "Updated description",
  "price": 1500.75,
  "stock": 8
}
Response:
json
Copy
Edit
{
  "message": "Product updated successfully"
}
6️⃣ Delete Product (Requires JWT)
URL: http://127.0.0.1:5000/products/1
Method: DELETE
Headers:
makefile
Copy
Edit
Authorization: Bearer your_jwt_token_here
Response:
json
Copy
Edit
{
  "message": "Product deleted successfully"
}