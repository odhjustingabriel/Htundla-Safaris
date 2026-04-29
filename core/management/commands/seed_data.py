from django.core.management.base import BaseCommand
from core.models import Destination, Activity

STYLE_MAP = {'BF': 'Budget-friendly', 'STD': 'Standard', 'LUX': 'Luxury'}
DATA = {
'Nairobi': [('Nairobi National Park game drive','STD'),('Nairobi Safari Walk visit','BF'),('Giraffe Centre / conservation stop','BF'),('Karen / city photo spots','BF'),('Carnivore-style local cuisine dinner','STD'),('Nairobi National Museum / city sightseeing','BF'),('Karura-style guided nature walk','BF'),('Team-building garden or conference lawn session','STD'),('Premium rooftop city dinner / sundowner','LUX'),('Full-day MICE venue + city excursion combo','LUX')],
'Maasai Mara': [('Morning game drive','STD'),('Evening game drive','STD'),('Big cat / animal spotting circuit','STD'),('Maasai village cultural immersion','BF'),('Savannah photo site stop','BF'),('Guided nature walk in safe designated area','STD'),('Bush breakfast / picnic viewpoint','STD'),('Campsite safari night','BF'),('Hot air balloon safari','LUX'),('Luxury lodge sundowner and photo deck session','LUX')],
'Amboseli': [('Elephant-viewing game drive','STD'),('Mount Kilimanjaro photo viewpoint stop','BF'),('Bird spotting around wetlands/swamps','BF'),('Maasai cultural visit','STD'),('Nature walk near designated safe areas','STD'),('Local cuisine tasting stop','BF'),('Campsite evening experience','BF'),('Sunrise photography session','STD'),('Premium lodge viewing deck experience','LUX'),('Private extended game drive with sundowner','LUX')],
'Lake Nakuru': [('Flamingo / bird spotting drive','BF'),('Rhino / animal spotting drive','STD'),('Baboon Cliff viewpoint','BF'),('Lion Hill / Out of Africa photo stop','BF'),('Makalia Falls sightseeing','BF'),('Picnic + lake view session','BF'),('Guided nature walk around safe viewpoints','STD'),('Campsite stay','BF'),('Premium bird photography circuit','LUX'),('Luxury lodge lake-view experience','LUX')],
'Mount Kenya / Nanyuki': [('3-day Naro Moru trek','STD'),('5-day Chogoria-Sirimon traverse','LUX'),('Lower-slope guided nature walk','BF'),('Bird spotting in forest zone','BF'),('Campsite mountain experience','BF'),('Cave exploration / scenic stop','STD'),('Highland photo site session','STD'),('Nanyuki local cuisine stop','BF'),('Luxury mountain lodge recovery stay','LUX'),('Short acclimatization hike + scenic picnic','STD')],
'Lake Naivasha & Hell’s Gate': [('Hell\'s Gate hiking trail','BF'),('Hell\'s Gate cycling experience','BF'),('Fischer\'s Tower photo stop','STD'),('Lake Naivasha boat ride / hippo spotting','STD'),('Crescent Island-style walking wildlife experience','STD'),('Bird spotting around the lake','BF'),('Campsite lake experience','BF'),('Local cuisine lunch by the lake','STD'),('Geothermal spa / premium relaxation add-on','LUX'),('Premium lodge + Rift Valley scenic dinner','LUX')],
'Samburu': [('Game drive for northern species spotting','STD'),('Samburu cultural immersion visit','STD'),('Scenic riverbank photo stop','BF'),('Bird spotting session','BF'),('Guided nature walk with local guide','STD'),('Bush breakfast / picnic stop','STD'),('Campsite wilderness night','BF'),('Local cuisine / community meal experience','BF'),('Luxury tented camp sundowner','LUX'),('Private photography-focused game circuit','LUX')],
'Tsavo': [('Tsavo East game drive','STD'),('Tsavo West scenic drive','STD'),('Red elephant / big game spotting','STD'),('Bird spotting session','BF'),('Trekking / short guided trail in safe zone','STD'),('Mzima/Mudanda-style viewpoint stop','STD'),('Campsite wilderness experience','BF'),('Nature walk in controlled area','BF'),('Premium lodge bush dinner','LUX'),('Extended private multi-park safari circuit','LUX')],
'Laikipia / Ol Pejeta': [('Rhino / animal spotting drive','STD'),('Conservation experience / rhino tracking-style activity','STD'),('Guided walking safari','STD'),('Bird spotting session','BF'),('Community / ranch culture immersion','STD'),('Scenic photo stop across conservancy landscapes','BF'),('Campsite bush experience','BF'),('Local cuisine tasting at camp/lodge','STD'),('Luxury conservancy stay','LUX'),('Premium private game drive + sundowner','LUX')],
'Kenyan Coast': [('Snorkelling experience','STD'),('Beach sightseeing / shoreline nature walk','BF'),('Swahili local cuisine tasting','BF'),('Old Town / heritage culture immersion','STD'),('Fort / ruins / historical photo tour','STD'),('Bird spotting in coastal forest or creek area','BF'),('Beach camping experience','BF'),('Reef / marine photo site excursion','STD'),('Luxury dhow dinner / premium beach resort experience','LUX'),('Premium coral reef / island excursion','LUX')],
}


def classify(name):
    n = name.lower()
    if 'mice' in n or 'conference' in n or 'team-building' in n: return 'MICE'
    if 'bird' in n: return 'Birding'
    if 'culture' in n or 'village' in n or 'heritage' in n or 'museum' in n: return 'Culture'
    if 'photo' in n: return 'Photography'
    if 'hike' in n or 'trek' in n or 'cycling' in n: return 'Adventure'
    if 'beach' in n or 'reef' in n or 'snork' in n or 'marine' in n: return 'Beach'
    if 'cuisine' in n or 'dinner' in n or 'lunch' in n or 'breakfast' in n: return 'Cuisine'
    if 'camp' in n: return 'Camping'
    if 'walk' in n: return 'Nature Walk'
    return 'Game Drive'

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for destination, activities in DATA.items():
            dest, _ = Destination.objects.get_or_create(name=destination, defaults={'travel_type': 'Safari'})
            for i, (name, style_code) in enumerate(activities):
                tt = 'MICE' if 'mice' in name.lower() or 'conference' in name.lower() else 'Safari'
                interest = classify(name)
                time_slot = 'Full-day' if 'full-day' in name.lower() else ('Evening' if 'dinner' in name.lower() or 'sundowner' in name.lower() else ('Morning' if 'morning' in name.lower() or 'sunrise' in name.lower() else 'Afternoon'))
                day_fit = 'Arrival' if 'city sightseeing' in name.lower() else ('Departure' if 'sundowner' in name.lower() else 'Any')
                intensity = 'Heavy' if any(k in name.lower() for k in ['trek','hiking','cycling','traverse']) else ('Light' if any(k in name.lower() for k in ['museum','photo','dinner','cuisine']) else 'Moderate')
                Activity.objects.update_or_create(
                    destination=dest, name=name,
                    defaults=dict(travel_type=tt, style=STYLE_MAP[style_code], interest=interest, time_slot=time_slot, day_suitability=day_fit, intensity=intensity, base_score=5 - (i // 3)),
                )
        self.stdout.write(self.style.SUCCESS('Seeded expanded destinations and activities.'))
