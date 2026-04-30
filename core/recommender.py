from .models import Activity, Itinerary, ItineraryItem

SLOTS = ['Morning', 'Afternoon', 'Evening']


def _phase(day, total):
    return 'Arrival' if day == 1 else ('Departure' if day == total else 'Mid-trip')


def _score(activity, inquiry, phase, slot):
    score = activity.base_score
    if activity.style == inquiry.travel_style:
        score += 4
    if activity.interest in inquiry.interests:
        score += 5
    if activity.day_suitability in (phase, 'Any'):
        score += 3
    if activity.time_slot in (slot, 'Flexible', 'Full-day'):
        score += 3
    return score


def generate_itinerary(inquiry):
    itinerary, _ = Itinerary.objects.get_or_create(inquiry=inquiry)
    itinerary.items.all().delete()

    activities = list(Activity.objects.filter(destination=inquiry.destination, travel_type=inquiry.travel_type))
    if not activities:
        activities = list(Activity.objects.filter(destination=inquiry.destination))
    if not activities:
        itinerary.summary = 'No matching activities found yet.'
        itinerary.save()
        return itinerary

    remaining = activities[:]
    for day in range(1, inquiry.duration_days + 1):
        phase = _phase(day, inquiry.duration_days)
        for slot in SLOTS:
            if not remaining:
                remaining = activities[:]
            ranked = sorted(remaining, key=lambda a: (-_score(a, inquiry, phase, slot), a.name))
            pick = ranked[0]
            remaining.remove(pick)
            ItineraryItem.objects.create(
                itinerary=itinerary,
                day_number=day,
                time_slot=slot,
                title=pick.name,
                notes=f"{phase} day • {pick.interest} • {pick.intensity} • {pick.style}",
            )

    itinerary.summary = f"Draft {inquiry.duration_days}-day itinerary for {inquiry.destination.name} ({inquiry.travel_style}) with activity-interest matching."
    itinerary.save()
    return itinerary
