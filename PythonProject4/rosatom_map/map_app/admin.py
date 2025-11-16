from django.contrib import admin
from django.utils.html import format_html
from .models import City, NKOCategory, NKO, UserProfile


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'region', 'latitude', 'longitude']
    search_fields = ['name', 'region']
    list_filter = ['region']


@admin.register(NKOCategory)
class NKOCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color']
    search_fields = ['name']


@admin.register(NKO)
class NKOAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'city', 'created_by', 'is_approved', 'created_at', 'actions']
    list_filter = ['is_approved', 'category', 'city', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'created_by']
    list_per_page = 20

    def actions(self, obj):
        if obj.is_approved:
            return format_html(
                '<span style="color: green;">✓ Одобрено</span> | '
                '<a href="?action=reject&id={}">Отклонить</a>',
                obj.id
            )
        else:
            return format_html(
                '<a href="?action=approve&id={}">Одобрить</a> | '
                '<span style="color: red;">✗ На модерации</span>',
                obj.id
            )

    actions.short_description = 'Действия'

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # Быстрые действия через GET параметры
        action = request.GET.get('action')
        nko_id = request.GET.get('id')

        if action and nko_id:
            nko = NKO.objects.get(id=nko_id)
            if action == 'approve':
                nko.is_approved = True
                nko.save()
                self.message_user(request, f'НКО "{nko.name}" одобрена')
            elif action == 'reject':
                nko.is_approved = False
                nko.save()
                self.message_user(request, f'НКО "{nko.name}" отклонена')

        return qs

    def approve_nko(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} НКО одобрено')

    approve_nko.short_description = "Одобрить выбранные НКО"

    def reject_nko(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} НКО отклонено')

    reject_nko.short_description = "Отклонить выбранные НКО"

    actions = [approve_nko, reject_nko]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'city', 'created_at']
    search_fields = ['user__username', 'phone']
    list_filter = ['city', 'created_at']