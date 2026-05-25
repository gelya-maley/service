from django.contrib import admin
from .models import (
    EmployeeProfile, ServiceType, Service, Client,
    DeviceType, SparePart, Order, OrderService, OrderSparePart,
    News, Term, Review, Vacancy, Promocode
)

class OrderServiceInline(admin.TabularInline):
    model = OrderService
    extra = 1

class OrderSparePartInline(admin.TabularInline):
    model = OrderSparePart
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'master', 'device', 'status', 'order_date', 'total_cost')
    list_filter = ('status', 'order_date', 'master')
    search_fields = ('client__full_name', 'client_problem')
    inlines = [OrderServiceInline, OrderSparePartInline]
    readonly_fields = ('order_date',)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'service_type', 'price', 'unit')
    list_filter = ('service_type',)
    search_fields = ('name',)

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'birth_date', 'age')
    search_fields = ('full_name', 'phone')
    list_filter = ('birth_date',)

@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'phone')
    search_fields = ('user__username', 'specialization')

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)
    list_filter = ('created_at',)

@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ('term', 'created_at')
    search_fields = ('term',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'rating', 'created_at', 'is_approved')
    list_filter = ('rating', 'is_approved', 'created_at')
    search_fields = ('author', 'text')

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'salary', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title',)

@admin.register(Promocode)
class PromocodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount', 'is_active', 'valid_from', 'valid_to', 'is_expired')
    list_filter = ('is_active', 'valid_from', 'valid_to')
    search_fields = ('code',)

admin.site.register(ServiceType)
admin.site.register(DeviceType)
admin.site.register(SparePart)