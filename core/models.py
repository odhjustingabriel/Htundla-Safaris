from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

class Destination(models.Model):
    name = models.CharField(max_length=100, unique=True)
    travel_type = models.CharField(max_length=10, choices=[('Safari','Safari'),('MICE','MICE')], default='Safari')
    def __str__(self): return self.name

class Activity(models.Model):
    TIME_SLOTS=[('Morning','Morning'),('Afternoon','Afternoon'),('Evening','Evening'),('Full-day','Full-day'),('Flexible','Flexible')]
    DAY_SUIT=[('Arrival','Arrival'),('Mid-trip','Mid-trip'),('Departure','Departure'),('Any','Any')]
    INTENSITY=[('Light','Light'),('Moderate','Moderate'),('Heavy','Heavy')]
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='activities')
    name = models.CharField(max_length=120)
    travel_type = models.CharField(max_length=10, choices=[('Safari','Safari'),('MICE','MICE')])
    style = models.CharField(max_length=20, choices=[('Budget-friendly','Budget-friendly'),('Standard','Standard'),('Luxury','Luxury')], default='Standard')
    interest = models.CharField(max_length=50)
    time_slot = models.CharField(max_length=20, choices=TIME_SLOTS, default='Flexible')
    day_suitability = models.CharField(max_length=20, choices=DAY_SUIT, default='Any')
    intensity = models.CharField(max_length=20, choices=INTENSITY, default='Moderate')
    base_score = models.IntegerField(default=1)

    class Meta:
        verbose_name_plural = 'Activities'

class Inquiry(models.Model):
    travel_type_choices=[('Safari','Safari'),('MICE','MICE')]
    style_choices=[('Budget-friendly','Budget-friendly'),('Standard','Standard'),('Luxury','Luxury')]
    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone_number = models.CharField(max_length=25, blank=True, validators=[RegexValidator(r'^$|^[0-9+\-\s()]{7,25}$','Invalid phone format')])
    travel_type = models.CharField(max_length=10, choices=travel_type_choices)
    destination = models.ForeignKey(Destination, on_delete=models.PROTECT)
    duration_days = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    travel_style = models.CharField(max_length=20, choices=style_choices)
    group_size = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    interests = models.JSONField(default=list)
    status = models.CharField(max_length=20, default='Draft Generated')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Inquiries'

class Itinerary(models.Model):
    inquiry = models.OneToOneField(Inquiry, on_delete=models.CASCADE, related_name='itinerary')
    summary = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Itineraries'

class ItineraryItem(models.Model):
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE, related_name='items')
    day_number = models.PositiveIntegerField()
    time_slot = models.CharField(max_length=20)
    title = models.CharField(max_length=200)
    notes = models.TextField(blank=True)

class Operator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    def __str__(self): return self.user.username

class OperatorResponse(models.Model):
    inquiry = models.OneToOneField(Inquiry, on_delete=models.CASCADE, related_name='operator_response')
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    final_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    proposal_notes = models.TextField(blank=True)
    finalized = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
