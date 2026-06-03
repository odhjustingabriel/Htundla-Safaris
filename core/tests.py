from decimal import Decimal
from unittest.mock import patch

from django.contrib import admin
from django.contrib.auth.models import User
from django.template.context import BaseContext
from django.test import RequestFactory, TestCase
from django.urls import reverse

from .models import Destination, Inquiry, Itinerary, ItineraryItem, OperatorResponse


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

    def test_change_page_renders_generated_itinerary_without_admin_inclusion_tags(self):
        response = self.client.get(reverse('admin:core_inquiry_change', args=[self.inquiry.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Guest')
        self.assertContains(response, 'Generated itinerary')
        self.assertContains(response, 'Game drive')
        self.assertContains(response, 'Finalize and send proposal')

    def test_change_page_still_renders_if_template_context_copy_is_broken(self):
        def broken_copy(context):
            raise AttributeError(
                "'super' object has no attribute 'dicts' and no __dict__ for setting new attributes"
            )

        request = RequestFactory().get(reverse('admin:core_inquiry_change', args=[self.inquiry.pk]))
        request.user = self.user
        inquiry_admin = admin.site._registry[Inquiry]

        with patch.object(BaseContext, '__copy__', broken_copy):
            response = inquiry_admin.change_view(request, str(self.inquiry.pk))

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Game drive', response.content)

    def test_change_page_can_save_proposal_details(self):
        response = self.client.post(
            reverse('admin:core_inquiry_change', args=[self.inquiry.pk]),
            {'final_cost': '1200.00', 'proposal_notes': 'Approved plan.', 'save_proposal': '1'},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        operator_response = OperatorResponse.objects.get(inquiry=self.inquiry)
        self.assertEqual(operator_response.final_cost, Decimal('1200.00'))
        self.assertEqual(operator_response.proposal_notes, 'Approved plan.')
        self.assertFalse(operator_response.finalized)
