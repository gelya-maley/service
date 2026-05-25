from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils import timezone
import datetime

phone_regex = RegexValidator(
    regex=r'^\+375 \(\d{2}\) \d{3}-\d{2}-\d{2}$',
    message="Телефон должен быть в формате: +375 (29) 123-45-67"
)

class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    phone = models.CharField(max_length=20, validators=[phone_regex])
    specialization = models.CharField(max_length=100, verbose_name="Специализация")
    hire_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.specialization}"

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"


class ServiceType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=200)
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE, related_name='services')
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    unit = models.CharField(max_length=20, default="шт.", help_text="шт., час, услуга")
    image = models.ImageField(upload_to='services/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.price} руб.)"


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile', null=True, blank=True)
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, validators=[phone_regex])
    address = models.TextField()
    passport_data = models.CharField(max_length=100, blank=True, verbose_name="Паспортные данные")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Дата рождения")

    def age(self):
        if not self.birth_date:
            return 18
        today = timezone.now().date()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))

    def save(self, *args, **kwargs):
        if self.birth_date and self.age() < 18:
            raise ValueError("Клиент должен быть старше 18 лет")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name


class DeviceType(models.Model):
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.brand} {self.name}".strip()


class SparePart(models.Model):
    name = models.CharField(max_length=200)
    compatible_devices = models.ManyToManyField(DeviceType, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_quantity = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'В ожидании'),
        ('in_progress', 'В работе'),
        ('completed', 'Выполнен'),
        ('cancelled', 'Отменен'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='orders')
    master = models.ForeignKey(EmployeeProfile, on_delete=models.SET_NULL, null=True, related_name='orders')
    device = models.ForeignKey(DeviceType, on_delete=models.SET_NULL, null=True)
    services = models.ManyToManyField(Service, through='OrderService', related_name='orders')
    spare_parts = models.ManyToManyField(SparePart, through='OrderSparePart', blank=True)
    
    order_date = models.DateTimeField(auto_now_add=True)
    completion_date = models.DateField(null=True, blank=True)
    completion_deadline = models.DateField(null=True, blank=True, verbose_name="Срок выполнения")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    client_problem = models.TextField(verbose_name="Описание проблемы")
    
    contract_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="Номер договора")
    contract_date = models.DateField(null=True, blank=True, verbose_name="Дата договора")

    def total_cost(self):
        services_cost = sum(item.service.price * item.quantity for item in self.orderservice_set.all())
        parts_cost = sum(item.spare_part.price * item.quantity for item in self.ordersparepart_set.all())
        return services_cost + parts_cost

    def __str__(self):
        contract = f" (договор {self.contract_number})" if self.contract_number else ""
        return f"Заказ #{self.id} - {self.client.full_name}{contract}"


class OrderService(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


class OrderSparePart(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    spare_part = models.ForeignKey(SparePart, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


class News(models.Model):
    """Модель новостей"""
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    short_description = models.CharField(max_length=300, verbose_name="Краткое описание")
    content = models.TextField(verbose_name="Полное содержание")
    image = models.ImageField(upload_to='news/', blank=True, null=True, verbose_name="Изображение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ['-created_at']


class Term(models.Model):
    """Модель словаря терминов"""
    term = models.CharField(max_length=100, verbose_name="Термин")
    definition = models.TextField(verbose_name="Определение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    
    def __str__(self):
        return self.term
    
    class Meta:
        verbose_name = "Термин"
        verbose_name_plural = "Словарь терминов"
        ordering = ['term']


class Review(models.Model):
    """Модель отзывов"""
    RATING_CHOICES = [
        (1, '★☆☆☆☆'),
        (2, '★★☆☆☆'),
        (3, '★★★☆☆'),
        (4, '★★★★☆'),
        (5, '★★★★★'),
    ]
    
    author = models.CharField(max_length=100, verbose_name="Автор")
    rating = models.IntegerField(choices=RATING_CHOICES, verbose_name="Оценка")
    text = models.TextField(verbose_name="Текст отзыва")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_approved = models.BooleanField(default=True, verbose_name="Одобрен")
    
    def __str__(self):
        return f"{self.author} - {self.rating}★"
    
    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-created_at']

class Vacancy(models.Model):
    """Модель вакансий"""
    title = models.CharField(max_length=200, verbose_name="Должность")
    description = models.TextField(verbose_name="Описание")
    salary = models.CharField(max_length=100, blank=True, verbose_name="Зарплата")
    requirements = models.TextField(verbose_name="Требования", blank=True)
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"
        ordering = ['-created_at']


class Promocode(models.Model):
    """Модель промокодов и купонов"""
    code = models.CharField(max_length=50, unique=True, verbose_name="Код")
    discount = models.IntegerField(verbose_name="Скидка (%)", validators=[MinValueValidator(0), MaxValueValidator(100)])
    description = models.CharField(max_length=200, blank=True, verbose_name="Описание")
    is_active = models.BooleanField(default=True, verbose_name="Действует")
    valid_from = models.DateField(verbose_name="Действует с")
    valid_to = models.DateField(verbose_name="Действует до")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    def is_expired(self):
        """Проверка, истек ли срок действия"""
        from django.utils import timezone
        return self.valid_to < timezone.now().date()
    
    def __str__(self):
        status = "✓" if self.is_active and not self.is_expired() else "✗"
        return f"{status} {self.code} - {self.discount}%"
    
    class Meta:
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды и купоны"
        ordering = ['-is_active', '-valid_to']