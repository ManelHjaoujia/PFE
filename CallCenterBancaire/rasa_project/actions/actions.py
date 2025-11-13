# This files contains your custom actions which can be used to run
import re
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from pymongo import MongoClient
from urllib.parse import quote
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from datetime import datetime
import os

class ActionConsulterSolde(Action):
    def name(self) -> Text:
        return "action_consulter_solde"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        nom_complet = tracker.get_slot("nom_client")
        prenom_client = tracker.get_slot("prenom_client")
        num_compte = tracker.get_slot("num_compte")

        if not nom_complet or not num_compte or not prenom_client:
            dispatcher.utter_message(text="Pour consulter votre solde, veuillez fournir votre nom, prénom et numéro de compte ?")
            return []

        client = MongoClient("mongodb://admin:admin@localhost:27017/")
        db = client["Bank_DB_client"]
        collection = db["Bank_client"]

        # Recherche du client par nom, prénom et numéro de compte
        result_cursor = collection.find({
            "Nom_client": nom_complet,
            "Prénom": prenom_client,
            "Numéro de compte": num_compte
        }).sort("Date", -1)  # Trier par la date en ordre décroissant

        # Convertir le curseur en une liste
        result = list(result_cursor)

        # Si des résultats sont trouvés
        if result:
            latest_record = result[0]  # Le premier enregistrement est celui avec la date la plus récente
            solde = latest_record.get("Solde", "inconnu")  # Modifier ici pour récupérer le champ 'Solde'
            dispatcher.utter_message(text=f"Votre solde est {solde} TND")
        else:
            dispatcher.utter_message(text="Informations non trouvées.")

        return []


class ActionConsulterActions(Action):
    def name(self) -> Text:
        return "action_consulter_actions"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        nom_complet = tracker.get_slot("nom_client")
        prenom_client = tracker.get_slot("prenom_client")
        num_compte = tracker.get_slot("num_compte")
        rib = tracker.get_slot("rib")

        if not nom_complet or not num_compte or not prenom_client:
            dispatcher.utter_message(text="Pour consulter le nombre d’actions, veuillez fournir votre nom, prénom, RIB et numéro de compte ?")
            return []

        client = MongoClient("mongodb://admin:admin@localhost:27017/")
        db = client["Bank_DB_client"]
        collection = db["Bank_client"]

        # Recherche du client par nom, prénom et numéro de compte
        result_cursor = collection.find({
            "Nom_client": nom_complet,
            "Prénom": prenom_client,
            "Numéro de compte": num_compte,
            "RIB": rib
        }).sort("Date", -1)  # Trier par la date en ordre décroissant

        # Convertir le curseur en une liste
        result = list(result_cursor)

        # Si des résultats sont trouvés
        if result:
            latest_record = result[0]  # Le premier enregistrement est celui avec la date la plus récente
            actions = latest_record.get("Nombre dactions", "inconnu")
            dispatcher.utter_message(text=f"Vous possédez {actions} actions.")
        else:
            dispatcher.utter_message(text="Informations non trouvées.")

        return []


class ActionConsulterOperations(Action):
    def name(self) -> Text:
        return "action_consulter_operations"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        nom_complet = tracker.get_slot("nom_client")
        prenom_client = tracker.get_slot("prenom_client")
        rib = tracker.get_slot("rib")

        print(f"REÇU -> nom_complet: {nom_complet}, prenom_client: {prenom_client}, rib: {rib}")

        if not nom_complet or not rib or not prenom_client:
            dispatcher.utter_message(text="Vous souhaitez consulter vos dernières opérations, veuillez fournir votre nom, prénom et RIB ?")
            return []

        client = MongoClient("mongodb://admin:admin@localhost:27017/")
        db = client["Bank_DB_client"]
        collection = db["Bank_client"]

        # Récupérer les 3 dernières opérations du client
        result_cursor = collection.find({
            "Nom_client": {"$regex": f"^{nom_complet}$", "$options": "i"},
            "Prénom": {"$regex": f"^{prenom_client}$", "$options": "i"},
            "RIB": rib
        }).sort("Date", -1).limit(3)

        result_list = list(result_cursor)

        if result_list:
            message = "Voici vos 3 dernières opérations :\n"
            for record in result_list:
                operation = record.get("Consultation opérations", "inconnue")
                date = record.get("Date", "date inconnue")
                message += f"- {operation} le {date}\n"
            dispatcher.utter_message(text=message)
        else:
            dispatcher.utter_message(text="Impossible de trouver des opérations pour ce client.")

        return []

# Fonction utilitaire pour nettoyer les noms de fichiers
def safe_filename(text: str) -> str:
    """Nettoie le texte pour créer des noms de fichiers valides"""
    # Normaliser les espaces et caractères spéciaux
    text = re.sub(r'\s+', '_', text.strip())  # Remplace TOUS les espaces
    return re.sub(r'[^\w.-]', '', text)  # Supprime caractères non alphanumériques

class ActionConsulterExtrait(Action):
    def name(self) -> Text:
        return "action_consulter_extrait"

    def run(self, dispatcher: CollectingDispatcher,
           tracker: Tracker,
           domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        nom_complet = tracker.get_slot("nom_client")
        prenom_client = tracker.get_slot("prenom_client")
        num_compte = tracker.get_slot("num_compte")
        date_debut = tracker.get_slot("date_debut")
        date_fin = tracker.get_slot("date_fin")

        if not nom_complet or not prenom_client or not num_compte or not date_debut or not date_fin:
            dispatcher.utter_message(text="Vous souhaitez un extrait de compte, veuillez fournir votre nom, prénom, numéro de compte, date_debut et date_fin?")
            return []

        # Connect to MongoDB
        client = MongoClient("mongodb://admin:admin@localhost:27017/")
        db = client["Bank_DB_client"]
        collection = db["Bank_client"]

        # Convert input date strings to datetime objects
        try:
            date_debut_obj = datetime.strptime(date_debut, '%Y-%m-%d')
            date_fin_obj = datetime.strptime(date_fin, '%Y-%m-%d')
        except ValueError:
            dispatcher.utter_message(text="Les dates doivent être au format YYYY-MM-DD.")
            return []

        # Fetch the client details
        result_cursor = collection.find({
            "Nom_client": nom_complet,
            "Prénom": prenom_client,
            "Numéro de compte": num_compte
        })

        result = list(result_cursor)

        if result:
            # Find the earliest record before the start date
            earliest_record = collection.find({
                "Nom_client": nom_complet,
                "Prénom": prenom_client,
                "Numéro de compte": num_compte,
                "Date": {"$gte": date_debut_obj}
            }).sort("Date", 1).limit(1)

            earliest_record = list(earliest_record)

            if earliest_record:
                action_depart = earliest_record[0].get("Nombre dactions", "inconnu")
            else:
                action_depart = 0

            # Solde final
            latest_record = collection.find({
               "Nom_client": nom_complet,
               "Prénom": prenom_client,
               "Numéro de compte": num_compte,
               "Date": {"$lte": date_fin_obj}
            }).sort("Date", -1).limit(1)

            latest_record = list(latest_record)
            action_final = latest_record[0].get("Nombre dactions", 0) if latest_record else 0

            latest_vl = collection.find({
               "Nom_client": nom_complet,
               "Prénom": prenom_client,
               "Numéro de compte": num_compte,
               "Date": {"$lte": date_fin_obj}
            }).sort("Date", -1).limit(1)

            latest_vl = list(latest_vl)
            vl_final = latest_vl[0].get("VL", 0) if latest_vl else 0

            latest_montant = collection.find({
               "Nom_client": nom_complet,
               "Prénom": prenom_client,
               "Numéro de compte": num_compte,
               "Date": {"$lte": date_fin_obj}
            }).sort("Date", -1).limit(1)

            latest_montant = list(latest_montant)
            montant_final = latest_montant[0].get("Solde", 0) if latest_montant else 0

            agence = result[0].get("Agence", "inconnue")

            # Filter transactions
            transactions = collection.find({
                "Nom_client": nom_complet,
                "Prénom": prenom_client,
                "Numéro de compte": num_compte,
                "Date": {"$gte": date_debut_obj, "$lte": date_fin_obj}
            })

            rows = []
            numero_ligne = 1
            for txn in transactions:
                raw_date = txn.get("Date", "inconnu")
                formatted_date = raw_date.strftime("%d-%m-%Y") if isinstance(raw_date, datetime) else "inconnu"
                rows.append([
                    numero_ligne,
                    txn.get("Consultation opérations", "inconnu"),
                    formatted_date,
                    txn.get("Nombre dactions", "inconnue"),
                    txn.get("VL", "inconnue"),
                    txn.get("Solde", "inconnu"),
                    txn.get("RIB", "inconnu")
                ])
                numero_ligne += 1

            # Nom du fichier PDF
            # Remplacer les espaces dans les noms par des underscores
            safe_nom = nom_complet.replace(" ", "_")
            safe_prenom = prenom_client.replace(" ", "_")

            filename = f"{safe_nom}_{safe_prenom}_extrait.pdf"
            filepath = os.path.join("static", filename)  # PDF sera enregistré dans le dossier 'static'
            os.makedirs("static", exist_ok=True)  # Crée le dossier 'static' s'il n'existe pas

            self.save_transaction_to_pdf(filepath, rows, nom_complet, prenom_client, num_compte, agence, action_depart, action_final, date_debut, date_fin, vl_final, montant_final)

            # Générer le lien vers le PDF
            pdf_link = f"http://localhost:5500/static/{filename}"  # adapte l'URL selon ton serveur si besoin

            dispatcher.utter_message(text=f"Votre extrait de compte a été généré avec succès. Cliquez ici pour le télécharger : ({pdf_link})")
        else:
            dispatcher.utter_message(text="Informations non trouvées pour ce client.")

        return []

    def save_transaction_to_pdf(self, filepath, rows, nom_complet, prenom_client, num_compte, agence, solde_depart, solde_final, date_debut, date_fin, vl_final, montant_final):
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        header_centered = f"""
        <para align="center">
            <font size="18"><b>Historique des Souscriptions et Rachats</b></font><br/><br/>
            <b>Du : {date_debut} &nbsp;&nbsp;&nbsp;&nbsp;Au : {date_fin}</b><br/><br/>
        </para>
        """

        header_left = f"""
        <para align="left">
            <b>Portefeuille :</b> TUNISO EMIRATIE SICAV<br/><br/>
            <b>Souscripteur :</b> {nom_complet} {prenom_client}<br/><br/>
            <b>Numéro Compte :</b> {num_compte}<br/><br/>
            <b>Agence :</b> {agence}<br/><br/>
            <b>Solde Départ du {date_debut} :</b> {solde_depart}<br/><br/>
        </para>
        """

        elements.append(Paragraph(header_centered, styles["Normal"]))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(header_left, styles["Normal"]))
        elements.append(Spacer(1, 12))

        data = [["N° Opération", "Code Opération", "Date Opération", "Quantité", "VL", "Montant Net", "N° du compte RIB"]]

        def safe_float_conversion(value):
            try:
                return float(value)
            except (ValueError, TypeError):
                return 0.0

        for row in rows:
            data.append([
                str(row[0]), str(row[1]), str(row[2]), str(row[3]),
                f"{safe_float_conversion(row[4]):,.2f}",
                f"{safe_float_conversion(row[5]):,.2f}",
                str(row[6])
            ])

        col_widths = [0.9 * inch, 1.1 * inch, 1.1 * inch, 1.1 * inch, 1.1 * inch, 1.2 * inch, 2.0 * inch]
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#003366")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 12))

        footer_text = f"""
        <para align="left">
            <br/>
            <b>Solde Final au {date_fin} :</b> {solde_final}<br/><br/>
            <b>Valeur liquidative au {date_fin} :</b> {vl_final}<br/><br/>
            <b>Valorisation du portefeuille au {date_fin} :</b> {montant_final}
        </para>
        """
        elements.append(Paragraph(footer_text, styles["Normal"]))
        doc.build(elements)