const socket = io();
const messageContainer = document.getElementById('message-container');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-btn');
const videoCallBtn = document.getElementById('video-call-btn');
const microBtn = document.getElementById('micro-btn'); // Кнопка микрофона
const infoContainer = document.getElementById('info-container'); // Контейнер для данных анализа

let videoStream = null;
let captureInterval = null;
let isVideoActive = false;

let recognition;
let isRecording = false; // Статус записи
let currentTranscript = ''; // Храним текущий текст
let finalTranscript = ''; // Храним финальную версию текста
let lastAddedTranscript = ''; // Последний добавленный текст
let resetTimer; // Таймер для сброса текста

const emotionDictionary = {
    "neutral": "Нейтрально",
    "happy": "Счастье",
    "sad": "Грусть",
    "angry": "Злость",
    "surprised": "Удивление",
    "fearful": "Страх",
    "disgusted": "Отвращение",
    "contemptuous": "Презрение"
};

const genderDictionary = {
    "male": "Мужчина",
    "female": "Женщина"
};

if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.lang = 'ru-RU'; // Устанавливаем язык на русский
    recognition.interimResults = false; // Отключаем промежуточные результаты
    recognition.continuous = false; // Устанавливаем завершение после одного результата
} else {
    console.error('Speech Recognition API не поддерживается в этом браузере.');
}

microBtn.addEventListener('click', () => {
    if (isRecording) {
        stopRecognition();
    } else {
        startRecognition();
    }
});

function startRecognition() {
    if (!recognition) {
        alert('Ваш браузер не поддерживает запись речи.');
        return;
    }
    isRecording = true;
    microBtn.style.backgroundColor = '#3498db'; // Меняем цвет кнопки на синий
    recognition.start(); // Запуск распознавания речи
}

function stopRecognition() {
    isRecording = false;
    microBtn.style.backgroundColor = ''; // Возвращаем цвет кнопки
    recognition.stop(); // Останавливаем распознавание речи
}

recognition?.addEventListener('result', (event) => {
    // Берем только первый результат и форматируем текст
    let transcript = event.results[0][0].transcript;
    transcript = formatText(transcript); // Форматируем текст
    messageInput.value += transcript; // Заполняем поле ввода
});

recognition?.addEventListener('end', () => {
    if (isRecording) {
        recognition.start(); // Перезапускаем для нового ввода
    }
});

// Функция для обработки текста
function formatText(input) {
    input = input.trim(); // Убираем пробелы в начале и конце

    // Убедимся, что первая буква заглавная
    if (input.length > 0) {
        input = input[0].toUpperCase() + input.slice(1);
    }

    // Проверка на ключевые слова для вопроса
    const questionWords = ["как", "где", "почему", "что", "когда", "кто", "зачем", "разве"];
    const firstWord = input.split(' ')[0].toLowerCase();

    if (questionWords.includes(firstWord)) {
        input = input.replace(/[.!?]$/, '') + '?'; // Удаляем существующий знак и добавляем вопрос
    } else if (!/[.!?]$/.test(input)) {
        input += '.'; // Если нет знака, добавляем точку
    }

    return input + ' '; // Добавляем пробел в конце
}

function processText(input) {
    input = input.trim();

    // Убедимся, что первая буква заглавная
    if (input.length > 0) {
        input = input[0].toUpperCase() + input.slice(1);
    }

    // Добавляем точку в конце, если ее нет
    if (!/[.!?]$/.test(input)) {
        input += '.';
    }

    return input;
}

sendButton.addEventListener('click', sendMessage);

messageInput.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

videoCallBtn.addEventListener('click', toggleVideoStream);

function sendMessage() {
    const message = messageInput.value;
    if (message.trim() === '') return;
    socket.send(message);
    addMessage('Вы', message, 'right');
    messageInput.value = '';
}

socket.on('message', (msg) => {
    if (msg.startsWith('Бот:')) {
        addMessage('Надежда', msg.replace('Бот: ', ''), 'left');
    }
});

// Получаем обновления по анализу и выводим их на страницу
socket.on('analysis-update', (data) => {
    // Извлекаем эмоцию и пол, убираем префиксы
    const emotion = data.emotion.replace('Эмоция: ', '').toLowerCase(); // Убираем "Эмоция: " и приводим к нижнему регистру
    const gender = data.gender.replace('Пол: ', '').toLowerCase(); // Убираем "Пол: " и приводим к нижнему регистру

    // Переводим эмоцию и пол с помощью словарей
    const translatedEmotion = emotionDictionary[emotion] || 'Неизвестная эмоция';  // Если эмоция не найдена, выводим "Неизвестная эмоция"
    const translatedGender = genderDictionary[gender] || 'Неизвестный пол';  // Если пол не найден, выводим "Неизвестный пол"

    // Добавляем обратно префиксы
    const finalEmotion = `Эмоция: ${translatedEmotion}`;
    const finalGender = `Пол: ${translatedGender}`;

    // Обновляем отображение
    infoContainer.innerHTML = `${finalGender} <br> ${finalEmotion}`;
});



function addMessage(sender, message, side) {
    const senderDiv = document.createElement('div');
    senderDiv.classList.add('message-sender', side);
    senderDiv.textContent = sender;

    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', side);
    messageDiv.style.borderRadius = '10px';
    messageDiv.style.padding = '10px';
    messageDiv.style.color = 'white';
    messageDiv.style.maxWidth = '60%';
    messageDiv.style.wordWrap = 'break-word';

    const formattedMessage = message.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    messageDiv.innerHTML = formattedMessage;

    messageContainer.appendChild(senderDiv);
    messageContainer.appendChild(messageDiv);
    messageContainer.scrollTop = messageContainer.scrollHeight;
}

function toggleVideoStream() {
    if (isVideoActive) {
        stopVideoStream();
    } else {
        startVideoStream();
    }
}

async function startVideoStream() {
    try {
        isVideoActive = true;
        videoCallBtn.innerHTML = "Завершить";
        videoStream = await navigator.mediaDevices.getUserMedia({ video: true });
        const videoElement = document.createElement("video");
        videoElement.srcObject = videoStream;
        videoElement.play();
        document.body.appendChild(videoElement);
        videoElement.style.position = "absolute";
        videoElement.style.top = "10px";
        videoElement.style.left = "10px";
        videoElement.style.width = "300px";

        captureInterval = setInterval(() => {
            const canvas = document.createElement("canvas");
            const context = canvas.getContext("2d");
            canvas.width = videoElement.videoWidth;
            canvas.height = videoElement.videoHeight;
            context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);

            const frameData = canvas.toDataURL("image/jpeg");
            sendFrame(frameData);
        }, 1000);  // Отправка кадра каждую секунду

        // Показываем контейнер с анализом при активации камеры
        infoContainer.style.display = "block";
    } catch (err) {
        console.error("Ошибка при доступе к веб-камере:", err);
        isVideoActive = false;
    }
}

function stopVideoStream() {
    if (videoStream) {
        const tracks = videoStream.getTracks();
        tracks.forEach(track => track.stop());
        videoStream = null;
    }
    clearInterval(captureInterval);
    isVideoActive = false;
    videoCallBtn.innerHTML = '<img src="/static/img/call.png" alt="Видеозвонок"/>';
    const videoElement = document.querySelector("video");
    if (videoElement) {
        videoElement.remove();
    }

    // Скрываем контейнер с анализом при остановке камеры
    infoContainer.style.display = "none";
    socket.emit('camera-stopped', { message: 'Камера была отключена' });
}

async function sendFrame(frameData) {
    try {
        await fetch("/process-frame", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ frame: frameData })
        });
    } catch (err) {
        console.error("Ошибка отправки кадра:", err);
    }
}

socket.send('Привет! Представься как опытный психолог. Напиши что ты опытный психолог и готова помочь. Ты девушка. не больше 10 слов');

function setVhProperty() {
    document.documentElement.style.setProperty('--vh', `${window.innerHeight * 0.0096}px`);
}
window.addEventListener('resize', setVhProperty);
setVhProperty();
