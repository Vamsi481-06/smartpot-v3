from tensorflow.keras.models import load_model

def load_keras_model(model_path: str):
    model = load_model(model_path)
    return model
