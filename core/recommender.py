from .models import Activity, Itinerary, ItineraryItem

def generate_itinerary(inquiry):
    itinerary, _ = Itinerary.objects.get_or_create(inquiry=inquiry)
    itinerary.items.all().delete()
    activities = list(Activity.objects.filter(destination=inquiry.destination, travel_type=inquiry.travel_type))
    for a in activities:
        a._score = a.base_score + (2 if a.style == inquiry.travel_style else 0) + (3 if a.interest in inquiry.interests else 0)
    activities.sort(key=lambda a: (-a._score, a.day_suitability, a.time_slot, a.name))
    if not activities:
        itinerary.summary = 'No matching activities found yet.'
        itinerary.save(); return itinerary
    slots = ['Morning','Afternoon','Evening']
    for day in range(1, inquiry.duration_days+1):
        phase = 'Arrival' if day == 1 else ('Departure' if day == inquiry.duration_days else 'Mid-trip')
        candidates = [a for a in activities if a.day_suitability in (phase,'Any')]
        for i, slot in enumerate(slots):
            pick = next((a for a in candidates if a.time_slot in (slot,'Flexible','Full-day')), candidates[(day+i) % len(candidates)])
            ItineraryItem.objects.create(itinerary=itinerary, day_number=day, time_slot=slot, title=pick.name, notes=f'{pick.intensity} intensity')
    itinerary.summary = f'Draft {inquiry.duration_days}-day itinerary for {inquiry.destination.name}.'
    itinerary.save(); return itinerary
