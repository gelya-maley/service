import json
import logging
import requests
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django import forms

import os
if os.environ.get('RENDER'):
    from django.contrib.auth.models import User
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('anagelina', 'maley.gelya@mail.ru', 'fyutkbyf')
        print("=" * 50)
        print("Суперпользователь создан!")
        print("Логин: admin")
        print("Пароль: admin123")
        print("=" * 50)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime

logger = logging.getLogger(__name__)

from .models import (
    Order, Service, EmployeeProfile, Client, 
    OrderService, ServiceType, DeviceType, SparePart,
    News, Term, Review, Vacancy, Promocode
)


def get_weather():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=53.9&longitude=27.5667&current_weather=true"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()['current_weather']['temperature']
    except Exception as e:
        logger.error(f"Weather API error: {e}")
    return "N/A"

def get_exchange_rate():
    try:
        url = "https://api.nbrb.by/exrates/rates/USD?parammode=2"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()['Cur_OfficialRate']
    except Exception as e:
        logger.error(f"Exchange rate API error: {e}")
    return "N/A"



def home(request):
    latest_service = Service.objects.order_by('-id').first()
    weather = get_weather()
    usd_rate = get_exchange_rate()
    logger.info(f"Home page viewed, weather: {weather}, USD: {usd_rate}")
    return render(request, 'core/home.html', {
        'latest_service': latest_service,
        'weather': weather,
        'usd_rate': usd_rate
    })

def service_list(request):
    """Список услуг с фильтрацией по цене и категории"""
    services = Service.objects.select_related('service_type').all()
    service_types = ServiceType.objects.all()
    
    category = request.GET.get('category', '')
    if category:
        services = services.filter(service_type__id=category)
    
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    if min_price:
        services = services.filter(price__gte=min_price)
    if max_price:
        services = services.filter(price__lte=max_price)
    
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'price_asc':
        services = services.order_by('price')
    elif sort_by == 'price_desc':
        services = services.order_by('-price')
    else:
        services = services.order_by('name')
    
    return render(request, 'core/service_list.html', {
        'services': services,
        'service_types': service_types,
        'selected_category': category,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
    })

def service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk)
    return render(request, 'core/service_detail.html', {'service': service})

def about(request):
    return render(request, 'core/about.html')

def contacts(request):
    employees = EmployeeProfile.objects.select_related('user').all()
    return render(request, 'core/contacts.html', {'employees': employees})

def privacy_policy(request):
    return render(request, 'core/privacy_policy.html')

def search_orders(request):
    query = request.GET.get('q')
    sort_by = request.GET.get('sort', '-order_date')
    orders = Order.objects.select_related('client', 'master').all()
    if query:
        orders = orders.filter(client__full_name__icontains=query)
    orders = orders.order_by(sort_by)
    return render(request, 'core/search.html', {'orders': orders, 'query': query})



def news_list(request):
    news_items = News.objects.all().order_by('-created_at')
    return render(request, 'core/news_list.html', {'news_items': news_items})

def news_detail(request, pk):
    news_item = get_object_or_404(News, pk=pk)
    return render(request, 'core/news_detail.html', {'news': news_item})



def terms_list(request):
    terms = Term.objects.all().order_by('term')
    return render(request, 'core/terms_list.html', {'terms': terms})


def vacancies(request):
    vacancies_list = Vacancy.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'core/vacancies.html', {'vacancies': vacancies_list})



def promocodes(request):
    from django.utils import timezone
    
    active_promocodes = Promocode.objects.filter(
        is_active=True, 
        valid_from__lte=timezone.now().date(),
        valid_to__gte=timezone.now().date()
    ).order_by('-discount')
    
    archived_promocodes = Promocode.objects.filter(
        is_active=False
    ) | Promocode.objects.filter(valid_to__lt=timezone.now().date())
    
    return render(request, 'core/promocodes.html', {
        'active_promocodes': active_promocodes,
        'archived_promocodes': archived_promocodes.distinct().order_by('-valid_to')
    })



def spare_parts_list(request):
    spare_parts = SparePart.objects.all()
    device_types = DeviceType.objects.all()
    
    device = request.GET.get('device', '')
    if device:
        spare_parts = spare_parts.filter(compatible_devices__id=device)
    
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    if min_price:
        spare_parts = spare_parts.filter(price__gte=min_price)
    if max_price:
        spare_parts = spare_parts.filter(price__lte=max_price)
    
    search = request.GET.get('search', '')
    if search:
        spare_parts = spare_parts.filter(name__icontains=search)
    
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'price_asc':
        spare_parts = spare_parts.order_by('price')
    elif sort_by == 'price_desc':
        spare_parts = spare_parts.order_by('-price')
    else:
        spare_parts = spare_parts.order_by('name')
    
    return render(request, 'core/spare_parts.html', {
        'spare_parts': spare_parts,
        'device_types': device_types,
        'selected_device': device,
        'min_price': min_price,
        'max_price': max_price,
        'search': search,
        'sort_by': sort_by,
    })


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'text': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Поделитесь впечатлениями о нашей работе...'}),
        }
    
    def clean_text(self):
        text = self.cleaned_data.get('text')
        if len(text) < 10:
            raise forms.ValidationError('Отзыв должен быть не менее 10 символов')
        if len(text) > 1000:
            raise forms.ValidationError('Отзыв не должен превышать 1000 символов')
        return text

def review_list(request):
    reviews = Review.objects.filter(is_approved=True).order_by('-created_at')
    return render(request, 'core/reviews.html', {'reviews': reviews})

def review_create(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            if hasattr(request.user, 'client_profile') and request.user.client_profile:
                review.author = request.user.client_profile.full_name
            elif request.user.is_authenticated:
                review.author = request.user.username
            else:
                review.author = "Аноним"
            review.save()
            return redirect('reviews')
    else:
        form = ReviewForm()
    return render(request, 'core/add_review.html', {'form': form})



class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['device', 'client_problem', 'status']
        widgets = {
            'client_problem': forms.Textarea(attrs={
                'rows': 4, 
                'class': 'form-control',
                'placeholder': 'Опишите подробно проблему...'
            }),
            'device': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_client_problem(self):
        problem = self.cleaned_data.get('client_problem')
        if len(problem) < 10:
            raise forms.ValidationError('Описание проблемы должно быть не менее 10 символов')
        if len(problem) > 500:
            raise forms.ValidationError('Описание проблемы не должно превышать 500 символов')
        return problem
    
    def save(self, commit=True):
        order = super().save(commit=False)
        if self.user and hasattr(self.user, 'client_profile'):
            order.client = self.user.client_profile
        if commit:
            order.save()
        return order

def order_list(request):
    orders = Order.objects.select_related('client', 'master', 'device').all().order_by('-order_date')
    return render(request, 'core/order_list.html', {'orders': orders})

@login_required
def order_detail_site(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'core/order_detail_site.html', {'order': order})

@login_required
def order_create(request):
    if not hasattr(request.user, 'client_profile'):
        return render(request, 'core/error.html', {'message': 'Только зарегистрированные клиенты могут создавать заказы'})
    
    if request.method == 'POST':
        form = OrderForm(request.POST, user=request.user)
        if form.is_valid():
            order = form.save()
            return redirect('order_detail_site', pk=order.pk)
    else:
        form = OrderForm(user=request.user)
    
    return render(request, 'core/order_form.html', {
        'form': form,
        'title': 'Создать новый заказ',
        'button_text': 'Оформить заказ'
    })

@login_required
def order_update(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    is_allowed = False
    if request.user.is_staff:
        is_allowed = True
    elif hasattr(request.user, 'employee_profile'):
        is_allowed = True
    elif hasattr(request.user, 'client_profile') and order.client == request.user.client_profile:
        is_allowed = True
    
    if not is_allowed:
        return render(request, 'core/error.html', {'message': 'У вас нет прав для редактирования этого заказа'})
    
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('order_detail_site', pk=order.pk)
    else:
        form = OrderForm(instance=order, user=request.user)
    
    return render(request, 'core/order_form.html', {
        'form': form,
        'title': 'Редактировать заказ',
        'button_text': 'Сохранить изменения'
    })

@login_required
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    is_allowed = False
    if request.user.is_staff:
        is_allowed = True
    elif hasattr(request.user, 'employee_profile'):
        is_allowed = True
    elif hasattr(request.user, 'client_profile') and order.client == request.user.client_profile:
        is_allowed = True
    
    if not is_allowed:
        return render(request, 'core/error.html', {'message': 'У вас нет прав для удаления этого заказа'})
    
    if request.method == 'POST':
        order.delete()
        return redirect('order_list')
    
    return render(request, 'core/order_confirm_delete.html', {'order': order})



@login_required
def master_schedule(request):
    if not hasattr(request.user, 'employee_profile'):
        return render(request, 'core/error.html', {'message': 'Доступ только для сотрудников'})
    
    master = request.user.employee_profile
    orders = Order.objects.filter(master=master).order_by('-order_date')
    
    total_orders = orders.count()
    completed_orders = orders.filter(status='completed').count()
    total_revenue = sum(o.total_cost() for o in orders)
    
    return render(request, 'core/master_schedule.html', {
        'orders': orders,
        'master': master,
        'total_orders': total_orders,
        'completed_orders': completed_orders,
        'total_revenue': total_revenue,
    })



@login_required
def cabinet(request):
    if hasattr(request.user, 'client_profile') and request.user.client_profile:
        orders = request.user.client_profile.orders.all()
        return render(request, 'core/client_cabinet.html', {'orders': orders})
    elif hasattr(request.user, 'employee_profile') and request.user.employee_profile:
        orders = request.user.employee_profile.orders.all()
        return render(request, 'core/master_cabinet.html', {'orders': orders})
    else:
        return render(request, 'core/cabinet.html')



def generate_statistics_chart():
    """Генерирует график количества заказов по месяцам с помощью matplotlib"""
    from collections import defaultdict
    from datetime import datetime
    
    all_orders = Order.objects.all()
    
    months_count = defaultdict(int)
    
    for order in all_orders:
        if order.order_date:
            month_key = order.order_date.strftime('%b %Y')  
            months_count[month_key] += 1
    
    sorted_months = sorted(months_count.keys(), key=lambda x: datetime.strptime(x, '%b %Y'))
    counts = [months_count[m] for m in sorted_months]
    
    if not sorted_months:
        sorted_months = ['Нет данных']
        counts = [0]
    
    plt.figure(figsize=(10, 5))
    
    if len(sorted_months) > 1 and max(counts) > 0:
        plt.plot(sorted_months, counts, marker='o', linestyle='-', color='royalblue', linewidth=2, markersize=8)
        plt.title('Динамика количества заказов по месяцам', fontsize=14, fontweight='bold')
        plt.xlabel('Месяц', fontsize=12)
        plt.ylabel('Количество заказов', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.xticks(rotation=45, ha='right')
    else:
        plt.bar(sorted_months, counts, color='royalblue')
        plt.title('Количество заказов', fontsize=14, fontweight='bold')
        plt.xlabel('Месяц', fontsize=12)
        plt.ylabel('Количество заказов', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=100)
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    return image_base64


def statistics(request):
    all_orders = Order.objects.all()
    total_orders = all_orders.count()
    
    print(f"DEBUG: Всего заказов в БД: {total_orders}")
    
    for order in all_orders:
        print(f"DEBUG: Заказ #{order.id}, дата: {order.order_date}, статус: {order.status}")
    
    total_sum = sum(o.total_cost() for o in all_orders)
    avg_cost = total_sum / total_orders if total_orders > 0 else 0
    
    costs_list = sorted([float(o.total_cost()) for o in all_orders])
    if costs_list:
        n = len(costs_list)
        if n % 2 == 0:
            median_cost = (costs_list[n//2 - 1] + costs_list[n//2]) / 2
        else:
            median_cost = costs_list[n//2]
    else:
        median_cost = 0
    
    popular_service = OrderService.objects.values('service__name').annotate(
        total=Sum('quantity')
    ).order_by('-total').first()
    
    profitable_service = OrderService.objects.values('service__name', 'service__price').annotate(
        total_quantity=Sum('quantity')
    ).order_by('-total_quantity')
    
    if profitable_service:
        for item in profitable_service:
            item['total_revenue'] = float(item['service__price']) * item['total_quantity']
        most_profitable = max(profitable_service, key=lambda x: x['total_revenue'])
        most_profitable_name = most_profitable['service__name']
        most_profitable_revenue = most_profitable['total_revenue']
    else:
        most_profitable_name = "Нет данных"
        most_profitable_revenue = 0
    
    chart_base64 = generate_statistics_chart()
    services_alpha = Service.objects.select_related('service_type').all().order_by('name')
    
    context = {
        'total_orders': total_orders,
        'avg_cost': round(avg_cost, 2),
        'median_cost': round(median_cost, 2),
        'popular_service': popular_service['service__name'] if popular_service else "Нет данных",
        'most_profitable_name': most_profitable_name,
        'most_profitable_revenue': round(most_profitable_revenue, 2),
        'chart_base64': chart_base64,
        'services_alpha': services_alpha,
    }
    return render(request, 'core/statistics.html', context)


@login_required
def api_weather(request):
    weather = get_weather()
    return JsonResponse({
        'temperature': weather,
        'unit': 'celsius',
        'status': 'success'
    })

@login_required
def api_exchange(request):
    rate = get_exchange_rate()
    return JsonResponse({
        'usd_rate': rate,
        'currency': 'USD',
        'status': 'success'
    })
