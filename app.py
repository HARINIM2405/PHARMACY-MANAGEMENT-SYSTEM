from flask import Flask, jsonify, render_template, request
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
from twilio.rest import Client # type: ignore

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Twilio configuration
TWILIO_ACCOUNT_SID = os.getenv('AC0ab1016261b84e9f90d9c467fa5b0983')
TWILIO_AUTH_TOKEN = os.getenv('a855157a36a4c79e3efd1b7e4a032cba')
TWILIO_PHONE_NUMBER = os.getenv('+13343759877')

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Database connection function
def create_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "22-Feb-05"),
            database=os.getenv("DB_NAME", "Pharmacydb")
        )
        if connection.is_connected():
            print("Connected to MySQL database")
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None

# Function to drop tables if they exist
def drop_tables(connection):
    try:
        cursor = connection.cursor()
        drop_table_queries = """
        DROP TABLE IF EXISTS Bill;
        DROP TABLE IF EXISTS Medicine;
        DROP TABLE IF EXISTS Employee;
        DROP TABLE IF EXISTS `Ordered Drugs`;
        DROP TABLE IF EXISTS Customer;
        DROP TABLE IF EXISTS VendorStock;
        """
        for query in drop_table_queries.split(';'):
            if query.strip():
                cursor.execute(query)
        connection.commit()
        cursor.close()
        print("Existing tables dropped successfully")
    except Error as e:
        print(f"Error dropping tables: {e}")

# Function to create tables
def create_tables(connection):
    try:
        cursor = connection.cursor()

        create_table_queries = """
        CREATE TABLE Customer (
            id              INT NOT NULL AUTO_INCREMENT, 
            `Name`          VARCHAR(255) NOT NULL, 
            Phone           BIGINT NOT NULL UNIQUE,
            address         VARCHAR(20),
            PRIMARY KEY (id)
        );

        CREATE TABLE `Ordered Drugs` (
            `Order ID`            INT NOT NULL AUTO_INCREMENT, 
            `Batch Number`        INT NOT NULL, 
            `Drug Name`           VARCHAR(255) NOT NULL,  
            `Ordered Quantity`    INT NOT NULL, 
            Price                 DECIMAL(10, 2) NOT NULL, 
            customerID            INT,
            CONSTRAINT fk_customer FOREIGN KEY (customerID) REFERENCES Customer(id),
            PRIMARY KEY (`Order ID`, `Drug Name`, `Batch Number`)
        );

        CREATE TABLE Employee (
            ID                INT NOT NULL AUTO_INCREMENT, 
            `Name`            VARCHAR(255) NOT NULL, 
            Role              VARCHAR(255) NOT NULL, 
            Salary            DECIMAL(10, 2) NOT NULL, 
            `Phone Number`    BIGINT NOT NULL, 
            PRIMARY KEY (ID)
        );

        CREATE TABLE Medicine (
            `Drug Name`       VARCHAR(255) NOT NULL, 
            `Batch Number`    INT NOT NULL, 
            MedicineType      VARCHAR(255) NOT NULL, 
            Manufacturer      VARCHAR(255) NOT NULL, 
            `Stock Quantity`  INT NOT NULL, 
            `Expiry Date`     DATE NOT NULL, 
            Price             DECIMAL(10, 2) NOT NULL, 
            PRIMARY KEY (`Drug Name`, `Batch Number`)
        );

        CREATE TABLE Bill (
            `Order ID`            INT NOT NULL, 
            `CustomerSSN`         INT NOT NULL, 
            `Total Amount`        DECIMAL(10, 2) NOT NULL, 
            `Customer Payment`    DECIMAL(10, 2) NOT NULL, 
            PRIMARY KEY (`Order ID`, `CustomerSSN`)
        );

        CREATE TABLE VendorStock (
            `Drug Name`       VARCHAR(255) NOT NULL, 
            `Batch Number`    INT NOT NULL, 
            `Vendor Name`     VARCHAR(255) NOT NULL, 
            `Stock Quantity`  INT NOT NULL,
            PRIMARY KEY (`Drug Name`, `Batch Number`, `Vendor Name`)
        );
        """

        for query in create_table_queries.split(';'):
            if query.strip():
                cursor.execute(query)

        connection.commit()
        cursor.close()
        print("Tables created successfully")
    except Error as e:
        print(f"Error creating tables: {e}")

# Function to insert dummy data
def insert_dummy_data(connection):
    try:
        cursor = connection.cursor()
        
        # Insert dummy values into Customer table
        customer_values = [
            (1, 'John', +919894361046, '123 Main St'),
            (2, 'Jane',+919894361046, '456 Elm St'),
            (3, 'Alice', +919894361046, '789 Oak St'),
            (4, 'Bob', +919894361046, '101 Pine St'),
            (5, 'Emily', +919894361046, '202 Cedar St')
        ]
        cursor.executemany("INSERT INTO Customer (id, `Name`, Phone, address) VALUES (%s, %s, %s, %s)", customer_values)

        # Insert dummy values into Ordered Drugs table
        ordered_drugs_values = [
            (100, 1, 'Drug A', 5, 25.00, 1),
            (101, 2, 'Drug B', 10, 50.00, 1),
            (102, 3, 'Drug C', 5, 37.50, 2),
            (103, 4, 'Drug D', 15, 225.00, 2),
            (104, 5, 'Drug E', 10, 250.00, 2)
        ]
        cursor.executemany("INSERT INTO `Ordered Drugs` (`Order ID`, `Batch Number`, `Drug Name`, `Ordered Quantity`, Price, customerID) VALUES (%s, %s, %s, %s, %s, %s)", ordered_drugs_values)

        # Insert dummy values into Employee table
        employee_values = [
            (1001, 'Alice', 'Pharmacist', 55000.00, 1234567890),
            (1002, 'Bob', 'Pharmacy Technician', 45000.00, 9876543210),
            (1003, 'Charlie', 'Pharmacist', 60000.00, 5556667777)
        ]
        cursor.executemany("INSERT INTO Employee (ID, `Name`, Role, Salary, `Phone Number`) VALUES (%s, %s, %s, %s, %s)", employee_values)

        # Insert dummy values into Medicine table
        medicine_values = [
            ('Drug A', 1, 'Tablet', 'Manufacturer A', 100, '2024-12-31', 5.00),
            ('Drug B', 2, 'Capsule', 'Manufacturer B', 150, '2023-10-15', 7.50),
            ('Drug C', 3, 'Syrup', 'Manufacturer C', 200, '2025-06-30', 10.00)
        ]
        cursor.executemany("INSERT INTO Medicine (`Drug Name`, `Batch Number`, MedicineType, Manufacturer, `Stock Quantity`, `Expiry Date`, Price) VALUES (%s, %s, %s, %s, %s, %s, %s)", medicine_values)

        # Insert dummy values into Bill table
        bill_values = [
            (10001, 123456789, 100.00, 80.00),
            (10002, 987654321, 75.00, 60.00),
            (10003, 111111111, 120.00, 100.00)
        ]
        cursor.executemany("INSERT INTO Bill (`Order ID`, `CustomerSSN`, `Total Amount`, `Customer Payment`) VALUES (%s, %s, %s, %s)", bill_values)

        # Insert dummy values into VendorStock table
        vendor_stock_values = [
            ('Drug A', 1, 'Vendor X', 50),
            ('Drug B', 2, 'Vendor Y', 75),
            ('Drug C', 3, 'Vendor Z', 100)
        ]
        cursor.executemany("INSERT INTO VendorStock (`Drug Name`, `Batch Number`, `Vendor Name`, `Stock Quantity`) VALUES (%s, %s, %s, %s)", vendor_stock_values)

        # Commit the transaction
        connection.commit()
        print("Dummy data inserted successfully")
    except Error as e:
        print(f"Error inserting dummy data: {e}")

# Main function
connection = create_connection()
if connection:
    drop_tables(connection)
    create_tables(connection)
    insert_dummy_data(connection)
    connection.close()
    print("MySQL connection is closed")

@app.route('/')
def index():
    return render_template('index.html')

# Route to fetch and return stocked drugs data in JSON format
@app.route('/stocked-drugs')
def get_stocked_drugs():
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Medicine")
    stocked_drugs_data = cursor.fetchall()
    connection.close()
    return jsonify(stocked_drugs_data)    


# Route to fetch customer count data for monthly analysis in JSON format
@app.route('/add-stock', methods=['POST'])
def add_stock():
    data = request.get_json()
    drug_name = data['drug_name']
    batch_number = data['batch_number']
    medicine_type = data['medicine_type']
    manufacturer = data['manufacturer']
    stock_quantity = data['stock_quantity']
    expiry_date = data['expiry_date']
    price = data['price']

    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO Medicine (`Drug Name`, `Batch Number`, MedicineType, Manufacturer, `Stock Quantity`, `Expiry Date`, Price)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (drug_name, batch_number, medicine_type, manufacturer, stock_quantity, expiry_date, price))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({'message': 'Stock added successfully'}), 200




# Route to generate bill for a customer
@app.route('/generate-bill', methods=['POST'])
def generate_bill():
    data = request.get_json()
    customer_id = data['customer_id']
    order_id = data['order_id']
    total_amount = data['total_amount']
    customer_payment = data['customer_payment']

    # Assuming you have a function to calculate the bill details
    # Here, we'll just print them
    print(f"Customer ID: {customer_id}")
    print(f"Order ID: {order_id}")
    print(f"Total Amount: {total_amount}")
    print(f"Customer Payment: {customer_payment}")

    # Sending message to customer
    try:
        message_body = f"Your bill details: Order ID: {order_id}, Total Amount: {total_amount}, Customer Payment: {customer_payment}"
        message = client.messages.create(
            body=message_body,
            from_=+13343759877,
            to=+919894361046
        )
        print(f"Message sent to {(+919894361046)}")
        return jsonify({'message': 'Bill generated and message sent successfully'}), 200
    except Exception as e:
        print(f"Error sending message: {e}")
        return jsonify({'message': 'Error generating bill and sending message'}), 500
@app.route('/show-tables')
def show_tables():
    connection = create_connection()
    cursor = connection.cursor(dictionary=True)

    # Get the list of tables
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

    # Create a dictionary to store table data
    table_data = {}

    for table in tables:
        table_name = list(table.values())[0]
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        table_data[table_name] = rows

    connection.close()
    return jsonify(table_data)

if __name__ == '__main__':
    app.run(debug=True)