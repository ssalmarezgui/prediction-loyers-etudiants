from flask import Flask, render_template, jsonify , request
import joblib
from datetime import datetime
import os
import pandas as pd

app = Flask(__name__)

model = None
scaler = None
label_encoders = None

def load_model():
    global model, scaler, label_encoders
    try:
        model = joblib.load('models/model.pkl')
        scaler = joblib.load('models/scaler.pkl')
        label_encoders = joblib.load('models/encoders.pkl')
        print('model loaded successfully')
    except Exception as e:
        print(f'Error loading model: {e}')
        model= None

load_model()

@app.route('/')
def home():
    return render_template('home.html')
@app.route('/form')
def form_page():
    return render_template('form.html') 
@app.route('/choix')
def choix_page():
    return render_template('choix.html')
@app.route('/aide')
def aide():
    return render_template('aide.html')
@app.route('/resultat')
def resultat():
    prix = request.args.get('prix', '0')
    return render_template('resultat.html', prix = prix)

#predict route
@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({'success': False, 'error': 'Model not loaded. Execute model.py first'})
    try:
        data = request.json
        print("Received data:", data)

        #mapping from text to numerical values
        type_chambre_mapping = {
            'individuelle': 1,
            'double': 2,
            'triple': 3,
        }

        # mapping for genre
        genre_mapping = {
            'fille': 'F',
            'garcon': 'M',
            'mixte': 'F'
        }

        def determine_genre(lieu_genre, my_genre):
            lieu_genre_clean = genre_mapping.get(lieu_genre, 'F')
            if lieu_genre_clean == 'mixte':  
                return my_genre  
            else:
                return lieu_genre_clean

        #prepare features 
        features = []

        #numerical features

        features.append(float(data['nbChambres']))
        features.append(1 if data.get('wifi', False) else 0)
        features.append(1 if data.get('electricite', False) else 0)
        features.append(1 if data.get('eau', False) else 0)

        #mapping categorical features
        type_chambre_value = type_chambre_mapping.get(data['typeChambre'], 1)
        features.append(type_chambre_value)

        #categorical encoding

        if 'lieu' in label_encoders:
            try:
                lieu_encoded = label_encoders['lieu'].transform([data['lieu']])[0]
                features.append(lieu_encoded)
            except:
                features.append(0)
        else:
            features.append(0)

        # encoding genre

        if 'genre_accepte' in label_encoders:
            try:
                genre_final = determine_genre(data['genre'], data.get('myGenre', 'F'))
                genre_encoded = label_encoders['genre_accepte'].transform([genre_final])[0] 
                features.append(genre_encoded)
                print(f"Genre encodé: {data['genre']} → {genre_final} → {genre_encoded}")
            except Exception as e:
                print(f"Erreur encodage genre: {e}")
                features.append(0)
        else:
            features.append(0)

        print(f'Features:{features}')

        #scaling features
        features_scaled = scaler.transform([features])

        #predicting
        prediction = model.predict(features_scaled)[0]

        return jsonify({
            'success': True,
            'prediction' : round(prediction, 2),
            'message': f'Le loyer mensuel estimé est de {round(prediction, 2)} DT'
        })
    except Exception as e:
        print(f'Error during prediction: {e}')
        return jsonify({'error': 'Error during prediction'})
    

@app.route('/add-data', methods=['POST'])
def add_data():
    try:
        data = request.json

        #mapping type_chambre
        type_chambre_mapping = {
            'individuelle': 1,
            'double': 2,
            'triple': 3,
        }

        def determine_genre_for_data(genre_accepte, user_genre=None):
            if genre_accepte == 'mixte':
                return user_genre if user_genre else 'F'  
            else:
                return genre_accepte 


        #new row
        new_row = {
            'id_maison': f'maison_{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'lieu': data['lieu'],
            'nb_chambres': int(data['nbChambres']),
            'type_chambre': type_chambre_mapping.get(data['typeChambre'], 1),
            'wifi': 1 if data.get('wifi', False) else 0,
            'electricite': 1 if data.get('electricite', False) else 0,
            'eau': 1 if data.get('eau', False) else 0,
            'montant_part': float(data['montant']),
            'genre_accepte': data['myGenre'] 
        }

        print(f'New row to add: {new_row}')
        #append to CSV

        new_data_file = 'data/new_data.csv'
        if not os.path.exists(new_data_file):
            pd.DataFrame([new_row]).to_csv(new_data_file, index=False)
        else:
            existing_data = pd.read_csv(new_data_file)
            updated_data = pd.concat([existing_data, pd.DataFrame([new_row])], ignore_index=True)
            updated_data.to_csv(new_data_file, index=False)
        return jsonify({'success': True, 'message': 'data added successfully'})
    except Exception as e:
        return jsonify({'error': f'Error adding data: {e}'})
    



if __name__ == '__main__':

    os.makedirs('data', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    app.run(debug=True)
