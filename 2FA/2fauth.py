from flask import Flask, request, jsonify, send_file
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import pyotp
import qrcode
import io
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import os

app = Flask(__name__)

# Configuration
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'super-secret-key-change-me')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=10)
jwt = JWTManager(app)

# Database configuration for XAMPP
db_config = {
    'host': 'localhost',
    'user': 'root',          
    'password': '',         
    'database': 'crud' 
}

# In-memory storage for 2FA secrets (for demo purposes)
user_secrets = {}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# User Registration Endpoint
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    username = data.get('username')
    password = data.get('password')

    if not name or not username or not password:
        return jsonify({'message': 'Name, username and password are required'}), 400

    hashed_password = generate_password_hash(password)
    
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            
            # Check if username already exists
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                return jsonify({'message': 'Username already exists'}), 400
            
            # Insert new user
            cursor.execute(
                "INSERT INTO users (name, username, password) VALUES (%s, %s, %s)",
                (name, username, hashed_password)
            )
            connection.commit()
            return jsonify({'message': 'User registered successfully'}), 201
    except Error as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Database error'}), 500
    finally:
        if connection:
            connection.close()

# Generate 2FA QR Code
@app.route('/generate-2fa/<username>', methods=['GET'])
def generate_2fa(username):
    # Verify user exists
    connection = get_db_connection()
    if not connection:
        return jsonify({'message': 'Database connection error'}), 500
    
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        if not cursor.fetchone():
            return jsonify({'message': 'User not found'}), 404
        
        # Generate a new secret key for the user
        secret = pyotp.random_base32()
        user_secrets[username] = secret  # Store in memory (use DB in production)

        # Create provisioning URI for the user
        uri = pyotp.totp.TOTP(secret).provisioning_uri(name=username, issuer_name='SecureFlaskAPI')

        # Generate QR code
        qr = qrcode.make(uri)
        img = io.BytesIO()
        qr.save(img)
        img.seek(0)

        return send_file(img, mimetype='image/png')
    finally:
        connection.close()

# Verify 2FA Code
@app.route('/verify-2fa/<username>', methods=['POST'])
def verify_2fa(username):
    user_code = request.json.get('code')
    secret = user_secrets.get(username)

    if not secret:
        return jsonify({'message': 'User not found or 2FA not set up'}), 404

    totp = pyotp.TOTP(secret)
    if totp.verify(user_code):
        return jsonify({'message': '2FA verified successfully'})
    else:
        return jsonify({'message': 'Invalid or expired code'}), 401

# Login Endpoint with JWT Token Generation
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    code = data.get('code')  # 2FA code

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({'message': 'Database connection error'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if not user or not check_password_hash(user['password'], password):
            return jsonify({'message': 'Invalid credentials'}), 401

        # Verify 2FA code if user has it set up
        if username in user_secrets:
            if not code:
                return jsonify({'message': '2FA code required'}), 401
            
            totp = pyotp.TOTP(user_secrets[username])
            if not totp.verify(code):
                return jsonify({'message': 'Invalid 2FA code'}), 401

        # Create JWT token
        access_token = create_access_token(identity=username)
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token
        }), 200
    finally:
        connection.close()

# Protected CRUD Endpoints for Products
@app.route('/products', methods=['GET'])
@jwt_required()
def get_products():
    connection = get_db_connection()
    if not connection:
        return jsonify({'message': 'Database connection error'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        return jsonify(products), 200
    finally:
        connection.close()

@app.route('/products', methods=['POST'])
@jwt_required()
def add_product():
    data = request.get_json()
    pname = data.get('pname')
    description = data.get('description')
    price = data.get('price')
    stock = data.get('stock')

    if not pname or not price or not stock:
        return jsonify({'message': 'Product name, price and stock are required'}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({'message': 'Database connection error'}), 500
    
    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO products (pname, description, price, stock) VALUES (%s, %s, %s, %s)",
            (pname, description, price, stock)
        )
        connection.commit()
        return jsonify({'message': 'Product added successfully'}), 201
    finally:
        connection.close()

@app.route('/products/<int:pid>', methods=['PUT'])
@jwt_required()
def update_product(pid):
    data = request.get_json()
    pname = data.get('pname')
    description = data.get('description')
    price = data.get('price')
    stock = data.get('stock')

    connection = get_db_connection()
    if not connection:
        return jsonify({'message': 'Database connection error'}), 500
    
    try:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE products SET pname = %s, description = %s, price = %s, stock = %s WHERE pid = %s",
            (pname, description, price, stock, pid)
        )
        connection.commit()
        if cursor.rowcount == 0:
            return jsonify({'message': 'Product not found'}), 404
        return jsonify({'message': 'Product updated successfully'}), 200
    finally:
        connection.close()

@app.route('/products/<int:pid>', methods=['DELETE'])
@jwt_required()
def delete_product(pid):
    connection = get_db_connection()
    if not connection:
        return jsonify({'message': 'Database connection error'}), 500
    
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM products WHERE pid = %s", (pid,))
        connection.commit()
        if cursor.rowcount == 0:
            return jsonify({'message': 'Product not found'}), 404
        return jsonify({'message': 'Product deleted successfully'}), 200
    finally:
        connection.close()

if __name__ == '__main__':
    app.run(debug=True)