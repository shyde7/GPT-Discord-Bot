from flask import Flask, request
import threading
import bot  # Import your bot.py module

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, the bot server is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():  
    server = threading.Thread(target=run)
    server.start()
