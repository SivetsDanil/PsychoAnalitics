from flask import Flask, render_template, session
from flask_socketio import SocketIO, send
import threading
import queue
from gigachat import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SESSION_TYPE'] = 'filesystem'
socketio = SocketIO(app)
message_queue = queue.Queue()

@app.route('/')
def index():
    return render_template('test.html')

@socketio.on('message')
def handle_message(msg):
    # Получаем токен и создаем ответ бота
    token = get_token()

    # Проверяем, было ли прошлое сообщение от бота для данного пользователя
    last_bot_message = session.get('last_bot_message')
    bot_reply = send_message(f'Сгенерируй текст-ответ на сообщение. Сообщение в чате между психологом и пациентом. '
                 f'Прошлое сообщение от психолога было такое: "{last_bot_message}".'
                 f'Теперь говорит пациент. '
                 f'Сообщение пациента: "{msg}". Сгенерируй текст-ответ на это сообщение от пациента. '
                             f'Текст-ответ на сообщение пациента написан девушкой, психолог, очень умная, имеет большой '
                             f'опыт, имя Надя. в тексте Надя отвечает своему пациенту. Ответ дружелюбный, краткий, '
                             f'заботливый, добрый, логичный. В тексте-ответе Надя говорит профессиональное мнение психолога.'
                             f' В тексте Надя рассуждает как психолог. В тексте Надя выносит вердикт. В тексте Надя'
                             f' рассматривает ситуацию пациента с точки зрения психологии. Текст это ответ на сообщение пациента.'
                             f' пиши простым языком. пиши так, будто пишет психолог, пиши в стиле переписке между друзьями', token)
    # Отправляем ответ и сохраняем текущее сообщение бота в сессии
    bot_reply = ' '.join(bot_reply.split())
    bot_reply = ' '.join(bot_reply.split('\n'))
    bot_reply = bot_reply.replace('. Надя.', '').replace('Привет!', '').replace('Здравствуйте!', '').replace("С уважением, Надя", '')
    send(f"Бот: {bot_reply}", broadcast=False)
    session['last_bot_message'] = bot_reply  # Обновляем прошлое сообщение от бота в сессии пользователя

if __name__ == '__main__':
    threading.Thread(daemon=True).start()
    socketio.run(app, debug=True)
