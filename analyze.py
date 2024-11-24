import cv2
import subprocess
import re
import os
import json
import threading
import time

NODE_SCRIPT = "./node_project/face_api.js"
TEMP_IMAGE_PATH = "./temp_frame.jpg"
ANALYSIS_INTERVAL = 1

last_analysis_time = 0


def analyze_frame(image_path):
    try:
        result = subprocess.run(
            ["node", NODE_SCRIPT, image_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        match = re.search(r'\[.*\]', result.stdout, re.DOTALL)
        if match:
            raw_json = match.group(0)
            json_data = json.loads(raw_json)[0]
            print(f"Возраст: {json_data['age']}")
            print(f"Пол: {json_data['gender']}")
            print(f"Эмоции: {json_data['expressions']}")
        else:
            print("JSON не найден в выводе")
    except Exception as e:
        print(f"Ошибка анализа кадра: {e}")


def async_analysis(frame):
    cv2.imwrite(TEMP_IMAGE_PATH, frame)
    if os.path.exists(TEMP_IMAGE_PATH):
        threading.Thread(target=analyze_frame, args=(TEMP_IMAGE_PATH,)).start()
    else:
        print("Ошибка: файл не был сохранен")

