from django.db import models
from django.contrib.auth.models import User
from datetime import date
from .choices import Route
from django.db.models import Q
from django.db import transaction

class Medication(models.Model):
    name = models.CharField(max_length=1000)

    def __str__(self):
        return self.name


class Facility(models.Model):
    name = models.CharField(max_length=255)
    external_id = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name

class MedicationTimelineEntry(models.Model):
    """
    Represents a signle medication course on the main timeline
    """
    medication = models.ForeignKey(
        Medication,
        on_delete=models.CASCADE,
        related_name="timeline_entries"
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    current_dose = models.CharField(max_length=100, blank=True)
    current_frequency = models.CharField(max_length=100, blank=True)
    current_route = models.CharField(
        max_length=20,
        choices=Route.choices,
        blank=True
    )
    source_facility = models.ForeignKey(
        Facility,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    notes = models.TextField(blank=True) #general notes
    conflict_notes = models.TextField(blank=True)
    conflicting = models.BooleanField(default=False)

    contributor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="medication_entries"
    )

    def update_conflicts(self):
        today = date.today()

        MedicationTimelineEntry.objects.filter(
            medication=self.medication,
        ).update(conflicting=False, conflict_notes="")

        entries = MedicationTimelineEntry.objects.filter(
            medication=self.medication,
            start_date__isnull=False,
            source_facility__isnull=False
        )

        updates = []

        for entry in entries:
            entry_end = entry.end_date or today

            conflicting_entries = [
                other for other in entries
                if other.pk != entry.pk
                and other.start_date is not None
                and other.source_facility != entry.source_facility
                and other.current_dose != entry.current_dose
                and other.start_date <= entry_end
                and (other.end_date or today) >= entry.start_date
            ]

            if conflicting_entries:
                entry.conflicting = True
                notes = []
                for other in conflicting_entries:
                    notes.append(
                        f"Conflict with {other.source_facility} ({other.current_dose}) from {other.start_date} to {other.end_date or 'Present'}."
                    )
                    other.conflicting = True
                    other.conflict_notes = f"Conflict with {entry.source_facility} ({entry.current_dose}) from {entry.start_date} to {entry.end_date or 'Present'}."
                    updates.append(other)
                
                entry.conflict_notes = " | ".join(notes)
                updates.append(entry)

        with transaction.atomic():
            for entry in updates:
                MedicationTimelineEntry.objects.filter(pk=entry.pk).update(
                    conflicting=entry.conflicting,
                    conflict_notes=entry.conflict_notes
                )
                          
        
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.start_date:
            self.update_conflicts()

    def __str__(self):
        return f"{self.medication.name} ({self.start_date or 'Unknown'} - {self.end_date or 'Present'})"

#change within a medication course
class MedicationHistory(models.Model):
    timeline_entry = models.ForeignKey(
        MedicationTimelineEntry,
        on_delete=models.CASCADE,
        related_name="history"
    )
    dose = models.CharField(max_length=100, blank=True)
    frequency = models.CharField(max_length=100, blank=True)
    route = models.CharField(
        max_length=20,
        choices=Route.choices,
        blank=True
    )
    end_date = models.DateField(null=True, blank=True)
    
    source_facility = models.ForeignKey(
        Facility,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    change_notes = models.TextField(blank=True)

    contributor = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="medication_history_entries"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.pk is None:
            last_entry = (
                MedicationHistory.objects
                .filter(timeline_entry=self.timeline_entry)
                .order_by("-created_at")
                .first()
            )
            
            if last_entry:
                fields_to_carry_forward = [
                    "dose", 
                    "route",
                    "end_date",
                    "source_facility",
                    "frequency",
                ]
                for field in fields_to_carry_forward:
                    current_value = getattr(self, field)
                    previous_value = getattr(last_entry, field)

                    if current_value in ("", None):
                        setattr(self, field, previous_value)

        super().save(*args, **kwargs)

        latest = self.timeline_entry.history.order_by("-created_at").first()
        if latest:
            self.timeline_entry.current_dose = latest.dose
            self.timeline_entry.current_route = latest.route
            self.timeline_entry.source_facility = latest.source_facility
            self.timeline_entry.end_date = latest.end_date
            self.timeline_entry.save()

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.timeline_entry.medication.name} ({self.dose}, {self.route}, {self.created_at.date()})"
    
