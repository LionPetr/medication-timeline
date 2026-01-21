from django.db import models
from django.contrib.auth.models import User

class Medication(models.Model):
    name = models.CharField(max_length=1000)

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
    current_route = models.CharField(max_length=20, blank=True)
    source_facility = models.CharField(max_length=200, blank=True)

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

    def __str__(self):
        return f"{self.medication.name} ({self.start_date or 'Unknown'} - {self.end_date or 'Present'})"
    
    def save(self, *args, **kwargs):
        self.conflicting = False
        self.conflict_notes = ""

        if self.start_date:
            conflicts = MedicationTimelineEntry.objects.filter(
                medication = self.medication,
                start_date__isnull=False
            ).exclude(pk=self.pk).filter(
                source_facility__isnull=False
            )

            for entry in conflicts:
                entry_start = entry.start_date
                entry_end = entry.end_date or entry_start

                self_end = self.end_date or self.start_date

                if(self.start_date <= entry_end and self_end >= entry_start) and (self.source_facility != entry.source_facility):
                    self.conflicting = True
                    self.conflict_notes = (
                        f"conflict with {entry.source_facility} on overlapping date(s)."
                    )
                    break

        super().save(*args, **kwargs)

#change within a medication course
class MedicationHistory(models.Model):
    ROUTE_CHOICES = [
        ("oral", "Oral"),
        ("iv", "IV"),
        ("subcutaneous", "Subcutaneous"),
        ("topical", "Topical"),
        ("other", "Other"),
    ]

    timeline_entry = models.ForeignKey(
        MedicationTimelineEntry,
        on_delete=models.CASCADE,
        related_name="history"
    )
    dose = models.CharField(max_length=100, blank=True)
    frequency = models.CharField(max_length=100, blank=True)
    route = models.CharField(
        max_length=20,
        choices=ROUTE_CHOICES,
        blank=True
    )
    end_date = models.DateField(null=True, blank=True)
    source_facility = models.CharField(max_length=200, blank=True)

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
    
