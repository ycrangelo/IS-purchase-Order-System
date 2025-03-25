from flask import render_template, request, jsonify, session, redirect, url_for
from db import get_db_connection

def register_accountType_routes(app):
    @app.route('/accountType')
    def accountType():
        # Check if 'username' exists in the session
        if 'username' not in session or session['username'] == '':
            # If not logged in, redirect to the login page
            return redirect(url_for('home'))
                # Connect to the database
        mydb = get_db_connection()
        my_cursor = mydb.cursor()
        
        # Check if 'username' exists in the session
        if 'username' not in session or session['username'] == '':
            # If not logged in, redirect to the login page
            return redirect(url_for('home'))
        
        # Handle POST request (form submission)
        
        # Fetch inventory data for both GET and POST requests
        my_cursor.execute("SELECT * FROM account_type ORDER BY created_at DESC")
        logs = my_cursor.fetchall()  # Fetch all rows

        # Format the date and time for each log entry
        formatted_logs = []
        for log in logs:
            formatted_logs.append((log[0], log[1], log[2]))

        # Close cursor and database connection
        my_cursor.close()
        mydb.close()

        # Pass the formatted logs to the template
        return render_template('accountType.html', logs=formatted_logs, show_sidebar=True)
    
    @app.route('/users/create/accountType', methods=['GET', 'POST'])
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