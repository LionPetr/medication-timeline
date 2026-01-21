from django.db import models

class Route(models.TextChoices):
    ORAL = 'oral', 'Oral'
    INTRAVENOUS = 'intravenous', 'Intravenous'
    INTRAMUSCULAR = 'intramuscular', 'Intramuscular'
    SUBCUTANEOUS = 'subcutaneous', 'Subcutaneous'
    TOPICAL = 'topical', 'Topical'
    INHALATION = 'inhalation', 'Inhalation'
    RECTAL = 'rectal', 'Rectal'
    OTHER = 'other', 'Other'