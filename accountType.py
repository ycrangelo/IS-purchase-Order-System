from flask import render_template, request, jsonify, session, redirect, url_for
from db import get_db_connection

def register_accountType_routes(app):
    @app.route('/accountType')
    def accountType():
        # Check if 'username' exists in the session
        if 'username' not in session or session['username'] == '':
            # If not logged in, redirect to the login page
            return redirect(url_for('home'))
        
        return render_template('accountType.html', show_sidebar=False)