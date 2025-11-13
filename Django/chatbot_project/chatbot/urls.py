from django.urls import path
from . import views

urlpatterns = [
    path('', views.chatbot_view, name='chatbot'),  # MODIFIÉ : Suppression du préfixe
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('conversation/<int:conversation_id>/delete/', views.delete_conversation, name='delete_conversation'),
    path('submit-feedback/', views.submit_feedback, name='submit_feedback'),
]
