from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import Group, User
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .django_compat import ensure_local_sqlite_inquiry_schema
from .forms import InquiryForm, ProposalForm
from .models import Destination, Inquiry, OperatorResponse
from .recommender import generate_itinerary


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


@staff_member_required
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
        itinerary_text = '\n'.join([f"Day {i.day_number} {i.time_slot}: {i.title}" for i in inquiry.itinerary.items.all()]) if hasattr(inquiry, 'itinerary') else ''
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


@staff_member_required
def admin_dashboard(request):
    inquiries, filters = _filtered_inquiries(request)
    recent_users = User.objects.order_by('-date_joined')[:10] if request.user.is_superuser else []
    ctx = {
        'panel_title': 'Superuser Admin Panel' if request.user.is_superuser else 'Staff Admin Panel',
        'is_superuser_panel': request.user.is_superuser,
        'total_inquiries': Inquiry.objects.count(),
        'draft_count': Inquiry.objects.filter(status='Draft Generated').count(),
        'sent_count': Inquiry.objects.filter(status='Proposal Sent').count(),
        'total_users': User.objects.count(),
        'recent_users': recent_users,
        'inquiries': inquiries[:50],
        'destinations': Destination.objects.order_by('name'),
        'filters': filters,
    }
    return render(request, 'core/admin_dashboard.html', ctx)


@staff_member_required
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
    return render(request, 'core/operator_inquiry_review.html', {
        'inquiry': inquiry,
        'response': response,
        'proposal_form': form,
    })


@staff_member_required
def superuser_dashboard(request):
    if not request.user.is_superuser:
        messages.error(request, 'Only superusers can access the superuser admin panel.')
        return redirect('admin_dashboard')
    groups = Group.objects.order_by('name')
    ctx = {
        'staff_users': User.objects.filter(is_staff=True).order_by('username'),
        'groups': groups,
        'total_users': User.objects.count(),
        'total_staff': User.objects.filter(is_staff=True).count(),
        'total_superusers': User.objects.filter(is_superuser=True).count(),
    }
    return render(request, 'core/superuser_dashboard.html', ctx)
