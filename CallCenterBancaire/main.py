from flask import Flask, request, jsonify, session
import requests

app = Flask(__name__)
app.secret_key = "your_secret_key_123"  # Clé pour utiliser la session Flask

RASA_URL = "http://localhost:5005/webhooks/rest/webhook"


@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Récupérer ou créer l'identifiant de l'utilisateur
    if "sender_id" not in session:
        session["sender_id"] = "user_" + str(id(session))  # Créer un id unique

    payload = {
        "sender": session["sender_id"],
        "message": user_message
    }

    response = requests.post(RASA_URL, json=payload)

    if response.status_code != 200:
        return jsonify({"error": "Failed to connect to Rasa server"}), 500

    bot_responses = response.json()

    return jsonify(bot_responses)


if __name__ == "__main__":
    app.run(port=5000, debug=True)

# app = Flask(__name__)
#
# # L'adresse de ton serveur Rasa
# RASA_URL = "http://localhost:5005/webhooks/rest/webhook"
#
#
# @app.route("/chat", methods=["POST"])
# def chat():
#     user_message = request.json.get("message")
#
#     if not user_message:
#         return jsonify({"error": "No message provided"}), 400
#
#     # Envoyer le message à Rasa
#     payload = {
#         "sender": "user1",  # Tu peux mettre un ID unique pour chaque utilisateur
#         "message": user_message
#     }
#     response = requests.post(RASA_URL, json=payload)
#
#     if response.status_code != 200:
#         return jsonify({"error": "Failed to connect to Rasa server"}), 500
#
#     # Récupérer la réponse de Rasa
#     bot_responses = response.json()
#
#     # Renvoyer la réponse
#     return jsonify(bot_responses)
#
#
# if __name__ == "__main__":
#     app.run(port=8000, debug=True)