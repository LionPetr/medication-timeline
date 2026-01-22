from django.db import models
from django.contrib.auth.models import User
from datetime import date
from .choices import Route
from django.db.models import Q
from django.db import transaction

class Patient(models.Model):
    name = models.CharField(max_length=255)

class Medication(models.Model):
    name = models.CharField(max_length=1000)

    def __str__(self):
        return self.name


class Facility(models.Model):
    name = models.CharField(max_length=255)
    external_id = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name

class Prescription(models.Model):
    """
    Represents a signle medication course on the main timeline
    """
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
    )
    medication = models.ForeignKey(
        Medication,
        on_delete=models.CASCADE,
        related_name="timeline_entries"
    )
    start_date = models.DateField(null=True, blank=True)
    source_facility = models.ForeignKey(
        Facility,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    notes = models.TextField(blank=True) #general notes
    contributor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="medication_entries"
    )
    

    def __str__(self):
        return f"{self.medication.name}"


class DosageSchedule(models.Model):
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
    )
    dose = models.CharField(max_length=100, blank=True)
    frequency = models.CharField(max_length=100, blank=True)
    route = models.CharField(
        max_length=20,
        choices=Route.choices,
        blank=True
    )
    duration = models.DurationField()
