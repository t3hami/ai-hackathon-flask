import os
import json
import datetime
from bson.objectid import ObjectId
from flask import Flask, render_template, request
from werkzeug import secure_filename
from flask_pymongo import PyMongo
import numpy as np
from keras.preprocessing import image
from keras.models import load_model


peoples = ['Ahmer', 'Fayyaz', 'Kashan', 'Mansoor', 'Sachin', 'Shaheer', 'Sir', 'Tehami', 'Wahab']

class JSONEncoder(json.JSONEncoder):
    ''' extend json-encoder class'''

    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime.datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'aihackathon'
app.config['MONGO_URI'] = 'mongodb://localhost/aihackathon'

mongo = PyMongo(app)

app.json_encoder = JSONEncoder

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

model = load_model('students_faces.h5')
model._make_predict_function()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/auth', methods=['POST'])
def auth():
    user_cursor = mongo.db.users.find_one({'username': request.form['username']})
    if user_cursor:
        if user_cursor['password'] == request.form['password']:
            return render_template('upload-file.html')
    return "Wrong credentias!"


@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/create-acount', methods=['POST'])
def create_account():
    user_cursor = mongo.db.users.find_one({'username': request.form['username']})
    if user_cursor:
        return "Username not available!"
    user = {
        'username': request.form['username'],
        'password': request.form['password']
    }
    mongo.db.users.insert(user)
    return 'Account created! Go to <a href="/"}>Login page</a>'

@app.route('/predict', methods=['POST'])
def predict():
    f = request.files['file']
    f.save('uploads/'+secure_filename(f.filename))
    test_image = image.load_img('uploads/'+f.filename, target_size=(224,224))
    test_image = image.img_to_array(test_image)
    test_image = np.expand_dims(test_image,axis=0)
    result = model.predict(test_image)
    prediction = peoples[np.argmax(result)]
    return 'Prediction: ' + prediction

if __name__ == '__main__':
    app.run(debug=True)