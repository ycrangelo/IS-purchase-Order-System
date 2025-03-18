from flask import Flask, render_template, session,request,jsonify, redirect, url_for

import mysql.connector

app = Flask(__name__, template_folder='pages')
app.secret_key = 'your_strong_random_secret_key_here'

# Function to connect to the MySQL database
def get_db_connection():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="pythonflask",  # Use the pythonflask database
        port=3305
    )
    return mydb

# Home route
@app.route('/')
def home():
    
    #  # Check if 'username' exists in the session
    # if 'username' in session or session['username'] != '':
    #     # If not logged in, redirect to the login page
    #     return redirect(url_for('auditlogs'))

    return render_template('login.html', show_sidebar=False)

# Login route to handle form submission
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('name')  # name field in form
    password = request.form.get('password')  # password field in form

    # Connect to the database
    mydb = get_db_connection()
    my_cursor = mydb.cursor()

    # Query the database to check if the credentials are correct
    my_cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = my_cursor.fetchone()  # Fetch a single row

    if user:  # If user is found
        print("inside validation, World!")
        session['username'] = user[3]  # Set session only if user is valid
        session['password'] = password
        my_cursor.execute("INSERT INTO auditLogs (username, did) VALUES (%s, %s)", (session['username'], "log in"))
        mydb.commit()
        return redirect(url_for('auditlogs'))  # Redirect to the audit logs page after successful login
    else:
        # If login fails, go back to the login page with an error message
        return render_template('login.html', error="Invalid username or password.")
    
    # Close the cursor and connection
    my_cursor.close()
    mydb.close()

# Audit logs route
@app.route('/auditLogs')
def auditlogs():
    # Check if 'username' exists in the session
    if 'username' not in session or session['username'] == '':
        # If not logged in, redirect to the login page
        return redirect(url_for('home'))

    # Connect to the database
    mydb = get_db_connection()
    my_cursor = mydb.cursor()

    # Query the database to get all audit logs
    my_cursor.execute("SELECT * FROM auditLogs ORDER BY created_at DESC")
    logs = my_cursor.fetchall()  # Fetch all rows

    # Format the date and time for each log entry
    formatted_logs = []
    for log in logs:
        # Assuming log[3] is the datetime field (created_at)
        log_date = log[3].strftime('%Y-%m-%d')  # Date in format YYYY-MM-DD
        log_time = log[3].strftime('%I:%M:%S %p')  # Time in 12-hour format with AM/PM
        
        formatted_logs.append((log[0], log[1], log[2], log_date, log_time))

    # Close cursor and database connection
    my_cursor.close()
    mydb.close()

    # Pass the formatted logs to the template
    return render_template('auditlogs.html', logs=formatted_logs, show_sidebar=True)

# Inventory route
@app.route('/inventory', methods=['GET', 'POST'])
def inventory():
    # Connect to the database
    mydb = get_db_connection()
    my_cursor = mydb.cursor()
    
    # Check if 'username' exists in the session
    if 'username' not in session or session['username'] == '':
        # If not logged in, redirect to the login page
        return redirect(url_for('home'))
    
    # Handle POST request (form submission)
    if request.method == 'POST':
        # Process form data
        code_id = request.form.get('codeId')
        description = request.form.get('description')
        location = request.form.get('location')
        quantity = request.form.get('quantity')
        my_cursor.execute("INSERT INTO inventory (code_id, desription, location, quantity) VALUES (%s, %s, %s, %s)", 
                          (code_id, description, location, quantity))
        my_cursor.execute("INSERT INTO auditLogs (username, did) VALUES (%s, %s)", 
                          (session['username'], f"Added in Inventory with code ID: {code_id}, Description: {description}"))
        mydb.commit()
    
    # Fetch inventory data for both GET and POST requests
    my_cursor.execute("SELECT * FROM inventory ORDER BY created_at DESC")
    logs = my_cursor.fetchall()  # Fetch all rows

    # Format the date and time for each log entry
    formatted_logs = []
    for log in logs:
        # Assuming log[5] is the datetime field (created_at)
        log_date = log[5].strftime('%Y-%m-%d')  # Date in format YYYY-MM-DD
        log_time = log[5].strftime('%I:%M:%S %p')  # Time in 12-hour format with AM/PM
        
        formatted_logs.append((log[0], log[1], log[2], log[3], log[4], log_date, log_time,session['username']))

    # Close cursor and database connection
    my_cursor.close()
    mydb.close()

    # Pass the formatted logs to the template
    return render_template('inventory.html', logs=formatted_logs, show_sidebar=True)
# Logout route
@app.route('/logout')
def logout():
    # Clear the session
    session.pop('username', None)
    session.pop('password', None)
    return redirect(url_for('home'))

@app.route('/users')
def users():
    # Check if 'username' exists in the session
    if 'username' not in session or session['username'] == '':
        # If not logged in, redirect to the login page
        return redirect(url_for('home'))
    
    mydb = get_db_connection()
    my_cursor = mydb.cursor()

    # Query the database to get all audit logs
    my_cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
    logs = my_cursor.fetchall()  # Fetch all rows

    # Format the date and time for each log entry
    formatted_logs = []
    for log in logs:

        formatted_logs.append((log[0], log[1], log[3], log[4], log[5]))

    # Close cursor and database connection
    my_cursor.close()
    mydb.close()

    # Pass the formatted logs to the template
    return render_template('users.html', logs=formatted_logs, show_sidebar=True)


@app.route('/users/create/accountType', methods=['GET','POST'])
def createAccountType():
    mydb = get_db_connection()
    my_cursor = mydb.cursor()
    
    try:
        # Get the JSON data from the request body
        data = request.get_json()
        
        status = data.get('status')
        accountType = data.get('accountType')
        
        print(f"Status: {status}, Account Type: {accountType}")

        # Ensure data is not empty before proceeding with the insert
        if status and accountType:
            my_cursor.execute("INSERT INTO account_type (account_type, status) VALUES (%s, %s)", (accountType, status))
            my_cursor.execute("INSERT INTO auditLogs (username, did) VALUES (%s, %s)", (session['username'], f"Created account type: {accountType} With status: {status} "))
            mydb.commit()
            return jsonify({"message": "Account Type created successfully!"}), 200
        else:
            return jsonify({"error": "Missing data!"}), 400
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
    
@app.route('/users/create/account', methods=['GET','POST'])
def createAccount():
    mydb = get_db_connection()
    my_cursor = mydb.cursor()
    
    try:
        # Get the JSON data from the request body
        data = request.get_json()
        status = data.get('status')
        accountType = data.get('accountTypeButton')
        Username = data.get('Username')
        password = data.get('password')
        fullname = data.get('fullname')
        
        print(f"Status: {status}, Account Type: {accountType}")

        # Ensure data is not empty before proceeding with the insert
        if status and accountType:
            my_cursor.execute("INSERT INTO users (username, password,fullname,status,account_type) VALUES (%s, %s,%s,%s, %s)", (Username,password, fullname,status,accountType))
            my_cursor.execute("INSERT INTO auditLogs (username, did) VALUES (%s, %s)", (session['username'], f"Created account: {Username} With status: {accountType} "))
            mydb.commit()
            return jsonify({"message": "Account Type created successfully!"}), 200
        else:
            return jsonify({"error": "Missing data!"}), 400
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True)