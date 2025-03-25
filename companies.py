from flask import render_template, request, jsonify, session, redirect, url_for
from db import get_db_connection

def register_companies_routes(app):
    @app.route('/companies')
    def companies():
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
        my_cursor.execute("SELECT * FROM companies ORDER BY created_at DESC")
        logs = my_cursor.fetchall()  # Fetch all rows

        # Format the date and time for each log entry
        formatted_logs = []
        for log in logs:
            formatted_logs.append((log[0], log[1], log[2],log[3],log[4],log[5],log[6]))

        # Close cursor and database connection
        my_cursor.close()
        mydb.close()
        logs=formatted_logs

        return render_template('companies.html',logs=formatted_logs, show_sidebar=True)
    
    @app.route('/company/createCompany', methods=['GET', 'POST'])
    def createCompany():
        mydb = get_db_connection()
        my_cursor = mydb.cursor()
        
        try:
            # Get the JSON data from the request body
            data = request.get_json()
            status = "1"
            companyName = data.get('companyName')
            contactPerson = data.get('contactPerson')
            username = data.get('username')
            password = data.get('password')
            print(companyName)
            print(contactPerson)
            print(username)
            print(password)

            # Ensure data is not empty before proceeding with the insert
            if status and companyName:
                my_cursor.execute("INSERT INTO companies (company_name, contact_person, username, password, status) VALUES (%s, %s, %s, %s, %s)", (companyName, contactPerson, username, password, status))
                my_cursor.execute("INSERT INTO auditLogs (username, did) VALUES (%s, %s)", (session['username'], f"Created Company: {companyName} With contact Person: {contactPerson} "))
                mydb.commit()
                return jsonify({"message": "Account created successfully!"}), 200
            else:
                return jsonify({"error": "Missing data!"}), 400
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": str(e)}), 500