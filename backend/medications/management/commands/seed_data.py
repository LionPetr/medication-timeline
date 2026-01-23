from django.core.management.base import BaseCommand
from medications.models import Patient, Medication, Facility, Prescription, DosageSchedule
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Seed initial data for testing'

    def handle(self, *args, **options):
        # Create patient if doesn't exist
        patient, created = Patient.objects.get_or_create(
            id=1,
            defaults={'name': 'Test Patient'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created test patient'))

        # Create some medications
        med1, _ = Medication.objects.get_or_create(name='Aspirin')
        med2, _ = Medication.objects.get_or_create(name='Ibuprofen')
        med3, _ = Medication.objects.get_or_create(name='Paracetamol')
        
        self.stdout.write(self.style.SUCCESS('Medications created'))

        # Create a facility
        facility, _ = Facility.objects.get_or_create(
            name='General Hospital',
            external_id='GH001'
        )

        # Create some prescriptions
        if not Prescription.objects.filter(patient=patient, medication=med1).exists():
            prescription1 = Prescription.objects.create(
                patient=patient,
                medication=med1,
                start_date=date.today() - timedelta(days=10),
                source_facility=facility,
                notes='For pain management'
            )
            DosageSchedule.objects.create(
                prescription=prescription1,
                dose='100mg',
                frequency='twice daily',
                route='oral',
                duration=timedelta(days=7)
            )

        if not Prescription.objects.filter(patient=patient, medication=med2).exists():
            prescription2 = Prescription.objects.create(
                patient=patient,
                medication=med2,
                start_date=date.today() - timedelta(days=5),
                source_facility=facility,
                notes='Anti-inflammatory'
            )
            DosageSchedule.objects.create(
                prescription=prescription2,
                dose='200mg',
                frequency='three times daily',
                route='oral',
                duration=timedelta(days=5)
            )

        if not Prescription.objects.filter(patient=patient, medication=med3, start_date__isnull=True).exists():
            prescription3 = Prescription.objects.create(
                patient=patient,
                medication=med3,
                start_date=None,  # Undated medication
                notes='As needed for fever'
            )
            DosageSchedule.objects.create(
                prescription=prescription3,
                dose='500mg',
                frequency='every 6 hours',
                route='oral',
                duration=timedelta(days=1)
            )

        self.stdout.write(self.style.SUCCESS('Sample prescriptions created'))
