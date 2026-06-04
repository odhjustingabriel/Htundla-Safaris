from django.contrib.auth.models import User
from django.template.context import BaseContext
from django.test import TestCase
from django.urls import reverse

from .django_compat import patch_template_context_copy
from .models import Destination, Inquiry, Itinerary, ItineraryItem


class DjangoTemplateContextCompatibilityTests(TestCase):
    def test_patch_replaces_broken_base_context_copy(self):
        def broken_copy(context):
            raise AttributeError(
                "'super' object has no attribute 'dicts' and no __dict__ for setting new attributes"
            )

        BaseContext.__copy__ = broken_copy
        patch_template_context_copy()

        copied = BaseContext().__copy__()
        self.assertIsInstance(copied, BaseContext)


class InquiryAdminTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password12345',
        )
        self.destination = Destination.objects.create(name='Maasai Mara')
        self.inquiry = Inquiry.objects.create(
            full_name='Test Guest',
            email='guest@example.com',
            travel_type='Safari',
            destination=self.destination,
            duration_days=3,
            travel_style='Standard',
            group_size=2,
            interests=['Game Drive'],
        )
        self.itinerary = Itinerary.objects.create(
            inquiry=self.inquiry,
            summary='A short safari itinerary.',
        )
        ItineraryItem.objects.create(
            itinerary=self.itinerary,
            day_number=1,
            time_slot='Morning',
            title='Game drive',
            notes='Look for big cats.',
        )
        self.client.force_login(self.user)

    def test_regular_admin_change_form_renders(self):
        response = self.client.get(reverse('admin:core_inquiry_change', args=[self.inquiry.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Guest')
        self.assertContains(response, 'History')
        self.assertContains(response, 'Save')
