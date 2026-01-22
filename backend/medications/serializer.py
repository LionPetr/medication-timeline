from rest_framework import serializers
from .models import Patient, Medication, Facility, Prescription, DosageSchedule

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'name']

class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = ['id', 'name']

class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = ['id', 'name', 'external_id']

class DosageScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DosageSchedule
        fields = ['id', 'dose', 'frequency', 'route', 'duration']

class PrescriptionSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    medication = MedicationSerializer(read_only=True)
    source_facility = FacilitySerializer(read_only=True)
    dosage_schedules = DosageScheduleSerializer(
        source='dosageschedule_set', many=True, read_only=True
    )

    class Meta:
        model = Prescription
        fields = [
            'id',
            'patient',
            'medication',
            'start_date',
            'source_facility',
            'notes',
            'contributor',
            'dosage_schedules',
        ]