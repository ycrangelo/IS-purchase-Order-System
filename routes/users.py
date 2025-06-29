from flask import render_template, request, jsonify, session, redirect, url_for
from routes.db import get_db_connection  # Import from db.py

def register_user_routes(app):
    @app.route('/user/deactivation', methods=['GET', 'POST'])
    def userDeactivation():
        # Connect to the database
        mydb = get_db_connection()
        my_cursor = mydb.cursor()

        try:
            # Process form data
            data = request.get_json()
            item_id = data['id']
            codeId=data['codeId']
            
            my_cursor.execute("SELECT status FROM users WHERE id = %s", (item_id,))
            logs = my_cursor.fetchone()  # Fetch all rows
            user_status = logs[0]
            print(logs)
            if user_status =="1":
                deactivation = 0
                # Perform the update operation
                my_cursor.execute("""
                    UPDATE users
                    SET status = %s WHERE id = %s
                """, (deactivation, item_id))
                mydb.commit()
                # Log the update to the audit log
                my_cursor.execute("INSERT INTO auditLogs (username, did) VALUES (%s, %s)", 
                            (session['username'], f"Deactivate an account with code ID: {codeId}"))
            if user_status =="0":
                deactivation = 1
                # Perform the update operation
                my_cursor.execute("""
                    UPDATE users
                    SET status = %s WHERE id = %s
                """, (deactivation, item_id))
                mydb.commit()
            # Log the update to the audit log
                my_cursor.execute("INSERT INTO auditLogs (username, did) VALUES (%s, %s)", 
                            (session['username'], f"Activate an account with code ID: {codeId}"))

            # Commit changes to the database
            mydb.commit()

            # Return a success response
            return jsonify({"message": "Inventory Deactivate successfully!"}), 200

        except Exception as e:
            # Capture the exact error for logging and return it in the response
            mydb.rollback()
            print(f"Error occurred: {e}")  # This will print to your console
            return jsonify({"error": f"An error occurred while updating the inventory: {str(e)}"}), 500

        finally:
            # Close the database connection
            my_cursor.close()
            mydb.close()
            
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
        
        my_cursor.execute("SELECT * FROM account_type WHERE status != 0 ORDER BY created_at DESC")
        account_type = my_cursor.fetchall()  # Fetch all rows

        # Format the date and time for each log entry
        formatted_logs = []
        for log in logs:
            formatted_logs.append((log[0], log[1], log[3], log[4], log[5],log[2]))
        formatted_account_type = []
        for account_types in account_type:
            formatted_account_type.append((account_types[1]))

        # Close cursor and database connection
        my_cursor.close()
        mydb.close()

        # Pass the formatted logs to the template
        return render_template('users.html', logs=formatted_logs, formatted_account_type=formatted_account_type, show_sidebar=True)

        
    @app.route('/users/create/account', methods=['GET', 'POST'])
    def createAccount():
        mydb = get_db_connection()
        my_cursor = mydb.cursor()
        
        try:
            # Get the JSON data from the request body
            data = request.get_json()
            status = "1"
            accountType = data.get('accountTypeButton')
            Username = data.get('Username')
            password = data.get('password')
            fullname = data.get('fullname')
            
            print(f"Status: {status}, Account Type: {accountType}")

            # Ensure data is not empty before proceeding with the insert
            if status and accountType:
                my_cursor.execute("INSERT INTO users (username, password, fullname, status, account_type) VALUES (%s, %s, %s, %s, %s)", (Username, password, fullname, status, accountType))
                my_cursor.execute("INSERT INTO auditLogs (username, did) VALUES (%s, %s)", (session['username'], f"Created account: {Username} With status: {accountType} "))
                mydb.commit()
                return jsonify({"message": "Account created successfully!"}), 200
            else:
                return jsonify({"error": "Missing data!"}), 400
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": str(e)}), 500
    @app.route('/users/changepass', methods=['GET', 'POST'])
    def change_password():
        mydb = get_db_connection()
        my_cursor = mydb.cursor()

        data = request.get_json()
        new_password = data.get('newPassword')
        user_id = data.get('id')

        try:
            # Update the user's password in the database
            my_cursor.execute(
                "UPDATE users SET password = %s WHERE id = %s",
                (new_password, user_id)
            )

            # Log the password change (optional)
            my_cursor.execute(
                "INSERT INTO auditLogs (username, did) VALUES (%s, %s)", 
                (session['username'], f"Changed password for user ID: {user_id}")
            )

            # Commit changes to the database
            mydb.commit()

            return jsonify({"message": "Password changed successfully"}), 200

        except Exception as e:
            mydb.rollback()
            return jsonify({"error": str(e)}), 500

        finally:
            my_cursor.close()
            mydb.close()

