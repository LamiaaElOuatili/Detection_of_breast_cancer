
from fastapi import FastAPI, UploadFile
import tensorflow as tf
from keras.models import load_model
import cv2
import io
from PIL import Image
import numpy as np


print("TensorFlow version:", tf.__version__)

app = FastAPI()

from keras.models import model_from_json

def load():
    model_weights_path = r"C:/Desktop/_model2_.h5"
    model_json_path = r"C:/Desktop/_model2_.json"

    try:
        # Load the model architecture from JSON
        with open(model_json_path, 'r') as json_file:
            model_json = json_file.read()
            model = model_from_json(model_json)

        # Load the weights into the model
        model.load_weights(model_weights_path)

        print("Model loaded successfully")
        return model
    except Exception as e:
        print(f"Error loading the model: {e}")
        return None

model = load()

def preprocessing(img):
    target_size = (224, 224)
    
    # Convert PIL Image to NumPy array
    img_np = np.array(img)

    # Resize the image
    img_resized = cv2.resize(img_np, (target_size[1], target_size[0]))

    # Convert BGR to RGB
    img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)

    # Normalize the image
    img_normalized = img_rgb / 255.0

    # Add batch dimension
    img_batch = np.expand_dims(img_normalized, axis=0)

    return img_batch

@app.get("/")
def greet():
    return {"message": "bonjour"}


@app.post("/predict")
async def predict(file: UploadFile):
    image_data = await file.read()

    img = Image.open(io.BytesIO(image_data))

    img_processed = preprocessing(img)

    pathologies = {
    0: ' Catégorie 0 Investigation incomplète',
    1: ' Catégorie 1 Normal',
    2: ' Catégorie 2 Anomalie bénigne',
    3: ' Catégorie 3 Anomalie probablement bénigne',
    4: ' Catégorie 4 Anomalie demandant une biopsie',
    5: ' Catégorie 5 Anomalie fortement suspecte d un cancer',
    6: ' Catégorie 6 Cancer prouvé à la biopsie'
    }

    prediction = model.predict(img_processed)
    predicted_label = pathologies[prediction.argmax()]

    return {"Diagnostic Prédit": predicted_label}