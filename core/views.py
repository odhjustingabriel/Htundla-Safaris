from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from .forms import InquiryForm, ProposalForm
from .models import Destination, Inquiry, OperatorResponse
from .recommender import generate_itinerary

def index(request):
    return render(request, 'core/index.html')

def destinations(request):
    return render(request, 'core/destinations.html', {'destinations': Destination.objects.all()})

def contact_us(request):
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
        response.finalized = True
        response.sent_at = timezone.now()
        response.operator = request.user if request.user.is_authenticated else None
        proposal_form = ProposalForm(request.POST)
        if not proposal_form.is_valid():
            messages.error(request, 'Invalid proposal payload.')
            return HttpResponseRedirect(reverse('admin:core_inquiry_change', args=[inquiry.id]))
        response.final_cost = proposal_form.cleaned_data.get('final_cost') or response.final_cost
        response.proposal_notes = proposal_form.cleaned_data.get('proposal_notes','')
        response.save()
        itinerary_text = '\n'.join([f"Day {i.day_number} {i.time_slot}: {i.title}" for i in inquiry.itinerary.items.all()]) if hasattr(inquiry,'itinerary') else ''
        send_mail('Your Htundla Proposal', f'Hello {inquiry.full_name},\n\n{response.proposal_notes}\nFinal cost: {response.final_cost}\n\n{itinerary_text}', None, [inquiry.email])
        inquiry.status = 'Proposal Sent'; inquiry.save(update_fields=['status'])
        return HttpResponseRedirect(reverse('admin:core_inquiry_change', args=[inquiry.id]))
    return redirect('admin:core_inquiry_change', inquiry.id)


@staff_member_required
def admin_dashboard(request):
    inquiries = Inquiry.objects.select_related('destination').prefetch_related('itinerary__items').order_by('-created_at')[:25]
    recent_users = User.objects.order_by('-date_joined')[:10]
    ctx = {
        'total_inquiries': Inquiry.objects.count(),
        'draft_count': Inquiry.objects.filter(status='Draft Generated').count(),
        'sent_count': Inquiry.objects.filter(status='Proposal Sent').count(),
        'total_users': User.objects.count(),
        'recent_users': recent_users,
        'inquiries': inquiries,
    }
    return render(request, 'core/admin_dashboard.html', ctx)
