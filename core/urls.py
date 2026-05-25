from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('services/', views.service_list, name='service_list'),
    path('services/<int:pk>/', views.service_detail, name='service_detail'),
    path('about/', views.about, name='about'),
    path('contacts/', views.contacts, name='contacts'),
    path('vacancies/', views.vacancies, name='vacancies'),
    path('reviews/', views.review_list, name='reviews'),
    path('reviews/', views.review_list, name='review_list'),
    path('reviews/add/', views.review_create, name='add_review'),
    path('promocodes/', views.promocodes, name='promocodes'),
    path('statistics/', views.statistics, name='statistics'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    
    path('news/', views.news_list, name='news_list'),
    path('news/<int:pk>/', views.news_detail, name='news_detail'),
    
    path('terms/', views.terms_list, name='terms_list'),
    
    path('spare-parts/', views.spare_parts_list, name='spare_parts'),
    
    path('master/schedule/', views.master_schedule, name='master_schedule'),
    
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:pk>/', views.order_detail_site, name='order_detail_site'),
    path('orders/create/', views.order_create, name='order_create'),
    path('orders/<int:pk>/edit/', views.order_update, name='order_update'),
    path('orders/<int:pk>/delete/', views.order_delete, name='order_delete'),
    
    re_path(r'^order/(?P<order_id>\d+)/$', views.order_detail_site, name='order_detail'),
    
    path('search/', views.search_orders, name='search_orders'),
    path('cabinet/', views.cabinet, name='cabinet'),
    
    # API endpoints
    path('api/weather/', views.api_weather, name='api_weather'),
    path('api/exchange/', views.api_exchange, name='api_exchange'),
]