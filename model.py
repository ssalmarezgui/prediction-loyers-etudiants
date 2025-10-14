import pandas as pd
import numpy as np 
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import os
import joblib 

def fusionner():
    if os.path.exists('data/new_data.csv'):
        df2 = pd.read_csv('data/new_data.csv')
        if len(df2) > 0:
            df1 = pd.read_csv('data/logements_etudiants_manouba.csv')
            df_fusionne = pd.concat([df1, df2], ignore_index=True)
            df_fusionne.to_csv('data/logements_etudiants_manouba.csv', index=False)
            pd.DataFrame(columns=df2.columns).to_csv('data/new_data.csv', index=False)
            print(f'File new_data.csv fusionned successfully, {len(df2)} rows added.')

def train_model():
    fusionner()
    df = pd.read_csv('data/logements_etudiants_manouba.csv')
    print('Colonnes : ', df.columns.tolist())
    print('Aperçu des données :\n', df.head())
    
    #Cleaning data
    df_clean=df.drop('id_maison',axis=1)
    df_clean=df_clean.dropna()
    print('Colonnes après nettoyage : ', df_clean.columns.tolist())

    categorical_features=['lieu','genre_accepte']
    label_encodings={}
    for feature in categorical_features:
        if feature in df_clean.columns:
            le=LabelEncoder()
            df_clean[feature] = le.fit_transform(df_clean[feature].astype(str))
            label_encodings[feature]=le
            print(f'Encodage de {feature} - {len(le.classes_)} categories')

    print(f'\n Colonnes finales :, {df_clean.columns.tolist()}')
    print(df_clean.head())

    X = df_clean.drop('montant_part',axis=1)
    Y = df_clean['montant_part']

    print(f'Features : {X.shape} , Target : {Y.shape}')

    # Normalization
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
       X_scaled, Y, test_size=0.2, random_state=42
    )

    # Entrainement du modèle
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    #Evaluation
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f'Perfermance du modèle : MAE = {mae:.2f}, Rsquared = {r2:.2f}')

    #Sauvegarde du modèle
    os.makedirs('models', exist_ok=True)

    joblib.dump(model,'models/model.pkl')
    joblib.dump(scaler, 'models/scaler.pkl')
    joblib.dump(label_encodings, 'models/encoders.pkl')

    #Feature importance
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    print('\nImportance des features :\n', feature_importance)

    #Test prediction
    print('\nTest de prédiction :')
    sample_prediction = model.predict(X_scaled[0:1])[0]
    actual_value = Y.iloc[0]
    print(f'Prix reel: {actual_value} DT')
    print(f'Prix prédit: {sample_prediction:.2f} DT')
    print(f'Erreur: {abs(actual_value - sample_prediction):.2f} DT')




if __name__ == '__main__':
    train_model()