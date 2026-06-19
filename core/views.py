from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group, User
from django.core.mail import send_mail
from django.db.models import Case, IntegerField, Q, Value, When
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils import timezone
from .django_compat import ensure_local_sqlite_inquiry_schema
from .forms import InquiryForm, ItineraryItemFormSet, ProposalForm, StaffRoleForm, StaffUserForm
from .models import Destination, Inquiry, ItineraryItem, OperatorResponse
from .recommender import generate_itinerary


SLOT_ORDER = Case(
    When(time_slot='Morning', then=Value(1)),
    When(time_slot='Afternoon', then=Value(2)),
    When(time_slot='Evening', then=Value(3)),
    default=Value(4),
    output_field=IntegerField(),
)


def _chronological_items(queryset):
    return queryset.alias(slot_order=SLOT_ORDER).order_by('day_number', 'slot_order', 'id')


def _is_staff_portal_user(user):
    return user.is_authenticated and user.is_staff


def _is_superuser(user):
    return user.is_authenticated and user.is_superuser


def _portal_login(request, *, portal_name, required_check, redirect_name, template_name):
    if required_check(request.user):
        return redirect(redirect_name)

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        if required_check(user):
            login(request, user)
            next_url = request.GET.get('next')
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect(redirect_name)
        form.add_error(None, f'This account is not allowed to access the {portal_name}.')

    return render(request, template_name, {'form': form, 'portal_name': portal_name})


def staff_login(request):
    return _portal_login(
        request,
        portal_name='Staff Portal',
        required_check=lambda user: user.is_authenticated and user.is_staff,
        redirect_name='admin_dashboard',
        template_name='core/portal_login.html',
    )


def superuser_login(request):
    return _portal_login(
        request,
        portal_name='Superuser Admin Panel',
        required_check=lambda user: user.is_authenticated and user.is_superuser,
        redirect_name='superuser_dashboard',
        template_name='core/portal_login.html',
    )


def index(request):
    return render(request, 'core/index.html')


def destinations(request):
    return render(request, 'core/destinations.html', {'destinations': Destination.objects.all()})


def contact_us(request):
    ensure_local_sqlite_inquiry_schema()
    if request.method == 'POST':
        form = InquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save()
            generate_itinerary(inquiry)
            messages.success(request, 'Inquiry submitted. Draft itinerary generated.')
            return redirect('contactus')
    else:
        form = InquiryForm()
    return render(request, 'core/contactus.html', {'form': form})


@user_passes_test(_is_staff_portal_user, login_url='staff_login')
def send_proposal(request, inquiry_id):
    inquiry = get_object_or_404(Inquiry, id=inquiry_id)
    response, _ = OperatorResponse.objects.get_or_create(inquiry=inquiry)
    if request.method == 'POST':
        proposal_form = ProposalForm(request.POST)
        if not proposal_form.is_valid():
            messages.error(request, 'Invalid proposal payload.')
            return redirect('operator_inquiry_review', inquiry_id=inquiry.id)
        response.finalized = True
        response.sent_at = timezone.now()
        response.operator = request.user if request.user.is_authenticated else None
        response.final_cost = proposal_form.cleaned_data.get('final_cost') or response.final_cost
        response.proposal_notes = proposal_form.cleaned_data.get('proposal_notes', '')
        response.save()
        itinerary_text = '\n'.join([f"Day {i.day_number} {i.time_slot}: {i.title}" for i in _chronological_items(inquiry.itinerary.items.all())]) if hasattr(inquiry, 'itinerary') else ''
        send_mail('Your Htundla Proposal', f'Hello {inquiry.full_name},\n\n{response.proposal_notes}\nFinal cost: {response.final_cost}\n\n{itinerary_text}', None, [inquiry.email])
        inquiry.status = 'Proposal Sent'
        inquiry.save(update_fields=['status'])
        messages.success(request, 'Proposal finalized and sent to the customer.')
        return redirect('operator_inquiry_review', inquiry_id=inquiry.id)
    return redirect('operator_inquiry_review', inquiry_id=inquiry.id)


def _filtered_inquiries(request):
    ensure_local_sqlite_inquiry_schema()
    inquiries = Inquiry.objects.select_related('destination').prefetch_related('itinerary__items').order_by('-created_at')
    status = request.GET.get('status', '').strip()
    travel_type = request.GET.get('travel_type', '').strip()
    destination_id = request.GET.get('destination', '').strip()
    search = request.GET.get('q', '').strip()

    if status:
        inquiries = inquiries.filter(status=status)
    if travel_type:
        inquiries = inquiries.filter(travel_type=travel_type)
    if destination_id:
        inquiries = inquiries.filter(destination_id=destination_id)
    if search:
        inquiries = inquiries.filter(Q(full_name__icontains=search) | Q(email__icontains=search))

    return inquiries, {
        'status': status,
        'travel_type': travel_type,
        'destination': destination_id,
        'q': search,
    }


@user_passes_test(_is_staff_portal_user, login_url='staff_login')
def admin_dashboard(request):
    inquiries, filters = _filtered_inquiries(request)
    ctx = {
        'panel_title': 'Staff Admin Panel',
        'total_inquiries': Inquiry.objects.count(),
        'draft_count': Inquiry.objects.filter(status='Draft Generated').count(),
        'sent_count': Inquiry.objects.filter(status='Proposal Sent').count(),
        'total_users': User.objects.count(),
        'inquiries': inquiries[:50],
        'destinations': Destination.objects.order_by('name'),
        'filters': filters,
    }
    return render(request, 'core/admin_dashboard.html', ctx)


@user_passes_test(_is_staff_portal_user, login_url='staff_login')
def operator_inquiry_review(request, inquiry_id):
    ensure_local_sqlite_inquiry_schema()
    inquiry = get_object_or_404(
        Inquiry.objects.select_related('destination').prefetch_related('itinerary__items'),
        id=inquiry_id,
    )
    response, _ = OperatorResponse.objects.get_or_create(inquiry=inquiry)
    form = ProposalForm(initial={
        'final_cost': response.final_cost,
        'proposal_notes': response.proposal_notes,
    })
    items_by_day = {}
    if hasattr(inquiry, 'itinerary'):
        for item in _chronological_items(inquiry.itinerary.items.all()):
            items_by_day.setdefault(item.day_number, []).append(item)
    return render(request, 'core/operator_inquiry_review.html', {
        'inquiry': inquiry,
        'response': response,
        'proposal_form': form,
        'items_by_day': items_by_day,
    })


@user_passes_test(_is_staff_portal_user, login_url='staff_login')
def edit_itinerary(request, inquiry_id):
    ensure_local_sqlite_inquiry_schema()
    inquiry = get_object_or_404(Inquiry.objects.select_related('destination'), id=inquiry_id)
    if not hasattr(inquiry, 'itinerary'):
        generate_itinerary(inquiry)
    queryset = _chronological_items(ItineraryItem.objects.filter(itinerary=inquiry.itinerary))
    formset = ItineraryItemFormSet(request.POST or None, queryset=queryset)
    if request.method == 'POST' and formset.is_valid():
        formset.save()
        messages.success(request, 'Draft itinerary updated successfully.')
        return redirect('operator_inquiry_review', inquiry_id=inquiry.id)
    return render(request, 'core/edit_itinerary.html', {
        'inquiry': inquiry,
        'formset': formset,
    })


@user_passes_test(_is_superuser, login_url='superuser_login')
def staff_role_create(request):
    form = StaffRoleForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        role = form.save()
        messages.success(request, f'Role "{role.name}" created successfully.')
        return redirect('superuser_dashboard')
    return render(request, 'core/staff_role_form.html', {'form': form, 'title': 'Create Staff Role'})


@user_passes_test(_is_superuser, login_url='superuser_login')
def staff_role_edit(request, role_id):
    role = get_object_or_404(Group, id=role_id)
    form = StaffRoleForm(request.POST or None, instance=role)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Role "{role.name}" updated successfully.')
        return redirect('superuser_dashboard')
    return render(request, 'core/staff_role_form.html', {'form': form, 'title': f'Edit Staff Role: {role.name}'})


@user_passes_test(_is_superuser, login_url='superuser_login')
def staff_user_create(request):
    form = StaffUserForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        messages.success(request, f'Staff user "{user.username}" created successfully.')
        return redirect('superuser_dashboard')
    return render(request, 'core/staff_user_form.html', {'form': form, 'title': 'Create Staff User'})


@user_passes_test(_is_superuser, login_url='superuser_login')
def staff_user_edit(request, user_id):
    staff_user = get_object_or_404(User, id=user_id)
    form = StaffUserForm(request.POST or None, instance=staff_user)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        messages.success(request, f'Staff user "{user.username}" updated successfully.')
        return redirect('superuser_dashboard')
    return render(request, 'core/staff_user_form.html', {'form': form, 'title': f'Edit Staff User: {staff_user.username}'})


@user_passes_test(_is_superuser, login_url='superuser_login')
def superuser_dashboard(request):
    groups = Group.objects.order_by('name')
    ctx = {
        'staff_users': User.objects.filter(is_staff=True).order_by('username'),
        'groups': groups,
        'total_users': User.objects.count(),
        'total_staff': User.objects.filter(is_staff=True).count(),
        'total_superusers': User.objects.filter(is_superuser=True).count(),
    }
    return render(request, 'core/superuser_dashboard.html', ctx)
