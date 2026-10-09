from django.contrib import admin
from .models import HomePage


@admin.register(HomePage)
class HomePageAdmin(admin.ModelAdmin):
    list_display = ("title", "hero_badge", "hero_title", "live", "first_published_at", "last_published_at")
    search_fields = ("title", "hero_title", "hero_subtitle")
    list_filter = ("live", "first_published_at")
    readonly_fields = ("first_published_at", "last_published_at", "latest_revision_created_at")
