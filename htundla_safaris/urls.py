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
    path('superuser/dashboard/', views.superuser_dashboard, name='superuser_dashboard'),
]
