from django.urls import path
from . import views
from .views import logout_view

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', views.register, name='register'),

    path('ads/', views.ad_list, name='ad_list'),
    path('ads/<int:pk>/', views.ad_detail, name='ad_detail'),
    path('ads/new/', views.ad_create, name='ad_create'),
    path('ads/<int:pk>/edit/', views.ad_update, name='ad_update'),
    path('ads/<int:pk>/delete/', views.ad_delete, name='ad_delete'),

    path('ads/<int:ad_id>/propose-exchange/', views.create_exchange_proposal, name='propose_exchange'),
    path('my-proposals/', views.my_proposals, name='my_proposals'),
    path('proposals/<int:proposal_id>/update-status/', views.update_proposal_status, name='update_proposal_status'),
]