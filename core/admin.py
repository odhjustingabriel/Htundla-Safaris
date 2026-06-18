from django.contrib import admin
from django.core.mail import send_mail
from django.utils import timezone
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
    list_filter = ('travel_type','travel_style','status','destination')
    readonly_fields = ('created_at',)
    actions = [finalize_and_send]

@admin.register(OperatorResponse)
class OperatorResponseAdmin(admin.ModelAdmin):
    list_display = ('inquiry','operator','final_cost','finalized','sent_at')

admin.site.register(Destination)
admin.site.register(Activity)
admin.site.register(ItineraryItem)
admin.site.register(Operator)
