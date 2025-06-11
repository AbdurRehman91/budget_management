from django.contrib import admin
from .models import Brand, Campaign, AdImpression


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "daily_budget",
        "current_daily_spend",
        "last_daily_reset",
        "monthly_budget",
        "current_monthly_spend",
        "last_monthly_reset",
    )
    search_fields = ("name",)
    list_filter = ("last_daily_reset", "last_monthly_reset")
    readonly_fields = (
        "current_daily_spend",
        "current_monthly_spend",
        "last_daily_reset",
        "last_monthly_reset",
    )

    fieldsets = (
        (None, {"fields": ("name", "daily_budget", "monthly_budget")}),
        (
            "Current Spend & Last Reset",
            {
                "fields": (
                    "current_daily_spend",
                    "last_daily_reset",
                    "current_monthly_spend",
                    "last_monthly_reset",
                ),
                "description": "These fields are updated automatically by the system.",
            },
        ),
    )


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "is_active", "start_time", "end_time")
    list_filter = ("is_active", "brand")
    search_fields = ("name", "brand__name")
    list_editable = ("is_active",)

    fieldsets = (
        (None, {"fields": ("brand", "name", "is_active")}),
        (
            "Dayparting Schedule",
            {
                "fields": ("start_time", "end_time"),
                "description": "Campaigns will only run between these times. Leave blank for 24/7.",
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(AdImpression)
class AdImpressionAdmin(admin.ModelAdmin):
    list_display = ("campaign", "cost", "timestamp")
    list_filter = ("campaign__brand", "campaign")
    search_fields = ("campaign__name", "campaign__brand__name")
    readonly_fields = ("campaign", "cost", "timestamp")  # Impressions are read-only
    date_hierarchy = ("timestamp")
