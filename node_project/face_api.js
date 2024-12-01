const fs = require('fs');
const path = require('path');
const tf = require('@tensorflow/tfjs-node');
const faceapi = require('@vladmandic/face-api');

// Указываем путь к моделям
const modelPathRoot = path.resolve('C:\\Users\\Laptop Sivets\\WebAnalytic\\pythonProject\\node_project\\models');

async function loadModels() {
  console.log(`{"status": "loading_models", "path": "${modelPathRoot}"}`);
  await faceapi.nets.ssdMobilenetv1.loadFromDisk(modelPathRoot); // Для обнаружения лиц
  await faceapi.nets.faceExpressionNet.loadFromDisk(modelPathRoot); // Для эмоций
  await faceapi.nets.ageGenderNet.loadFromDisk(modelPathRoot); // Для пола (опционально)
  console.log(`{"status": "models_loaded"}`);
}

async function imageToTensor(imgPath) {
  const buffer = fs.readFileSync(imgPath);
  const decoded = tf.node.decodeImage(buffer);
  return decoded.expandDims(0);
}

async function detectFace(imageTensor) {
  try {
    return await faceapi.detectAllFaces(imageTensor)
      .withFaceExpressions()
      .withAgeAndGender(); // Если нужен пол, оставьте; иначе удалите.
  } catch (err) {
    console.error(`{"status": "error", "message": "${err.message}"}`);
    return [];
  }
}

async function main() {
  const imgPath = process.argv[2];
  if (!imgPath) {
    console.error(`{"status": "error", "message": "No image path provided"}`);
    process.exit(1);
  }
  console.log(`{"status": "image_path", "path": "${imgPath}"}`);
  await loadModels();
  const tensor = await imageToTensor(imgPath);
  const detections = await detectFace(tensor);

  // Возвращаем только эмоции и пол
  const result = detections.map(detection => ({
    gender: detection.gender,
    expressions: detection.expressions
  }));

  console.log(JSON.stringify(result, null, 2));
}

main();
