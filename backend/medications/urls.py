from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PatientViewSet,
    MedicationViewSet,
    FacilityViewSet,
    PrescriptionViewSet,
    DosageScheduleViewSet,
)

router = DefaultRouter()
router.register(r'patients', PatientViewSet)
router.register(r'medications', MedicationViewSet)
router.register(r'facilities', FacilityViewSet)
router.register(r'prescriptions', PrescriptionViewSet)
router.register(r'dosageschedules', DosageScheduleViewSet)

urlpatterns = [
    path('api/', include(router.urls)),  # ✅ include the router only once
]