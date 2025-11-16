from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.map_view, name='map'),

    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='map'), name='logout'),

    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='map_app/password_reset.html',
             email_template_name='map_app/password_reset_email.html',
             subject_template_name='map_app/password_reset_subject.txt',
             success_url='/password-reset/done/'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='map_app/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='map_app/password_reset_confirm.html',
             success_url='/password-reset-complete/'
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='map_app/password_reset_complete.html'),
         name='password_reset_complete'),

    path('add-nko/', views.add_nko_view, name='add_nko'),
    path('edit-nko/<int:nko_id>/', views.edit_nko_view, name='edit_nko'),
    path('profile/', views.profile_view, name='profile'),

    path('city/<int:city_id>/nkos/', views.get_nko_by_city, name='nko_by_city'),
    path('category/<int:category_id>/nkos/', views.get_nko_by_category, name='nko_by_category'),
    path('moderation/', views.moderation_view, name='moderation'),
    path('api/nkos/', views.get_all_nko_data, name='api_nkos'),
]