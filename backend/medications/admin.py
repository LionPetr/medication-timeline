from django.contrib import admin
from .models import (
    Patient,
    Medication,
    Facility,
    Prescription,
    DosageSchedule,
)


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "external_id")
    search_fields = ("name", "external_id")


class DosageScheduleInline(admin.TabularInline):
    model = DosageSchedule
    extra = 0


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "patient",
        "medication",
        "start_date",
        "source_facility",
        "contributor",
    )
    list_filter = ("medication", "source_facility")
    search_fields = ("medication__name", "patient__name")
    inlines = [DosageScheduleInline]


@admin.register(DosageSchedule)
class DosageScheduleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "prescription",
        "dose",
        "route",
        "frequency",
        "duration",
        "end_date",  
    )
    list_filter = ("route",)


    def end_date(self, obj):
        if obj.prescription.start_date and obj.duration:
            return obj.prescription.start_date + obj.duration
        return None
    end_date.short_description = "End date"

