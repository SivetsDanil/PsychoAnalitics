from flask import Flask, render_template, session, request, jsonify
from flask_socketio import SocketIO, send
import threading
from gigachat import send_message, get_token
import base64
import cv2
import numpy as np
from analyze import analyze_frame

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SESSION_TYPE'] = 'filesystem'
app.config["SESSION_PERMANENT"] = False
socketio = SocketIO(app)

TEMP_IMAGE_PATH = "./temp_frame.jpg"
user_analysis = {}

emotion_dictionary = {
    "neutral": "Нейтрально",
    "happy": "Счастье",
    "sad": "Грусть",
    "angry": "Злость",
    "surprised": "Удивление",
    "fearful": "Страх",
    "disgusted": "Отвращение",
    "contemptuous": "Презрение"
}

gender_dictionary = {
    "male": "Мужчина",
    "female": "Женщина"
}


def decode_base64_to_image(base64_string):
    try:
        if base64_string.startswith('data:image/jpeg;base64,'):
            base64_string = base64_string.split('data:image/jpeg;base64,')[1]
        image_data = base64.b64decode(base64_string)
        np_array = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        return image if image is not None else None
    except Exception:
        return None


@app.route('/')
def index():
    return render_template('unlog_index.html')


@app.route('/chat')
def chat():
    return render_template('index.html')


@socketio.on('message')
def handle_message(msg):
    token = get_token()
    last_bot_message = session.get('last_bot_message')
    sid = request.args.get('sid')
    analysis_info = user_analysis.get(sid, ['', "Не включена камера"])

    text = (
        f'Сгенерируй текст-ответ на сообщение. Сообщение в чате между психологом и пациентом. '
        f'Прошлое сообщение от психолога было такое: "{last_bot_message}". Теперь говорит пациент. '
        f'Сообщение пациента: "{msg}". Сгенерируй текст-ответ на это сообщение от пациента. '
        f'Ответ дружелюбный, краткий, заботливый, добрый, логичный, профессиональный. '
        f'Текст-ответ написан девушкой-психологом Надей, с большим опытом и профессионализмом.'
    )

    if analysis_info[1] != 'Не включена камера':
        text += f' Пользователь испытывает эмоцию {emotion_dictionary.get(analysis_info[1].split()[1], analysis_info[1])}.'

    bot_reply = send_message(text, token)
    bot_reply = ' '.join(bot_reply.split()).replace('. Надя.', '').replace('Привет!', '').replace('Здравствуйте!',
                                                                                                  '').replace(
        "С уважением, Надя", '')
    send(f"Бот: {bot_reply}", broadcast=False)
    session['last_bot_message'] = bot_reply


@app.route('/process-frame', methods=['POST'])
def process_frame():
    try:
        sid = request.args.get('sid')
        frame_base64 = request.json.get("frame", "")
        if not frame_base64:
            user_analysis.pop(sid, None)
            return jsonify({"status": "error", "message": "Кадр отсутствует"}), 400

        frame = decode_base64_to_image(frame_base64)
        if frame is None:
            user_analysis.pop(sid, None)
            return jsonify({"status": "error", "message": "Не удалось декодировать кадр"}), 400

        cv2.imwrite(TEMP_IMAGE_PATH, frame)
        result = analyze_frame(TEMP_IMAGE_PATH)

        if result:
            translated_emotion = emotion_dictionary.get(result[1].lower(), result[1])
            translated_gender = gender_dictionary.get(result[0].lower(), result[0])
            user_analysis[sid] = [translated_gender, translated_emotion]
            socketio.emit('analysis-update', {'gender': translated_gender, 'emotion': translated_emotion}, room=sid)
        else:
            user_analysis.pop(sid, None)
            socketio.emit('analysis-update', {'gender': 'Ошибка анализа', 'emotion': ''}, room=sid)

        return jsonify({"status": "success", "analysis": result}), 200
    except Exception:
        return jsonify({"status": "error", "message": "Ошибка обработки кадра"}), 500


@socketio.on('camera-stopped')
def handle_camera_stopped():
    sid = request.args.get('sid')
    user_analysis.pop(sid, None)


if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True, host='0.0.0.0')
