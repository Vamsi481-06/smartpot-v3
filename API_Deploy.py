import importlib.util
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from PIL import Image
import boto3
import tempfile
from tensorflow.keras.models import load_model
import os
from botocore.exceptions import NoCredentialsError

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load your trained model from S3 bucket
def load_keras_model_from_s3(bucket: str, model_key: str):
    s3 = boto3.client('s3')
    with tempfile.TemporaryFile() as fp:
        s3.download_fileobj(Fileobj=fp, Bucket=bucket, Key=model_key)
        fp.seek(0)
        model = load_model(fp)
    return model

model = load_keras_model_from_s3("smartpot-v2", "testmodel.h5")

# Download recipe files from S3
def download_recipes_from_s3(bucket: str, recipe_folder: str):
    s3 = boto3.client('s3')
    local_folder = '/tmp/recipes'

    if not os.path.exists(local_folder):
        os.makedirs(local_folder)

    try:
        for recipe in recipe_folder:
            local_file = os.path.join(local_folder, recipe)
            s3.download_file(bucket, recipe, local_file)
    except NoCredentialsError:
        print("No AWS credentials found.")
    return local_folder

recipe_folder = download_recipes_from_s3("smartpot-v2", "recipes")

@app.post("/predict")
async def predict(recipe: str = Form(...), image: UploadFile = File(...)):
    # Import the selected recipe as a module
    spec = importlib.util.spec_from_file_location("recipe_module", f"{recipe_folder}/{recipe}.py")
    recipe_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(recipe_module)
    
    # Preprocess the input data and make predictions using the model
    predictions = await make_prediction(model, image)

    # Execute the recipe with the predictions and get the steps
    recipe_step = recipe_module.run_recipe(np.argmax(predictions))

    # Return the recipe steps as JSON
    return JSONResponse(content={"step": recipe_step})

async def make_prediction(model, image: UploadFile):
    # Load the image file
    image_data = Image.open(image.file)

    # Preprocess the image (e.g., resize, convert to grayscale, normalize, etc.)
    processed_image = image_data.convert("RGB").resize((256, 256))

    # Convert the PIL image to a NumPy array and add an extra dimension for batch size
    input_array = np.array(processed_image)[np.newaxis, :, :]

    # Make predictions using the model
    predictions = model.predict(input_array)

    # Post-process the predictions (e.g., convert to a Python list or dictionary)
    result = predictions.tolist()

    return result
