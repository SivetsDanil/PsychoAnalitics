from flask import Flask, render_template, request, jsonify
import base64
import cv2
import numpy as np
import os
import time
from analyze import analyze_frame  # Импорт вашей функции для анализа

app = Flask(__name__)
TEMP_IMAGE_PATH = "./temp_frame.jpg"
ANALYSIS_INTERVAL = 1  # Интервал анализа в секундах
last_analysis_time = 0

def decode_base64_to_image(base64_string):
    """
    Преобразует строку base64 в изображение OpenCV.
    """
    try:
        # Убираем префикс 'data:image/jpeg;base64,' если он есть
        if base64_string.startswith('data:image/jpeg;base64,'):
            base64_string = base64_string.split('data:image/jpeg;base64,')[1]

        # Декодируем строку base64 в изображение
        image_data = base64.b64decode(base64_string)
        np_array = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

        if image is None:
            print("Ошибка: Не удалось создать изображение из base64.")
            return None
        return image
    except Exception as e:
        print(f"Ошибка декодирования base64: {e}")
        return None

@app.route('/')
def index():
    return render_template('test.html')  # Загружает HTML страницу

@app.route('/process-frame', methods=['POST'])
def process_frame():
    global last_analysis_time
    try:
        data = request.json

        # Отладочный вывод получаемых данных (если нужно)
        # print("Полученные данные: ", data)

        frame_base64 = data.get("frame", "")
        if not frame_base64:
            print("Кадр отсутствует")
            return jsonify({"status": "error", "message": "Кадр отсутствует"}), 400

        # Преобразуем base64-строку в изображение
        frame = decode_base64_to_image(frame_base64)
        if frame is None:
            print("Не удалось декодировать кадр")
            return jsonify({"status": "error", "message": "Не удалось декодировать кадр"}), 400

        current_time = time.time()

        # Сохраняем кадр во временный файл
        cv2.imwrite(TEMP_IMAGE_PATH, frame)
        if os.path.exists(TEMP_IMAGE_PATH):
            last_analysis_time = current_time

            # Анализируем кадр
            result = analyze_frame(TEMP_IMAGE_PATH)

            # Если результат анализа есть, выводим информацию в консоль
            if result:
                print(f"Возраст: {result['age']}")
                print(f"Пол: {result['gender']}")
                print(f"Эмоции: {result['expressions']}")

            return jsonify({"status": "success", "analysis": result}), 200
        else:
            return jsonify({"status": "error", "message": "Не удалось сохранить временный файл"}), 500
    except Exception as e:
        print(f"Ошибка обработки кадра: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
