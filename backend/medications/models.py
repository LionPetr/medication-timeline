from django.db import models
from django.contrib.auth.models import User
from datetime import date
from .choices import Route

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
        self.conflicting = False
        self.conflict_notes = ""

        others = MedicationTimelineEntry.objects.filter(
            medication=self.medication,
            start_date__isnull=False,
            source_facility__isnull=False
        ).exclude(pk=self.pk)

        self_end = self.end_date or date.today() 

        updates = []

        for other in others:
            other_end = other.end_date or date.today()

            if self.start_date <= other_end and self_end >= other.start_date and (self.source_facility != other.source_facility):
                self.conflicting = True
                other.conflicting = True

                self.conflict_notes = f"Conflict with {other.source_facility} from {other.start_date} to {other_end}."
                other.conflict_notes = f"Conflict with {self.source_facility} from {self.start_date} to {self_end}."

                updates.append(other)

        
        super(MedicationTimelineEntry, self).save(update_fields=["conflicting", "conflict_notes"])

        for other in updates:
            MedicationTimelineEntry.objects.filter(pk=other.pk).update(
                conflicting=True,
                conflict_notes=other.conflict_notes
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
    
