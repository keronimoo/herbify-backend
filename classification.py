from datetime import datetime
from flask import Blueprint, render_template, request, current_app
from flask_login import current_user
from keras.utils.image_utils import load_img, img_to_array
from keras.models import load_model
import numpy as np
import os
from .models import User , db , IdentifiedPlant

classification = Blueprint('classification', __name__)

@classification.route('/classification')
def _classification():
    return render_template('identification-page.html')


@classification.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        # Gelen görüntüyü kaydet
        image_file = request.files['image']
        if image_file:
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_file.filename)
            print("IMAGE PATH IS AS FOLLOWS!!:", image_path)
            image_file.save(image_path)

            # Görüntüyü yükle ve yeniden boyutlandır
            img = load_img(image_path, target_size=(224, 224))
            img_array = img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)

            # Modeli yükle
            model_path = os.path.join(current_app.root_path, 'modelVersion1.h5')
            model = load_model(model_path)

            class_names = ['Daisy!', 'Dandelion!', 'Rose!', 'Sunflower!']



            # Tahmin yap
            prediction = model.predict(img_array)
            predicted_class = class_names[np.argmax(prediction)]
            global x
            if predicted_class == 'Daisy!':
                    photo = 'static/daisy.jpeg'
                    x=1
            elif predicted_class == 'Dandelion!':
                    photo = 'static/dandelion.jpeg'
                    x=2
            elif predicted_class == 'Rose!':
                    photo = 'static/rose.jpeg'
                    x=3
            elif predicted_class == 'Sunflower!':
                    photo = 'static/sunflower.jpeg'
                    x=4
            
            #for achievements
            if current_user.is_authenticated:
                user = User.query.get(current_user.id)
                if user:
                    user.identification_count += 1
                    db.session.commit()
             # Store identified plant in the database
            if current_user.is_authenticated:
                user = User.query.get(current_user.id)
                if user:
                    identified_plant = IdentifiedPlant(user_id=user.id, plant_name=predicted_class, date_identified=datetime.utcnow())
                    db.session.add(identified_plant)
                    db.session.commit()


            return render_template('prediction_results.html', photo=photo, predicted_class=predicted_class)

@classification.route('/Info')
def Info():
    if x == 1:
        return render_template('Daisy_Info.html')
    elif x == 2:
        return render_template('Dandelion_Info.html')
    elif x == 3:
        return render_template('Rose_Info.html')
    elif x == 4:
        return render_template('Sunflower_Info.html')
