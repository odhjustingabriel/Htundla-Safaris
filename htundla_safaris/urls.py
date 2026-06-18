from django.contrib import admin
from django.urls import path
from core import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('destinations/', views.destinations, name='destinations'),
    path('contactus/', views.contact_us, name='contactus'),
    path('proposal/send/<int:inquiry_id>/', views.send_proposal, name='send_proposal'),
    path('operator/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('operator/dashboard', views.admin_dashboard),
    path('operator/inquiries/<int:inquiry_id>/review/', views.operator_inquiry_review, name='operator_inquiry_review'),
    path('operator/inquiries/<int:inquiry_id>/itinerary/edit/', views.edit_itinerary, name='edit_itinerary'),
    path('superuser/dashboard/', views.superuser_dashboard, name='superuser_dashboard'),
    path('superuser/staff/create/', views.staff_user_create, name='staff_user_create'),
    path('superuser/staff/<int:user_id>/edit/', views.staff_user_edit, name='staff_user_edit'),
    path('superuser/roles/create/', views.staff_role_create, name='staff_role_create'),
    path('superuser/roles/<int:role_id>/edit/', views.staff_role_edit, name='staff_role_edit'),
]
