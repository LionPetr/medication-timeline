from collections import defaultdict
from django.db.models import Sum
from datetime import timedelta

def get_prescription_total_duration(prescription):
    agg = prescription.dosageschedule_set.aggregate(
        total=Sum("duration")
    )
    return agg["total"] or timedelta(0)


def get_prescription_end_date(prescription):
    if not prescription.start_date:
        return None
    return prescription.start_date + get_prescription_total_duration(prescription)

def get_truncated_prescriptions(prescriptions):
    """
    Returns:
        dict[prescription_id] = cutoff_date
    """
    result = {}
    by_medication = defaultdict(list)

    for p in prescriptions:
        if p.start_date:
            by_medication[p.medication_id].append(p)

    for meds in by_medication.values():
        meds.sort(key=lambda p: p.start_date)

        for i, p in enumerate(meds):
            natural_end = get_prescription_end_date(p)
            if not natural_end:
                continue

            if i + 1 < len(meds):
                next_p = meds[i + 1]
                if next_p.start_date < natural_end:
                    result[p.id] = next_p.start_date

    return result


def build_timeline_items(prescriptions):
    cutoffs = get_truncated_prescriptions(prescriptions)
    items = []

    for p in prescriptions:
        if not p.start_date:
            continue

        natural_end = get_prescription_end_date(p)
        if not natural_end:
            continue

        cutoff = cutoffs.get(p.id)
        end_date = cutoff if cutoff else natural_end

        dosages = [
            {
                "dose": d.dose,
                "frequency": d.frequency,
                "route": d.route,
                "duration": str(d.duration) if d.duration else None
            }
            for d in p.dosageschedule_set.all()
        ]

        items.append({
            "id": p.id,
            "medication": p.medication.name,
            "start_date": p.start_date,
            "end_date": end_date,
            "natural_end_date": natural_end,
            "is_truncated": cutoff is not None,
            "dosages": dosages,
        })

    return items
