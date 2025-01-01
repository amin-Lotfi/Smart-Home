from fastapi import FastAPI, Request, Form, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn
import serial
from database import Database  
import socket
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from nltk.tokenize import word_tokenize
from hazm import Normalizer
import nltk
nltk.download('punkt')

app = FastAPI()
db = Database()

command_map = {
    'lamp1_on': b'1',
    'lamp1_off': b'2',
    'lamp2_on': b'3',
    'lamp2_off': b'4',
    'lamp3_on': b'5',
    'lamp3_off': b'6',
    'lamp4_on': b'7',
    'lamp4_off': b'8',
    'lamp5_on': b'9',
    'lamp5_off': b'0',
    'Timer_on': b'H',
    'Timer_off': b'L',
}

data_file = "/home/amin/Documents/project rostami/smart_home_project/backend/data.txt"
with open(data_file, 'r', encoding='utf-8') as file:
    data = file.readlines()

input_texts = []
output_labels = []
for line in data:
    if "**" in line:  
        text, label = line.strip().split("**")
        input_texts.append(text.strip())
        output_labels.append(label.strip())

augmented_input_texts = input_texts + [text[::-1] for text in input_texts]
augmented_output_labels = output_labels + output_labels

normalizer = Normalizer()
normalized_texts = [normalizer.normalize(text) for text in augmented_input_texts]

model_pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(tokenizer=word_tokenize)),
    ('svc', SVC(probability=True))
])

model_pipeline.fit(normalized_texts, augmented_output_labels)

arduino_port = '/dev/ttyUSB0'  
arduino_baudrate = 9600

try:
    arduino = serial.Serial(arduino_port, arduino_baudrate)
    print("Connected to Arduino")
except serial.SerialException as e:
    print(f"Error opening port {arduino_port}: {e}")
    exit()

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

class User(BaseModel):
    username: str
    password: str

class Action(BaseModel):
    action: str

@app.get("/")
async def root(request: Request, error: str = None):
    return templates.TemplateResponse("login.html", {"request": request, "error": error})

@app.get("/register")
async def get_register(request: Request, error: str = None):
    return templates.TemplateResponse("register.html", {"request": request, "error": error})

@app.post("/register")
async def register_user(request: Request, username: str = Form(...), password: str = Form(...)):
    if db.check_username_exists(username):
        error = "Username already exists"
        return templates.TemplateResponse("register.html", {"request": request, "error": error})
    else:
        db.add_user(username, password)
        return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if db.authenticate_user(username, password):
        return templates.TemplateResponse("control.html", {"request": request})
    else:
        error = "Incorrect username or password"
        return templates.TemplateResponse("login.html", {"request": request, "error": error})

@app.get("/perform-action", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("control.html", {"request": request})

@app.get("/control")
async def control(command: str = Query(...)):
    if command in command_map:

        print(command)
        print(command_map[command])

        arduino.write(command_map[command])
        return f'Command {command} executed'
    else:
        return 'Invalid Command'
    

class TemperatureRequest(BaseModel):
    temperature: int
@app.post("/set-temperature")
async def set_temperature(request: TemperatureRequest):
    temperature = request.temperature
    print(f"Received temperature: {temperature}")
    return {'status': 'success', 'temperature': temperature}


class TextRequest(BaseModel):
    text: str
@app.post("/set-text")
async def set_text(request: TextRequest):
    text = request.text
    # print(f"Received text: {text}")

    new_text = text
    normalized_new_text = normalizer.normalize(new_text)

    predicted_label_index_svm = model_pipeline.predict([normalized_new_text])[0]
    prediction_confidence = max(model_pipeline.predict_proba([normalized_new_text])[0])

    confidence_threshold = 0.5

    if prediction_confidence < confidence_threshold:
        print("Low confidence prediction. Please check the request.")
    else:
        print("Predicted label (SVM):", predicted_label_index_svm)

        if predicted_label_index_svm in command_map:
            print(predicted_label_index_svm)
            print(command_map[predicted_label_index_svm])
            arduino.write(command_map[predicted_label_index_svm])
            return f'Command {predicted_label_index_svm} executed'
        else:
            return 'Invalid Command'
    return {'status': 'success', 'text': text}

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('192.168.1.1', 1))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = '127.0.0.1'
    finally:
        s.close()
    return local_ip

if __name__ == "__main__":
    local_ip = get_local_ip()
    print(f"Server running on http://{local_ip}:8000")
    uvicorn.run(app, host='127.0.0.1', port=8000)