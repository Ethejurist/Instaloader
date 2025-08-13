import time
from instagrapi import Client
import os
import json
from dotenv import load_dotenv

load_dotenv()
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
COMPANY_NAME = os.getenv("COMPANY_NAME")
COMPANY_WEBSITE = os.getenv("COMPANY_WEBSITE")
COMPANY_INSTAGRAM = os.getenv("COMPANY_INSTAGRAM")
DESTINATAIRES = json.loads(os.getenv("DESTINATAIRES", "[]"))

def build_message(username):
    return (
        f"Bonjour @{username},\n\n"
        f"Nous sommes {COMPANY_NAME}, une société spécialisée dans les produits de beauté de qualité. "
        "Votre profil nous intéresse beaucoup et nous serions ravis de vous compter parmi notre communauté.\n\n"
        f"Site web : {COMPANY_WEBSITE}\n"
        f"Instagram : {COMPANY_INSTAGRAM}\n\n"
        f"Au plaisir d’échanger avec vous !\n"
        f"L’équipe {COMPANY_NAME} 🌸"
    )

def login_instagram():
    client = Client()
    try:
        client.login(USERNAME, PASSWORD)
    except Exception as e:
        if "Two-factor authentication required" in str(e):
            code = input("Entrez le code 2FA : ")
            client.login(USERNAME, PASSWORD, verification_code=code)
        else:
            raise e
    return client

def envoyer_message(client, username):
    try:
        user_id = client.user_id_from_username(username)
        message = build_message(username)
        client.direct_send(message, [user_id])
        print("Message envoyé à", username)
        return True
    except Exception as e:
        if "Please wait a few minutes" in str(e) or "feedback_required" in str(e):
            print("Blocage détecté pour", username)
            return "blocked"
        print("Erreur pour", username, ":", e)
        return False

def main():
    client = login_instagram()
    delay = 10
    for username in DESTINATAIRES:
        result = envoyer_message(client, username)
        if result == "blocked":
            print(" Pause plus longue à cause d’un blocage")
            time.sleep(delay + 30)
            continue
        elif result is False:
            print(" Erreur ignorée. Passage au suivant.")
        time.sleep(delay)
    client.logout()
    print(" Terminé")

if __name__ == "__main__":
    main()
