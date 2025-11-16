from django.core.management.base import BaseCommand
from map_app.models import City, NKOCategory, NKO
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Add sample NKO data'

    def handle(self, *args, **options):
        # Создаем тестового пользователя
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@example.com', 'is_staff': True}
        )

        # Получаем города и категории
        cities = City.objects.all()[:10]  # Берем первые 10 городов
        categories = NKOCategory.objects.all()

        sample_nkos = [
            {
                'name': 'Центр помощи детям "Надежда"',
                'description': 'Оказываем помощь детям из малообеспеченных семей, организуем досуг и образовательные программы.',
                'address': 'ул. Центральная, 15',
                'phone': '+7 (495) 123-45-67',
                'website': 'https://childhelp.example.com',
                'vk_link': 'https://vk.com/childhelp',
                'category': 'Социальные'
            },
            {
                'name': 'Экологический патруль',
                'description': 'Занимаемся охраной окружающей среды, организуем субботники и экологические акции.',
                'address': 'ул. Зеленая, 25',
                'phone': '+7 (495) 234-56-78',
                'website': 'https://ecopatrol.example.com',
                'vk_link': 'https://vk.com/ecopatrol',
                'category': 'Экологические'
            },
            {
                'name': 'Культурный центр "Искусство"',
                'description': 'Проводим выставки, концерты и мастер-классы для всех желающих.',
                'address': 'пр. Культуры, 10',
                'phone': '+7 (495) 345-67-89',
                'website': 'https://artcenter.example.com',
                'vk_link': 'https://vk.com/artcenter',
                'category': 'Культурные'
            },
            {
                'name': 'Образовательный центр "Знание"',
                'description': 'Бесплатные курсы и репетиторство для школьников и студентов.',
                'address': 'ул. Учебная, 5',
                'phone': '+7 (495) 456-78-90',
                'website': 'https://knowledge.example.com',
                'vk_link': 'https://vk.com/knowledge',
                'category': 'Образовательные'
            },
            {
                'name': 'Медицинская помощь "Здоровье"',
                'description': 'Бесплатная медицинская консультация и помощь нуждающимся.',
                'address': 'ул. Медицинская, 20',
                'phone': '+7 (495) 567-89-01',
                'website': 'https://health.example.com',
                'vk_link': 'https://vk.com/health',
                'category': 'Медицинские'
            }
        ]

        for i, nko_data in enumerate(sample_nkos):
            city = cities[i % len(cities)]
            category = categories.get(name=nko_data['category'])

            # Добавляем небольшие смещения к координатам города
            latitude = city.latitude + (i * 0.01 - 0.02)
            longitude = city.longitude + (i * 0.01 - 0.02)

            NKO.objects.get_or_create(
                name=nko_data['name'],
                defaults={
                    'category': category,
                    'description': nko_data['description'],
                    'address': nko_data['address'],
                    'phone': nko_data['phone'],
                    'website': nko_data['website'],
                    'vk_link': nko_data['vk_link'],
                    'city': city,
                    'latitude': latitude,
                    'longitude': longitude,
                    'created_by': user,
                    'is_approved': True
                }
            )

        self.stdout.write(self.style.SUCCESS('Successfully added sample NKO data'))