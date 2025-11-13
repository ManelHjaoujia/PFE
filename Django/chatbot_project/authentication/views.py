# authentication/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from pymongo import MongoClient
from django.conf import settings
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth import logout
from django.shortcuts import redirect


# Connexion MongoDB
def get_mongo_collection():
    client = MongoClient("mongodb://admin:admin@localhost:27017/")
    db = client["Bank_DB_client"]
    return db["Bank_client"]


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'authentication/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        """Surcharger pour mettre à jour le nombre de clients lors de la connexion"""
        response = super().form_valid(form)

        # Mettre à jour le nombre de clients dans la session
        try:
            collection = get_mongo_collection()
            clients_count = collection.count_documents({"Agence": self.request.user.agence})
            self.request.session['clients_count'] = clients_count
        except Exception:
            self.request.session['clients_count'] = 0

        return response

    def get_success_url(self):
        return reverse_lazy('chatbot')


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.email = form.cleaned_data.get('email')
            user.save()
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=email, password=password)
            if user:
                login(request, user)

                # Mettre à jour le nombre de clients dans la session
                try:
                    collection = get_mongo_collection()
                    clients_count = collection.count_documents({"Agence": user.agence})
                    request.session['clients_count'] = clients_count
                except Exception:
                    request.session['clients_count'] = 0

                messages.success(request, 'Inscription réussie!')
                return redirect('chatbot')
    else:
        form = CustomUserCreationForm()
    return render(request, 'authentication/register.html', {'form': form})


@login_required
def profile_view(request):
    # Récupérer les clients de l'agence de l'utilisateur
    try:
        collection = get_mongo_collection()
        clients = list(collection.find({"Agence": request.user.agence}))
        clients_count = len(clients)
        # Stocker dans la session
        request.session['clients_count'] = clients_count
    except Exception as e:
        clients = []
        clients_count = 0
        request.session['clients_count'] = 0
        messages.warning(request, "Impossible de se connecter à la base de données MongoDB.")

    context = {
        'user': request.user,
        'clients': clients,
        'clients_count': clients_count,
        'active_page': 'profile'
    }
    return render(request, 'authentication/profile.html', context)


@login_required
def get_agency_clients(request):
    """Fonction pour récupérer les clients de l'agence de l'utilisateur connecté"""
    try:
        collection = get_mongo_collection()
        clients = list(collection.find({"Agence": request.user.agence}))
        return clients
    except Exception as e:
        return []


def logout_view(request):
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès.")
    return redirect('auth:login')
