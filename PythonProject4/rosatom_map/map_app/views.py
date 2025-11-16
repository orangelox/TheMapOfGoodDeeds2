from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import City, NKOCategory, NKO
from .forms import CustomUserCreationForm, UserProfileForm
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
import json


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


def map_view(request):
    cities = City.objects.all()
    categories = NKOCategory.objects.all()
    approved_nkos = NKO.objects.filter(is_approved=True)

    cities_data = []
    for city in cities:
        cities_data.append({
            'id': city.id,
            'name': city.name,
            'region': city.region,
            'latitude': city.latitude,
            'longitude': city.longitude,
        })

    if cities:
        avg_lat = sum(city.latitude for city in cities) / len(cities)
        avg_lon = sum(city.longitude for city in cities) / len(cities)
    else:
        avg_lat, avg_lon = 55.7558, 37.6173

    nko_data = []
    for nko in approved_nkos:
        nko_data.append({
            'id': nko.id,
            'name': nko.name,
            'category': nko.category.name,
            'category_id': nko.category.id,
            'category_color': nko.category.color,
            'description': nko.description,
            'address': nko.address,
            'phone': nko.phone,
            'website': nko.website,
            'vk_link': nko.vk_link,
            'city': str(nko.city),
            'latitude': nko.latitude,
            'longitude': nko.longitude,
        })

    context = {
        'cities': cities,
        'categories': categories,
        'nko_data_json': json.dumps(nko_data, ensure_ascii=False),
        'cities_json': json.dumps(cities_data, ensure_ascii=False),
        'map_center_lat': avg_lat,
        'map_center_lon': avg_lon,
    }
    return render(request, 'map_app/map.html', context)


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно! Теперь вы можете добавить свою НКО.')
            return redirect('add_nko')
    else:
        form = CustomUserCreationForm()

    return render(request, 'map_app/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('map')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')

    return render(request, 'map_app/login.html')


@login_required
def add_nko_view(request):
    if NKO.objects.filter(created_by=request.user).exists():
        messages.warning(request,
                         'Вы уже добавили одну НКО. К одному аккаунту можно привязать только одну организацию.')
        return redirect('profile')

    categories = NKOCategory.objects.all()
    cities = City.objects.all()

    if request.method == 'POST':
        try:
            nko = NKO(
                name=request.POST.get('name'),
                category_id=request.POST.get('category'),
                description=request.POST.get('description'),
                address=request.POST.get('address', ''),
                phone=request.POST.get('phone', ''),
                website=request.POST.get('website', ''),
                vk_link=request.POST.get('vk_link', ''),
                city_id=request.POST.get('city'),
                created_by=request.user,
                is_approved=False
            )

            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            if latitude and longitude:
                nko.latitude = float(latitude)
                nko.longitude = float(longitude)
            else:
                city = City.objects.get(id=request.POST.get('city'))
                nko.latitude = city.latitude
                nko.longitude = city.longitude

            nko.save()
            messages.success(request, 'НКО успешно добавлена и отправлена на модерацию!')
            return redirect('map')

        except Exception as e:
            messages.error(request, f'Ошибка при добавлении НКО: {str(e)}')

    return render(request, 'map_app/add_nko.html', {
        'categories': categories,
        'cities': cities
    })


@login_required
def edit_nko_view(request, nko_id):
    nko = get_object_or_404(NKO, id=nko_id, created_by=request.user)

    if request.method == 'POST':
        nko.name = request.POST.get('name')
        nko.category_id = request.POST.get('category')
        nko.description = request.POST.get('description')
        nko.address = request.POST.get('address', '')
        nko.phone = request.POST.get('phone', '')
        nko.website = request.POST.get('website', '')
        nko.vk_link = request.POST.get('vk_link', '')
        nko.city_id = request.POST.get('city')
        nko.is_approved = False

        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        if latitude and longitude:
            nko.latitude = float(latitude)
            nko.longitude = float(longitude)

        nko.save()
        messages.success(request, 'Информация о НКО успешно обновлена и отправлена на модерацию!')
        return redirect('map')

    categories = NKOCategory.objects.all()
    cities = City.objects.all()
    return render(request, 'map_app/edit_nko.html', {
        'nko': nko,
        'categories': categories,
        'cities': cities
    })


@login_required
def profile_view(request):
    user_nko = NKO.objects.filter(created_by=request.user).first()

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile')
    else:
        profile_form = UserProfileForm(instance=request.user.userprofile)

    context = {
        'user_nko': user_nko,
        'profile_form': profile_form,
    }
    return render(request, 'map_app/profile.html', context)


def get_nko_by_city(request, city_id):
    nkos = NKO.objects.filter(city_id=city_id, is_approved=True)
    nko_data = []
    for nko in nkos:
        nko_data.append({
            'id': nko.id,
            'name': nko.name,
            'category': nko.category.name,
            'category_color': nko.category.color,
            'description': nko.description,
            'address': nko.address,
            'phone': nko.phone,
            'website': nko.website,
            'vk_link': nko.vk_link,
            'latitude': nko.latitude,
            'longitude': nko.longitude,
        })
    return JsonResponse({'nkos': nko_data})


def get_nko_by_category(request, category_id):
    nkos = NKO.objects.filter(category_id=category_id, is_approved=True)
    nko_data = []
    for nko in nkos:
        nko_data.append({
            'id': nko.id,
            'name': nko.name,
            'category': nko.category.name,
            'category_color': nko.category.color,
            'description': nko.description,
            'address': nko.address,
            'phone': nko.phone,
            'website': nko.website,
            'vk_link': nko.vk_link,
            'city': str(nko.city),
            'latitude': nko.latitude,
            'longitude': nko.longitude,
        })
    return JsonResponse({'nkos': nko_data})





@staff_member_required
def moderation_view(request):
    pending_nkos = NKO.objects.filter(is_approved=False).select_related('category', 'city', 'created_by')
    approved_nkos = NKO.objects.filter(is_approved=True).select_related('category', 'city', 'created_by')

    if request.method == 'POST':
        nko_id = request.POST.get('nko_id')
        action = request.POST.get('action')

        if nko_id and action:
            nko = get_object_or_404(NKO, id=nko_id)
            if action == 'approve':
                nko.is_approved = True
                nko.save()
                messages.success(request, f'НКО "{nko.name}" одобрена')
            elif action == 'reject':
                nko.is_approved = False
                nko.save()
                messages.success(request, f'НКО "{nko.name}" отклонена')

            return redirect('moderation')

    context = {
        'pending_nkos': pending_nkos,
        'approved_nkos': approved_nkos,
    }
    return render(request, 'map_app/moderation.html', context)


def get_all_nko_data(request):
    """API endpoint для получения всех данных НКО"""
    approved_nkos = NKO.objects.filter(is_approved=True).select_related('category', 'city')

    nko_data = []
    for nko in approved_nkos:
        nko_data.append({
            'id': nko.id,
            'name': nko.name,
            'category': nko.category.name,
            'category_id': nko.category.id,
            'category_color': nko.category.color,
            'description': nko.description,
            'address': nko.address,
            'phone': nko.phone,
            'website': nko.website,
            'vk_link': nko.vk_link,
            'city': str(nko.city),
            'latitude': nko.latitude,
            'longitude': nko.longitude,
        })

    return JsonResponse({'nkos': nko_data})