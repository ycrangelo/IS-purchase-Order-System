from flask import render_template, request, jsonify, session, redirect, url_for
from routes.db import get_db_connection

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
        
        
    @app.route('/accountType/deactivation', methods=['GET', 'POST'])
    def accountTypeDeactivation():
        # Connect to the database
        mydb = get_db_connection()
        my_cursor = mydb.cursor()

        try:
            # Process form data
            data = request.get_json()
            item_id = data['id']
            codeId=data['codeId']
            
            my_cursor.execute("SELECT status FROM account_type WHERE id = %s", (item_id,))
            logs = my_cursor.fetchone()  # Fetch all rows
            user_status = logs[0]
            print(logs)
            if user_status =="1":
                deactivation = 0
                # Perform the update operation
                my_cursor.execute("""
                    UPDATE account_type
                    SET status = %s WHERE id = %s
                """, (deactivation, item_id))
                mydb.commit()
                # Log the update to the audit log
                my_cursor.execute("INSERT INTO auditLogs (username, did) VALUES (%s, %s)", 
                            (session['username'], f"Deactivate an account in Inventory with code ID: {codeId}"))
            if user_status =="0":
                deactivation = 1
                # Perform the update operation
                my_cursor.execute("""
                    UPDATE account_type
                    SET status = %s WHERE id = %s
                """, (deactivation, item_id))
                mydb.commit()
            # Log the update to the audit log
                my_cursor.execute("INSERT INTO auditLogs (username, did) VALUES (%s, %s)", 
                            (session['username'], f"Activate an account in Inventory with code ID: {codeId}"))

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
            
    @app.route('/accountType((s/changeAccountType', methods=['GET', 'POST'])
    def changeAccountType():
        mydb = get_db_connection()
        my_cursor = mydb.cursor()

        data = request.get_json()
        account_type = data.get('accountType')
        user_id = data.get('id')

        try:
            # Update the user's password in the database
            my_cursor.execute(
                "UPDATE account_type SET account_type = %s WHERE id = %s",
                (account_type, user_id)
            )

            # Log the password change (optional)
            my_cursor.execute(
                "INSERT INTO auditLogs (username, did) VALUES (%s, %s)", 
                (session['username'], f"Changed account_type for ID: {user_id}")
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