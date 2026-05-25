from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date

# Переименуем импорт модели Client, чтобы не конфликтовать
from .models import Client as ClientModel
from .models import (
    EmployeeProfile, ServiceType, Service, 
    DeviceType, SparePart, Order, OrderService
)


class ClientModelTest(TestCase):
    """Тесты модели Client"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
    
    def test_client_creation_with_valid_age(self):
        """Создание клиента с возрастом 18+"""
        client = ClientModel.objects.create(
            user=self.user,
            full_name='Test Client',
            phone='+375 (29) 123-45-67',
            address='Test Address',
            birth_date=date(1990, 1, 1)
        )
        self.assertEqual(client.full_name, 'Test Client')
        self.assertGreaterEqual(client.age(), 18)
    
    def test_client_age_calculation(self):
        """Проверка вычисления возраста"""
        client = ClientModel(
            user=self.user,
            full_name='Test Client',
            phone='+375 (29) 123-45-67',
            address='Test Address',
            birth_date=date(2000, 5, 15)
        )
        self.assertGreaterEqual(client.age(), 18)
    
    def test_client_str_method(self):
        client = ClientModel.objects.create(
            user=self.user,
            full_name='Ivan Petrov',
            phone='+375 (29) 123-45-67',
            address='Test Address',
            birth_date=date(1990, 1, 1)
        )
        self.assertEqual(str(client), 'Ivan Petrov')


class EmployeeProfileModelTest(TestCase):
    """Тесты модели EmployeeProfile"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='employee', password='12345')
    
    def test_employee_creation(self):
        employee = EmployeeProfile.objects.create(
            user=self.user,
            phone='+375 (29) 111-22-33',
            specialization='Master'
        )
        self.assertEqual(employee.specialization, 'Master')
        self.assertEqual(str(employee), f'{self.user.username} - Master')


class ServiceModelTest(TestCase):
    """Тесты модели Service"""
    
    def setUp(self):
        self.service_type = ServiceType.objects.create(name='Repair')
    
    def test_service_creation(self):
        service = Service.objects.create(
            name='Screen Replacement',
            service_type=self.service_type,
            price=150.00
        )
        self.assertEqual(service.name, 'Screen Replacement')
        self.assertEqual(float(service.price), 150.00)
    
    def test_service_str_method(self):
        service = Service.objects.create(
            name='Diagnostic',
            service_type=self.service_type,
            price=50.00
        )
        self.assertIn('50.0', str(service))


class OrderModelTest(TestCase):
    """Тесты модели Order"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='client_user', password='12345')
        self.client_obj = ClientModel.objects.create(
            user=self.user,
            full_name='Test Client',
            phone='+375 (29) 123-45-67',
            address='Test Address',
            birth_date=date(1990, 1, 1)
        )
        self.service_type = ServiceType.objects.create(name='Repair')
        self.service = Service.objects.create(
            name='Test Service',
            service_type=self.service_type,
            price=100.00
        )
    
    def test_order_creation(self):
        order = Order.objects.create(
            client=self.client_obj,
            client_problem='Test problem'
        )
        self.assertEqual(order.status, 'pending')
        self.assertIsNotNone(order.order_date)
    
    def test_order_status_choices(self):
        order = Order.objects.create(
            client=self.client_obj,
            status='completed',
            client_problem='Test'
        )
        self.assertEqual(order.status, 'completed')
    
    def test_total_cost_with_service(self):
        order = Order.objects.create(
            client=self.client_obj,
            client_problem='Test'
        )
        OrderService.objects.create(
            order=order,
            service=self.service,
            quantity=2
        )
        self.assertEqual(float(order.total_cost()), 200.00)


class ViewsTest(TestCase):
    """Тесты представлений"""
    
    def setUp(self):
        from django.test import Client
        self.http_client = Client()  
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client_obj = ClientModel.objects.create(
            user=self.user,
            full_name='Test Client',
            phone='+375 (29) 123-45-67',
            address='Test Address',
            birth_date=date(1990, 1, 1)
        )
    
    def test_home_page_status_code(self):
        response = self.http_client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
    
    def test_service_list_page(self):
        response = self.http_client.get(reverse('service_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_about_page(self):
        response = self.http_client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
    
    def test_contacts_page(self):
        response = self.http_client.get(reverse('contacts'))
        self.assertEqual(response.status_code, 200)
    
    def test_faq_page(self):
        response = self.http_client.get(reverse('faq'))
        self.assertEqual(response.status_code, 200)
    
    def test_vacancies_page(self):
        response = self.http_client.get(reverse('vacancies'))
        self.assertEqual(response.status_code, 200)
    
    def test_reviews_page(self):
        response = self.http_client.get(reverse('reviews'))
        self.assertEqual(response.status_code, 200)
    
    def test_promocodes_page(self):
        response = self.http_client.get(reverse('promocodes'))
        self.assertEqual(response.status_code, 200)
    
    def test_statistics_page(self):
        response = self.http_client.get(reverse('statistics'))
        self.assertEqual(response.status_code, 200)
    
    def test_search_page(self):
        response = self.http_client.get(reverse('search_orders'))
        self.assertEqual(response.status_code, 200)
    
    def test_cabinet_redirect_for_anonymous(self):
        """Неавторизованный пользователь перенаправляется на страницу входа"""
        response = self.http_client.get(reverse('cabinet'))
        self.assertEqual(response.status_code, 302)
    
    def test_cabinet_for_authenticated_client(self):
        self.http_client.login(username='testuser', password='12345')
        response = self.http_client.get(reverse('cabinet'))
        self.assertEqual(response.status_code, 200)
    
    def test_order_detail_requires_login(self):
        order = Order.objects.create(
            client=self.client_obj,
            client_problem='Test'
        )
        response = self.http_client.get(reverse('order_detail', args=[order.id]))
        self.assertEqual(response.status_code, 302)


class AuthenticationTest(TestCase):
    """Тесты аутентификации"""
    
    def setUp(self):
        from django.test import Client
        self.http_client = Client()
        self.register_url = reverse('register')
    
    def test_registration_page_loads(self):
        response = self.http_client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
    
    def test_successful_registration(self):
        response = self.http_client.post(self.register_url, {
            'username': 'newuser',
            'full_name': 'Тестовый Пользователь',
            'email': 'test@example.com',
            'phone': '+375 (29) 123-45-67',
            'address': 'ул. Тестовая, 1',
            'birth_date': '1990-01-01',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        })
        user_exists = User.objects.filter(username='newuser').exists()
        self.assertTrue(user_exists)
    
    def test_registration_with_invalid_age(self):
        """Регистрация с возрастом младше 18 лет должна провалиться"""
        response = self.http_client.post(self.register_url, {
            'username': 'younguser',
            'full_name': 'Молодой Пользователь',
            'email': 'young@example.com',
            'phone': '+375 (29) 111-22-33',
            'address': 'ул. Молодежная, 1',
            'birth_date': '2010-01-01',  
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        })
        user_exists = User.objects.filter(username='younguser').exists()
        self.assertFalse(user_exists)

class SearchTest(TestCase):
    """Тесты поиска и сортировки"""
    
    def setUp(self):
        from django.test import Client
        self.http_client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client_obj = ClientModel.objects.create(
            user=self.user,
            full_name='Ivan Petrov',
            phone='+375 (29) 123-45-67',
            address='Test',
            birth_date=date(1990, 1, 1)
        )
        Order.objects.create(
            client=self.client_obj,
            client_problem='Broken screen'
        )
    
    def test_search_by_client_name(self):
        response = self.http_client.get(reverse('search_orders'), {'q': 'Ivan'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ivan Petrov')
    
    def test_search_with_no_results(self):
        response = self.http_client.get(reverse('search_orders'), {'q': 'Nonexistent'})
        self.assertEqual(response.status_code, 200)


class PhoneValidationTest(TestCase):
    """Тесты валидации телефона"""
    
    def test_valid_phone_format(self):
        user = User.objects.create_user(username='testuser', password='12345')
        client = ClientModel.objects.create(
            user=user,
            full_name='Test',
            phone='+375 (29) 123-45-67',
            address='Test',
            birth_date=date(1990, 1, 1)
        )
        self.assertEqual(client.phone, '+375 (29) 123-45-67')