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


class StaffAdminPanelPageTests(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username='superadmin',
            email='superadmin@example.com',
            password='password12345',
        )
        self.staff_user = User.objects.create_user(
            username='operator',
            email='operator@example.com',
            password='password12345',
            is_staff=True,
        )
        self.portal_user = User.objects.create_user(
            username='portaluser',
            email='portal@example.com',
            password='password12345',
        )
        self.destination = Destination.objects.create(name='Serengeti')
        self.inquiry = Inquiry.objects.create(
            full_name='Panel Guest',
            email='panel@example.com',
            travel_type='Safari',
            destination=self.destination,
            duration_days=4,
            travel_style='Luxury',
            group_size=2,
            interests=['Photography'],
        )

    def test_operator_dashboard_renders_for_staff_user(self):
        self.client.force_login(self.staff_user)

        response = self.client.get(reverse('admin_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Staff Admin Panel')
        self.assertContains(response, 'Panel Guest')
        self.assertContains(response, 'Filter Records')

    def test_staff_user_create_page_renders_with_matched_actions(self):
        self.client.force_login(self.superuser)

        response = self.client.get(reverse('staff_user_create'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Staff User')
        self.assertContains(response, 'button primary')
        self.assertContains(response, 'button secondary')
        self.assertContains(response, 'Account Status')

    def test_staff_role_create_page_renders_spaced_permission_grid(self):
        self.client.force_login(self.superuser)

        response = self.client.get(reverse('staff_role_create'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Staff Role')
        self.assertContains(response, 'permissions-panel')
        self.assertContains(response, 'Select only the permissions this role needs')

    def test_staff_dashboard_redirects_anonymous_users_to_staff_login(self):
        response = self.client.get(reverse('admin_dashboard'))

        self.assertRedirects(response, f"{reverse('staff_login')}?next={reverse('admin_dashboard')}")

    def test_superuser_can_access_staff_dashboard(self):
        self.client.force_login(self.superuser)

        response = self.client.get(reverse('admin_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Staff Admin Panel')

    def test_superuser_dashboard_redirects_anonymous_users_to_superuser_login(self):
        response = self.client.get(reverse('superuser_dashboard'))

        self.assertRedirects(response, f"{reverse('superuser_login')}?next={reverse('superuser_dashboard')}")

    def test_staff_user_cannot_log_in_to_superuser_dashboard(self):
        response = self.client.post(reverse('superuser_login'), {
            'username': 'operator',
            'password': 'password12345',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This account is not allowed to access the Superuser Admin Panel')

    def test_staff_login_accepts_staff_credentials(self):
        response = self.client.post(reverse('staff_login'), {
            'username': 'operator',
            'password': 'password12345',
        })

        self.assertRedirects(response, reverse('admin_dashboard'))

    def test_staff_login_accepts_authenticated_portal_user_without_403(self):
        response = self.client.post(reverse('staff_login'), {
            'username': 'portaluser',
            'password': 'password12345',
        })

        self.assertRedirects(response, reverse('admin_dashboard'))
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_superuser_login_accepts_superuser_credentials(self):
        response = self.client.post(reverse('superuser_login'), {
            'username': 'superadmin',
            'password': 'password12345',
        })

        self.assertRedirects(response, reverse('superuser_dashboard'))

    def test_review_orders_itinerary_slots_chronologically(self):
        itinerary = Itinerary.objects.create(
            inquiry=self.inquiry,
            summary='Out-of-order source items.',
        )
        ItineraryItem.objects.create(
            itinerary=itinerary,
            day_number=1,
            time_slot='Evening',
            title='Dinner under the stars',
            notes='Close the day.',
        )
        ItineraryItem.objects.create(
            itinerary=itinerary,
            day_number=1,
            time_slot='Morning',
            title='Sunrise game drive',
            notes='Start early.',
        )
        ItineraryItem.objects.create(
            itinerary=itinerary,
            day_number=1,
            time_slot='Afternoon',
            title='Bush lunch',
            notes='Relax after lunch.',
        )
        self.client.force_login(self.staff_user)

        response = self.client.get(reverse('operator_inquiry_review', args=[self.inquiry.pk]))
        content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertLess(content.index('Sunrise game drive'), content.index('Bush lunch'))
        self.assertLess(content.index('Bush lunch'), content.index('Dinner under the stars'))
