import os
import time
import requests
import pandas as pd
import warnings
import pathlib

warnings.simplefilter("ignore")

URL = "https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/prix-des-carburants-en-france-flux-instantane-v2/exports/csv"

def download_data():
    try:
        res = requests.get(URL)
        file = os.path.join(os.getcwd(), os.path.basename(URL))
        with open(file, "wb") as f:
            f.write(res.content)
    except Exception as e:
        print("Erreur :", e)
    return None

def clean_data(df):
    df = df[["gazole_maj", "gazole_prix"]]
    df.gazole_maj = pd.to_datetime(df.gazole_maj)
    df = df.sort_values(by="gazole_maj", ascending=False).reset_index().drop(columns="index")
    return df

def extract_24_data(df):
    horloge = pd.to_datetime(time.asctime(), utc="UTC")
    for i in range(len(df)):
        tick = df.loc[i, "gazole_maj"]
        difference = horloge - tick
        comparateur = difference.days
        if comparateur > 1:
            break
        else:
            pass
    df = df[0:i]
    return df

def calculate_24_price(df):
    jour = time.strftime("%d/%m/%Y")
    heure = time.strftime("%H:%M:%S")
    prix_24 = round(float(df.gazole_prix.mean()), 3)
    nbr_echantillons = df.shape[0]
    data = [{"jour": jour,
            "heure": heure,
            "prix_24": prix_24,
            "echantillons": nbr_echantillons}]
    return data

def save_data(data):
    path = os.getcwd() + r"/bdd_prix_essence.csv"
    read = pathlib.Path(path)
    bdd = pd.read_csv(read, dtype=object)
    data = pd.DataFrame(data)
    bdd = pd.concat([bdd, data]).reset_index(drop=bool)
    bdd.to_csv(read, index=False)
    return bdd

def compute_data():

    # Télécharger les données.
    try:
        download_data()
        print("Base data (FR GOV API) file successfully downloaded.")
    except Exception as e:
        print("Erreur :", e)

    # Lire et supprimer le fichier de la base de données.
    try:
        file = os.getcwd() + r"/csv"
        df = pd.read_csv(file, sep=";")
        os.remove(file)
        print("Base data (FR GOV API) file successfully read and deleted.")
    except Exception as e:
        print("Erreur :", e)

    # Nettoyer la donnée et récupérer les prix des dernières 24 heures.
    try:
        df = clean_data(df)
        df = extract_24_data(df)
        print("Base data (FR GOV API) file successfully cleaned.")
    except Exception as e:
        print("Erreur :", e)

    # Calculer le prix moyen sur les dernières 24 heures et le nbr d'échantillons utilisés.
    try:
        data = calculate_24_price(df)
        del df
        print("Final data successfully computed.")
        print(data)
    except Exception as e:
        print("Erreur :", e)

    # Charger la base de donnée, stocker les données, sauvegarder.
    try:
        save_data(data)
        print("Final data successfully saved.")
    except Exception as e:
        print("Erreur :", e)

    return None