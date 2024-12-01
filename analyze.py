import cv2
import subprocess
import re
import json
import os

NODE_SCRIPT = "./node_project/face_api.js"
TEMP_IMAGE_PATH = "./temp_frame.jpg"

def analyze_frame(image_path):
    """
    Анализ кадра с использованием Node.js и face-api.js.
    Возвращает пол и эмоции.
    """
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
            return [
                f"Пол: {json_data['gender']}",
                f"Эмоция: {list(filter(lambda x: json_data['expressions'][x] == max(json_data['expressions'].values()), json_data['expressions']))[0]}"
            ]
    except Exception as e:
        print(f"Ошибка анализа кадра: {e}")
        return None
