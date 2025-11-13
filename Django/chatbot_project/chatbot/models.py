from django.db import models
from django.utils import timezone


class Conversation(models.Model):
    """Modèle pour stocker les conversations"""
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conversation {self.id} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-created_at']


class Message(models.Model):
    """Modèle pour stocker les messages"""
    SENDER_CHOICES = [
        ('user', 'Utilisateur'),
        ('bot', 'Bot'),
    ]

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}: {self.content[:50]}..."

    class Meta:
        ordering = ['created_at']

class ValeurLiquidative(models.Model):
    date = models.DateField(unique=True)
    valeur = models.DecimalField(max_digits=10, decimal_places=2)
    variation = models.DecimalField(max_digits=5, decimal_places=2)
    est_positive = models.BooleanField(default=True)

    def variation_est_positive(self):
        return self.variation >= 0

    def __str__(self):
        signe = '+' if self.variation_est_positive() else ''
        return f"{self.date} - {self.valeur} € ({signe}{self.variation} €)"


class Feedback(models.Model):
    """Modèle pour stocker les évaluations des utilisateurs"""
    RATING_CHOICES = [
        (1, '1 - Très insatisfait'),
        (2, '2 - Insatisfait'),
        (3, '3 - Neutre'),
        (4, '4 - Satisfait'),
        (5, '5 - Très satisfait'),
    ]

    conversation = models.OneToOneField(Conversation, on_delete=models.CASCADE, related_name='feedback')
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback pour conversation {self.conversation.id}: {self.get_rating_display()}"