from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import ProposalForm
from .models import Activity, Destination, Inquiry, Itinerary, ItineraryItem, Operator, OperatorResponse

class ItineraryItemInline(admin.TabularInline):
    model = ItineraryItem
    extra = 0

@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):
    inlines=[ItineraryItemInline]

@admin.action(description='Mark finalized and send proposals by email')
def finalize_and_send(modeladmin, request, queryset):
    for inquiry in queryset:
        response, _ = OperatorResponse.objects.get_or_create(inquiry=inquiry)
        response.finalized = True
        response.sent_at = timezone.now()
        response.operator = request.user
        response.save()
        send_mail('Your Htundla Proposal', f'Hello {inquiry.full_name}, your proposal is ready. Notes: {response.proposal_notes}. Final cost: {response.final_cost}', None, [inquiry.email])
        inquiry.status = 'Proposal Sent'; inquiry.save(update_fields=['status'])

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    change_form_template = 'admin/core/inquiry/change_form.html'
    list_display = ('full_name','email','travel_type','destination','duration_days','status','created_at')
    list_filter = ('travel_type','travel_style','status')
    readonly_fields = ('created_at',)
    actions = [finalize_and_send]

    def change_view(self, request, object_id, form_url='', extra_context=None):
        inquiry = self.get_object(request, object_id)
        if inquiry is None:
            return redirect(reverse('admin:core_inquiry_changelist'))
        if not self.has_view_or_change_permission(request, inquiry):
            raise PermissionDenied

        response, _ = OperatorResponse.objects.get_or_create(inquiry=inquiry)

        if request.method == 'POST':
            proposal_form = ProposalForm(request.POST)
            if proposal_form.is_valid():
                response.final_cost = proposal_form.cleaned_data.get('final_cost') or response.final_cost
                response.proposal_notes = proposal_form.cleaned_data.get('proposal_notes', '')
                response.operator = request.user if request.user.is_authenticated else None

                if 'send_proposal' in request.POST:
                    response.finalized = True
                    response.sent_at = timezone.now()
                    response.save()
                    itinerary_text = self._format_itinerary_for_email(inquiry)
                    send_mail(
                        'Your Htundla Proposal',
                        f'Hello {inquiry.full_name},\n\n{response.proposal_notes}\nFinal cost: {response.final_cost}\n\n{itinerary_text}',
                        None,
                        [inquiry.email],
                    )
                    inquiry.status = 'Proposal Sent'
                    inquiry.save(update_fields=['status'])
                    messages.success(request, 'Proposal finalized and sent.')
                else:
                    response.save()
                    messages.success(request, 'Proposal details saved.')

                return redirect(reverse('admin:core_inquiry_change', args=[inquiry.pk]))

            messages.error(request, 'Please correct the proposal details below.')
        else:
            proposal_form = ProposalForm(initial={
                'final_cost': response.final_cost,
                'proposal_notes': response.proposal_notes,
            })

        context = {
            **self.admin_site.each_context(request),
            'title': f'Review inquiry: {inquiry.full_name}',
            'opts': self.model._meta,
            'original': inquiry,
            'inquiry': inquiry,
            'itinerary': getattr(inquiry, 'itinerary', None),
            'operator_response': response,
            'proposal_form': proposal_form,
            'changelist_url': reverse('admin:core_inquiry_changelist'),
            'history_url': reverse('admin:core_inquiry_history', args=[inquiry.pk]),
        }
        if extra_context:
            context.update(extra_context)
        return render(request, 'admin/core/inquiry/review.html', context)

    def _format_itinerary_for_email(self, inquiry):
        if not hasattr(inquiry, 'itinerary'):
            return ''
        return '\n'.join(
            f'Day {item.day_number} {item.time_slot}: {item.title}'
            for item in inquiry.itinerary.items.order_by('day_number', 'id')
        )

@admin.register(OperatorResponse)
class OperatorResponseAdmin(admin.ModelAdmin):
    list_display = ('inquiry','operator','final_cost','finalized','sent_at')

admin.site.register(Destination)
admin.site.register(Activity)
admin.site.register(ItineraryItem)
admin.site.register(Operator)
