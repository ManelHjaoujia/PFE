# authentication/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    AGENCES_CHOICES = [
        ('CENTRALE CUN', 'Centrale CUN'),
        ('LES BERGES DU LAC', 'Les Berges du Lac'),
        ('ENNASR', 'Ennasr'),
        ('MEGRINE', 'Megrine'),
        ('SOUSSE SAHLOUL', 'Sousse Sahloul'),
        ('ARIANA', 'Ariana'),
        ('SFAX', 'Sfax'),
        ('BARDO', 'Bardo'),
        ('BIZERT', 'Bizert'),
        ('NABEUL', 'Nabeul'),
        ('MSAKEN', 'Msaken'),
        ('BEN AROUS', 'Ben Arous'),
        ('LA MARSA', 'La Marsa'),
        ('SOUSSE', 'Sousse'),
        ('GABES', 'Gabes'),
        ('MONASTIR', 'Monastir'),
        ('BEJA', 'Beja'),
        ('L''AOUINA', 'L`AOUINA'),
        ('BOUMHEL', 'Boumhel'),
        ('EL MENZAH 4', 'El Menzah 4'),
        ('HRAIRIA', 'Hrairia'),
        ('MONTPLAISIR', 'Montplaisir'),
        ('KAIRAOUAN', 'Kairaouan'),
        ('SFAX II', 'Sfax II'),
        ('MOKNINE', 'Moknine'),
        ('LAC II', 'Lac II'),
        ('KRAM', 'Kram'),
        ('DJERBA', 'Djerba'),
        ('MANOUBA', 'Manouba'),
        ('JENDOUBA', 'Jendouba'),
        ('PASTEUR', 'Pasteur'),
    ]

    first_name = models.CharField(max_length=30, verbose_name="Prénom")
    last_name = models.CharField(max_length=30, verbose_name="Nom")
    email = models.EmailField(unique=True, verbose_name="Email")
    agence = models.CharField(max_length=20, choices=AGENCES_CHOICES, verbose_name="Agence")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'agence']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.get_agence_display()}"

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
