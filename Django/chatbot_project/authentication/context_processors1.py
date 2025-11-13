from pymongo import MongoClient
from django.conf import settings


def get_mongo_collection():
    """Fonction pour se connecter à MongoDB"""
    try:
        client = MongoClient("mongodb://admin:admin@localhost:27017/")
        db = client["Bank_DB_client"]
        return db["Bank_client"]
    except Exception:
        return None


def user_clients_count(request):
    """Context processor pour ajouter le nombre de clients à tous les templates"""
    if request.user.is_authenticated:
        try:
            collection = get_mongo_collection()
            if collection is not None:
                clients_count = collection.count_documents({"Agence": request.user.agence})
                return {'clients_count': clients_count}
        except Exception:
            pass

    return {'clients_count': 0}
