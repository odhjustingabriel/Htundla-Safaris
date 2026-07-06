from .models import Activity, Itinerary, ItineraryItem

SLOTS = ['Morning', 'Afternoon', 'Evening']


def _phase(day, total):
    return 'Arrival' if day == 1 else ('Departure' if day == total else 'Mid-trip')


def _interest_values(inquiry):
    selected = inquiry.interests or []
    additional = [part.strip() for part in inquiry.additional_interests.split(',') if part.strip()]
    return {interest.lower() for interest in [*selected, *additional]}


def _score(activity, inquiry, phase, slot, used_titles):
    score = activity.base_score
    if activity.style == inquiry.travel_style:
        score += 4
    if activity.interest.lower() in _interest_values(inquiry):
        score += 5
    if activity.day_suitability in (phase, 'Any'):
        score += 3
    if activity.time_slot in (slot, 'Flexible', 'Full-day'):
        score += 3
    if activity.name in used_titles:
        score -= 3
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

    activities_per_day = max(1, min(int(getattr(inquiry, 'activities_per_day', 3) or 3), len(SLOTS)))
    selected_slots = SLOTS[:activities_per_day]

    used = set()
    remaining = activities[:]
    for day in range(1, inquiry.duration_days + 1):
        phase = _phase(day, inquiry.duration_days)
        for slot in selected_slots:
            if not remaining:
                remaining = activities[:]
            ranked = sorted(remaining, key=lambda a: (-_score(a, inquiry, phase, slot, used), a.name))
            pick = ranked[0]
            remaining.remove(pick)
            used.add(pick.name)
            ItineraryItem.objects.create(
                itinerary=itinerary,
                day_number=day,
                time_slot=slot,
                title=pick.name,
                notes=f"{phase} day • {pick.interest} • {pick.intensity} • {pick.style}",
            )

    itinerary.summary = f"Draft {inquiry.duration_days}-day itinerary for {inquiry.destination.name} ({inquiry.travel_style}) with {activities_per_day} activity slot(s) per day and activity-interest matching."
    itinerary.save()
    return itinerary
