from django.contrib import admin
from .models import Medication, MedicationTimelineEntry, MedicationHistory, Facility

class MedicationHistoryInline(admin.TabularInline):
    model = MedicationHistory
    extra = 1
    readonly_fields = ('created_at',)
    fields = ('dose', 'route', 'frequency', 'source_facility', 'end_date', 'change_notes', 'created_at')
    show_change_link = True

    def save_model(self, request, obj, form, change):
        if not obj.contributor:
            obj.contributor = request.user
        super().save_model(request, obj, form, change)


@admin.register(MedicationTimelineEntry)
class MedicationTimelineEntryAdmin(admin.ModelAdmin):
    list_display = ('medication', 'start_date', 'end_date', 'current_dose', 'current_route', 'source_facility', 'current_frequency', 'conflicting')
    list_filter = ('medication', 'source_facility', 'conflicting')
    search_fields = ('medication__name', 'notes', 'conflict_notes')
    inlines = [MedicationHistoryInline]

    readonly_fields = ('conflicting', 'conflict_notes', 'contributor')

    def save_model(self, request, obj, form, change):
        if not obj.contributor:
            obj.contributor = request.user
        super().save_model(request, obj, form, change)
    
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if not instance.contributor:
                instance.contributor = request.user
            instance.save()
        formset.save_m2m()

@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(MedicationHistory)
class MedicationHistoryAdmin(admin.ModelAdmin):
    list_display = ('timeline_entry', 'dose', 'route', 'source_facility', 'end_date', 'created_at')
    list_filter = ('route', 'source_facility')
    search_fields = ('dose', 'change_notes')

@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


