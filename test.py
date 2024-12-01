import cv2
import requests

# Ваши ключи для Azure API
subscription_key = 'YOUR_AZURE_API_KEY'
endpoint = 'https://YOUR_REGION.api.cognitive.microsoft.com/face/v1.0/detect'

# Функция для отправки изображения на Azure API и получения возраста
def get_age_from_image(image):
    # Сохранение изображения в файл
    image_path = 'temp_image.jpg'
    cv2.imwrite(image_path, image)

    # Заголовки для запроса
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Content-Type': 'application/octet-stream'
    }

    # Открытие изображения в формате байтов
    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()

    # Параметры запроса
    params = {
        'returnFaceAttributes': 'age,gender'
    }

    # Отправка изображения на сервер
    response = requests.post(endpoint, headers=headers, params=params, data=image_data)

    # Проверка ответа
    if response.status_code == 200:
        faces = response.json()
        if faces:
            age = faces[0]['faceAttributes']['age']
            gender = faces[0]['faceAttributes']['gender']
            return f'Предположительный возраст: {age}, Пол: {gender}'
        else:
            return 'Не удалось распознать лицо'
    else:
        return 'Ошибка при запросе'


cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Отображение захваченного изображения
    cv2.imshow('Webcam', frame)
    # Получение возраста при нажатии на клавишу 's'
    key = cv2.waitKey(1) & 0xFF
    if key == ord('s'):  # Нажмите 's', чтобы отправить изображение на API
        result = get_age_from_image(frame)
    # Выход из цикла при нажатии на клавишу 'q'
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
