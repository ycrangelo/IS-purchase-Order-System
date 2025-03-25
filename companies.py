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
        
    @app.route('/comapany/deactivation', methods=['GET', 'POST'])
    def companyDeactivation():
        # Connect to the database
        mydb = get_db_connection()
        my_cursor = mydb.cursor()

        try:
            # Process form data
            data = request.get_json()
            item_id = data['id']
            codeId=data['codeId']
            
            my_cursor.execute("SELECT status FROM companies WHERE id = %s", (item_id,))
            logs = my_cursor.fetchone()  # Fetch all rows
            user_status = logs[0]
            print(logs)
            if user_status =="1":
                deactivation = 0
                # Perform the update operation
                my_cursor.execute("""
                    UPDATE companies
                    SET status = %s WHERE id = %s
                """, (deactivation, item_id))
                mydb.commit()
                # Log the update to the audit log
                my_cursor.execute("INSERT INTO auditLogs (username, did) VALUES (%s, %s)", 
                            (session['username'], f"Deactivate an companies with code ID: {codeId}"))
            if user_status =="0":
                deactivation = 1
                # Perform the update operation
                my_cursor.execute("""
                    UPDATE companies
                    SET status = %s WHERE id = %s
                """, (deactivation, item_id))
                mydb.commit()
            # Log the update to the audit log
                my_cursor.execute("INSERT INTO auditLogs (username, did) VALUES (%s, %s)", 
                            (session['username'], f"Activate an companies with code ID: {codeId}"))

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

    @app.route('/companies/changepass', methods=['GET', 'POST'])
    def comChange_password():
        mydb = get_db_connection()
        my_cursor = mydb.cursor()

        data = request.get_json()
        new_password = data.get('newPassword')
        user_id = data.get('id')

        try:
            # Update the user's password in the database
            my_cursor.execute(
                "UPDATE companies SET password = %s WHERE id = %s",
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
            
    @app.route('/companies/edit', methods=['GET', 'POST'])
    def companiesEdit():
        # Connect to the database
        mydb = get_db_connection()
        my_cursor = mydb.cursor()

        try:
            # Process form data
            data = request.get_json()

            # Extract values from the request data
            editCompanyName = data.get('editCompanyName')
            editContactPerson = data.get('editContactPerson')
            EditUsername = data.get('EditUsername')
            print(editCompanyName)
            print(editContactPerson)
            print(EditUsername)
            item_id = data['id']

            # Perform the update operation
            my_cursor.execute("""
            UPDATE companies
            SET company_name = %s, contact_person = %s, username = %s
            WHERE id = %s
        """, (editCompanyName, editContactPerson, EditUsername, item_id))
            # Log the update to the audit log
            my_cursor.execute("INSERT INTO auditLogs (username, did) VALUES (%s, %s)", 
                            (session['username'], f"Edited Company Details with code ID: {item_id}"))

            # Commit changes to the database
            mydb.commit()

            # Return a success response
            return jsonify({"message": "Inventory updated successfully!"}), 200

        except Exception as e:
            # Capture the exact error for logging and return it in the response
            mydb.rollback()
            print(f"Error occurred: {e}")  # This will print to your console
            return jsonify({"error": f"An error occurred while updating the inventory: {str(e)}"}), 500

        finally:
            # Close the database connection
            my_cursor.close()
            mydb.close()