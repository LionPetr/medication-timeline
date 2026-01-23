from rest_framework import serializers
from .models import Patient, Medication, Facility, Prescription, DosageSchedule
from datetime import timedelta

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

class DurationFieldSerializer(serializers.Field):
    """Custom field to convert integer days to/from timedelta"""
    def to_representation(self, value):
        # When reading, return as string like "7 days, 0:00:00"
        if isinstance(value, timedelta):
            return str(value)
        return value
    
    def to_internal_value(self, data):
        # When writing, accept integer and convert to timedelta
        if isinstance(data, int):
            return timedelta(days=data)
        if isinstance(data, str):
            try:
                days = int(data)
                return timedelta(days=days)
            except (ValueError, TypeError):
                pass
        return data

class DosageScheduleSerializer(serializers.ModelSerializer):
    duration = DurationFieldSerializer()
    
    class Meta:
        model = DosageSchedule
        fields = ['id', 'prescription', 'dose', 'frequency', 'route', 'duration']

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

    def create(self, validated_data):
        # On write, accept medication and patient IDs
        medication_id = self.initial_data.get('medication')
        patient_id = self.initial_data.get('patient')
        
        if medication_id:
            validated_data['medication_id'] = medication_id
        if patient_id:
            validated_data['patient_id'] = patient_id
            
        return super().create(validated_data)

class TimelineItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    medication = serializers.CharField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    natural_end_date = serializers.DateField()
    is_truncated = serializers.BooleanField()
