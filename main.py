from flask import Flask, render_template
from flask_socketio import SocketIO, send
import threading
import queue
from gigachat import *


app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
socketio = SocketIO(app)
message_queue = queue.Queue()


@app.route('/')
def index():
    global token
    token = get_token()
    return render_template('index.html')


@socketio.on('message')
def handle_message(msg):
    bot_reply = send_message(msg, token)
    send(f"Бот: {bot_reply}", broadcast=False)


if __name__ == '__main__':
    threading.Thread(daemon=True).start()
    socketio.run(app, debug=True)
