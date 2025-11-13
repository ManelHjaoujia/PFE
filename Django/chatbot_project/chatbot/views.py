# chatbot/views.py (MODIFIÉ avec authentication et traitement des liens)
from django.shortcuts import render, redirect, get_object_or_404
import requests
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import ValeurLiquidative, Conversation, Message, Feedback
from datetime import date, timedelta
import random
import json
import time
import re
from django.db.models import Count, Avg, Sum, F, ExpressionWrapper, fields, Q
from django.utils import timezone


def process_bot_response(response_text):
    """
    Traite la réponse du bot pour s'assurer que les liens sont correctement formatés
    """
    if not response_text:
        return response_text

    # Si la réponse contient déjà des balises HTML de liens, les laisser telles quelles
    if '<a ' in response_text and '</a>' in response_text:
        return response_text

    # Regex améliorée pour détecter les URLs en excluant la ponctuation finale
    url_pattern = r'(https?://[^\s<>"{}|\\^`\[\]]+?)(?=[)\].,;:!?]*(?:\s|$))'
    processed_text = re.sub(
        url_pattern,
        r'<a href="\1" target="_blank" rel="noopener noreferrer">\1</a>',
        response_text
    )

    return processed_text


@csrf_exempt
@login_required
def chatbot_view(request):
    """Vue pour l'interface du chatbot"""
    # Get or create conversation based on session
    conversation_id = request.session.get('current_conversation_id')

    # If conversation_id is provided in URL, use that conversation
    if request.GET.get('conversation_id'):
        conversation_id = request.GET.get('conversation_id')
        request.session['current_conversation_id'] = conversation_id

    # If no conversation in session or starting a new one, create a new conversation
    if not conversation_id or request.GET.get('new', False):
        conversation = Conversation.objects.create()
        request.session['current_conversation_id'] = str(conversation.id)
    else:
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            # If conversation doesn't exist, create a new one
            conversation = Conversation.objects.create()
            request.session['current_conversation_id'] = str(conversation.id)

    if request.method == 'POST':
        user_input = request.POST.get('message')

        # Save user message to database
        Message.objects.create(
            conversation=conversation,
            sender='user',
            content=user_input
        )

        try:
            # Appel à l'API via ngrok
            response = requests.post('https://0cc1112e8d60.ngrok-free.app/chat',
                                     json={"message": user_input},
                                     timeout=10)  # Timeout de 10 secondes

            if response.status_code == 200:
                bot_data = response.json()
                if isinstance(bot_data, list) and len(bot_data) > 0:
                    bot_response = bot_data[0].get('text', 'Réponse vide du bot')
                else:
                    bot_response = 'Format de réponse non reconnu'
            else:
                bot_response = f'Erreur API: {response.status_code}'

        except requests.exceptions.RequestException as e:
            bot_response = f'Erreur de connexion: {str(e)}'

        # Traiter la réponse du bot pour les liens
        processed_bot_response = process_bot_response(bot_response)

        # Save bot response to database (avec le texte traité)
        Message.objects.create(
            conversation=conversation,
            sender='bot',
            content=processed_bot_response
        )

        return JsonResponse({'response': processed_bot_response})

    # Get messages for current conversation
    messages = Message.objects.filter(conversation=conversation).order_by('created_at')

    return render(request, 'chatbot/chat.html', {
        'active_page': 'chatbot',
        'conversation': conversation,
        'messages': messages
    })


# Ajoutez cette vue pour gérer la suppression des conversations
@login_required
def delete_conversation(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    conversation.delete()
    messages.success(request, "La conversation a été supprimée avec succès.")
    return redirect('chatbot')  # Redirige vers la page principale du chatbot


@login_required
def dashboard_view(request):
    """Vue pour le dashboard avec des statistiques en temps réel"""
    # Get today's date
    today = timezone.now().date()

    # Get conversations from today
    today_conversations = Conversation.objects.filter(created_at__date=today)
    today_conversations_count = today_conversations.count()

    # Get messages from today
    today_messages = Message.objects.filter(created_at__date=today)
    today_messages_count = today_messages.count()

    # Calculate average response time (time between user message and bot response)
    # Trouver toutes les paires de messages utilisateur-bot consécutifs
    avg_response_time = 0
    response_times = []

    for conversation in today_conversations:
        messages_list = list(conversation.messages.order_by('created_at'))
        for i in range(len(messages_list) - 1):
            if messages_list[i].sender == 'user' and messages_list[i + 1].sender == 'bot':
                response_time = (messages_list[i + 1].created_at - messages_list[i].created_at).total_seconds()
                response_times.append(response_time)

    # Calculer la moyenne si nous avons des temps de réponse
    if response_times:
        avg_response_time = round(sum(response_times) / len(response_times), 1)

    # Calculate total usage time (sum of conversation durations)
    total_usage_time = 0
    for conversation in today_conversations:
        messages = conversation.messages.order_by('created_at')
        if messages.count() >= 2:
            first_message = messages.first()
            last_message = messages.last()
            if first_message and last_message:
                duration = (last_message.created_at - first_message.created_at).total_seconds() / 60  # in minutes
                total_usage_time += duration

    # Round to 1 decimal place
    total_usage_time = round(total_usage_time, 1)

    # Get hourly activity data for today's chart
    hourly_data = []
    for hour in range(0, 24):
        hour_start = timezone.make_aware(
            timezone.datetime.combine(today, timezone.datetime.min.time()) + timedelta(hours=hour))
        hour_end = hour_start + timedelta(hours=1)

        hour_conversations = today_conversations.filter(created_at__gte=hour_start, created_at__lt=hour_end).count()
        hour_messages = today_messages.filter(created_at__gte=hour_start, created_at__lt=hour_end).count()

        hourly_data.append({
            'hour': f"{hour}:00",
            'conversations': hour_conversations,
            'messages': hour_messages
        })

    # Get recent conversations with details
    recent_conversations = []
    for conversation in today_conversations.order_by('-created_at')[:10]:
        messages_count = conversation.messages.count()

        # Calculate conversation duration
        if messages_count >= 2:
            first_message = conversation.messages.order_by('created_at').first()
            last_message = conversation.messages.order_by('created_at').last()
            if first_message and last_message:
                duration_seconds = (last_message.created_at - first_message.created_at).total_seconds()
                minutes = int(duration_seconds // 60)
                seconds = int(duration_seconds % 60)
                duration = f"{minutes}m {seconds}s"
            else:
                duration = "N/A"
        else:
            duration = "N/A"

        # Déterminer le statut de la conversation
        # Une conversation est considérée comme "Complétée" si le dernier message est du bot
        # et "En attente" si le dernier message est de l'utilisateur
        status = "En attente"
        if messages_count > 0:
            last_message = conversation.messages.order_by('-created_at').first()
            if last_message and last_message.sender == 'bot':
                status = "Complété"

        # Récupérer la satisfaction si elle existe
        try:
            feedback = conversation.feedback
            satisfaction = feedback.rating
        except (Feedback.DoesNotExist, AttributeError):
            satisfaction = 0  # Pas de feedback

        recent_conversations.append({
            'id': conversation.id,
            'date': conversation.created_at,
            'messages': messages_count,
            'status': status,
            'duration': duration,
            'satisfaction': satisfaction
        })

    # Calculer la satisfaction moyenne
    avg_satisfaction = Feedback.objects.filter(
        conversation__in=today_conversations
    ).aggregate(Avg('rating'))['rating__avg']

    if avg_satisfaction is None:
        avg_satisfaction = 0

    # Prepare stats for the template
    stats = {
        'today_messages_count': today_messages_count,
        'today_conversations_count': today_conversations_count,
        'avg_response_time': avg_response_time,
        'total_usage_time': total_usage_time,
    }

    return render(request, 'dashboard/dashboard.html', {
        'active_page': 'dashboard',
        'stats': stats,
        'hourly_data': hourly_data,
        'recent_conversations': recent_conversations
    })


@login_required
def submit_feedback(request):
    """Vue pour traiter les soumissions de feedback"""
    if request.method == 'POST':
        conversation_id = request.POST.get('conversation_id')
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')

        if not conversation_id or not rating:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Données manquantes'}, status=400)
            messages.error(request, "Veuillez fournir une évaluation.")
            return redirect('chatbot')

        try:
            conversation = Conversation.objects.get(id=conversation_id)

            # Vérifier si un feedback existe déjà pour cette conversation
            existing_feedback = Feedback.objects.filter(conversation=conversation).first()

            if existing_feedback:
                # Mettre à jour le feedback existant
                existing_feedback.rating = rating
                existing_feedback.comment = comment
                existing_feedback.save()
            else:
                # Créer un nouveau feedback
                Feedback.objects.create(
                    conversation=conversation,
                    rating=rating,
                    comment=comment
                )

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})

            messages.success(request, "Merci pour votre feedback!")
            return redirect('chatbot')

        except Conversation.DoesNotExist:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Conversation non trouvée'}, status=404)
            messages.error(request, "Conversation non trouvée.")
            return redirect('chatbot')

    # Si la méthode n'est pas POST
    return redirect('chatbot')
