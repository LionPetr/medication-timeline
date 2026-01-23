from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Patient, Medication, Facility, Prescription, DosageSchedule
from .serializer import (
    PatientSerializer,
    MedicationSerializer,
    FacilitySerializer,
    PrescriptionSerializer,
    DosageScheduleSerializer,
)
from .services import build_timeline_items

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


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

    @action(detail=True, methods=["get"])
    def timeline(self, request, pk=None):
        """
        GET /patients/<pk>/timeline/
        Returns the patient's timeline as JSON
        """
        patient = self.get_object()

        prescriptions = Prescription.objects.filter(patient=patient).prefetch_related("dosageschedule_set", "medication")

        timeline_items = build_timeline_items(prescriptions)

        return Response(timeline_items)

    @action(detail=True, methods=["get"])
    def undated_medications(self, request, pk=None):
        """
        GET /patients/<pk>/undated_medications/
        Returns prescriptions without start_date
        """
        patient = self.get_object()

        prescriptions = Prescription.objects.filter(
            patient=patient,
            start_date__isnull=True
        ).prefetch_related("dosageschedule_set", "medication")

        serializer = PrescriptionSerializer(prescriptions, many=True)
        return Response(serializer.data)
