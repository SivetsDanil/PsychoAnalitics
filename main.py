import eventlet

eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO, send
import threading
import queue
from gigachat import *

# Создание приложения Flask
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
    print(f"Message from user: {msg}")
    send(f"Бот: {send_message(msg, token)}", broadcast=True)



if __name__ == '__main__':
    # Запускаем приложение
    threading.Thread(daemon=True).start()
    socketio.run(app, port=5000, host='127.0.0.1', debug=True)