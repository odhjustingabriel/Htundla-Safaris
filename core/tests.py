from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Destination, Inquiry


class InquiryAdminTests(TestCase):
    def test_change_form_renders_without_object_tools_context_copy_error(self):
        user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password12345',
        )
        destination = Destination.objects.create(name='Maasai Mara')
        inquiry = Inquiry.objects.create(
            full_name='Test Guest',
            email='guest@example.com',
            travel_type='Safari',
            destination=destination,
            duration_days=3,
            travel_style='Standard',
            group_size=2,
            interests=['Game Drive'],
        )

        self.client.force_login(user)
        response = self.client.get(reverse('admin:core_inquiry_change', args=[inquiry.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Guest')
        self.assertContains(response, 'History')
