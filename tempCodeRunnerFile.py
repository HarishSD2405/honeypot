from flask import Flask, render_template, request, redirect, url_for
import logging
from logging.handlers import RotatingFileHandler
logging_format = logging.Formatter('%(asctime)s %(message)s')

http_logger = logging.getLogger('HTTPLogger') 
http_logger.setLevel(logging.INFO) 
http_handler = RotatingFileHandler("http_audits.log",maxBytes = 2000, backupCount = 5)
http_handler.setFormatter(logging_format)
http_logger.addHandler(http_handler)

# serve up static webpage to accept username and password
def web_honeypot(input_username="admin", input_password="password"):
    app = Flask(__name__)

    @app.route('/')

    def index():
        return render_template('wp-admin.html')
        
    @app.route('/wp-admin-login', methods=['POST'])

    def login():
        username = request.form['username'] # from html file
        password = request.form['password'] # from html file

        ip_address = request.remote_addr
        http_logger.info(f'Client with IP Address : {ip_address} entered \nUsername : {username}, Password : {password}')
        if username == input_username and password == input_password:
            return 'HELLO'
        else:
            return "invalid username or password"
    return app

def run_web_honeypot(port=5000, input_username="admin", input_password="deeboodah"):
     app = web_honeypot(input_username, input_password)
     app.run(debug=True, port=port, host="0.0.0.0")

     return app

run_web_honeypot(port=5000,input_username="admin", input_password="password")