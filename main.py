import eventlet

eventlet.monkey_patch()

from flask import Flask, render_template, redirect, url_for, request, session
from flask_socketio import SocketIO, send
import threading
import queue

# Создание приложения Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'

# Инициализация SocketIO
socketio = SocketIO(app)

# Очередь для обмена сообщениями между консолью и пользователем
message_queue = queue.Queue()


# Главная страница (чат)
@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    return redirect(url_for('login'))


# Страница авторизации
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return render_template('login.html')


# Страница выхода
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


# Обработка сообщений из чата
@socketio.on('message')
def handle_message(msg):
    username = session.get('username', 'Anonymous')
    print(f"Message from {username}: {msg}")

    # Отправляем полученное сообщение в очередь
    message_queue.put((username, msg))

    # Отправляем пользователю копию сообщения
    send(f"{username}: {msg}", broadcast=True)

    # Ожидаем ответа из консоли
    response = message_queue.get()
    send(f"Бот: Привет", broadcast=True)


# Поток для отправки сообщений с сервера через консоль
def console_input():
    while True:
        # Ожидаем вопрос от клиента
        username, msg = message_queue.get()

        # Читаем ответ из консоли
        response = input(f"Enter response to {username}: ")

        # Отправляем ответ в очередь
        message_queue.put(response)


if __name__ == '__main__':
    # Запускаем приложение
    threading.Thread(target=console_input, daemon=True).start()
    socketio.run(app, port=5000, host='127.0.0.1', debug=True)