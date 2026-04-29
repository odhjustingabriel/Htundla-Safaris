from django.core.management.base import BaseCommand
from core.models import Destination, Activity

DESTS=['Nairobi','Maasai Mara','Amboseli','Lake Nakuru','Mount Kenya / Nanyuki','Lake Naivasha & Hell’s Gate','Samburu','Tsavo','Laikipia / Ol Pejeta','Kenyan Coast']
class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for d in DESTS:
            dest,_=Destination.objects.get_or_create(name=d, defaults={'travel_type':'Safari'})
            Activity.objects.get_or_create(destination=dest,name='Game Drive',travel_type='Safari',style='Standard',interest='Game Drive',time_slot='Morning',day_suitability='Any',intensity='Moderate')
            Activity.objects.get_or_create(destination=dest,name='Cultural Visit',travel_type='Safari',style='Budget-friendly',interest='Culture',time_slot='Afternoon',day_suitability='Mid-trip',intensity='Light')
            Activity.objects.get_or_create(destination=dest,name='Sunset Photography',travel_type='Safari',style='Luxury',interest='Photography',time_slot='Evening',day_suitability='Any',intensity='Light')
        self.stdout.write(self.style.SUCCESS('Seeded sample destinations and activities'))
