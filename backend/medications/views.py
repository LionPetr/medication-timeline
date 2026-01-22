from django.shortcuts import render

from rest_framework import viewsets
from .models import Patient, Medication, Facility, Prescription, DosageSchedule
from .serializer import (
    PatientSerializer,
    MedicationSerializer,
    FacilitySerializer,
    PrescriptionSerializer,
    DosageScheduleSerializer,
)

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

class MedicationViewSet(viewsets.ModelViewSet):
    queryset = Medication.objects.all()
    serializer_class = MedicationSerializer

class FacilityViewSet(viewsets.ModelViewSet):
    queryset = Facility.objects.all()
    serializer_class = FacilitySerializer

class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer

class DosageScheduleViewSet(viewsets.ModelViewSet):
    queryset = DosageSchedule.objects.all()
    serializer_class = DosageScheduleSerializer
