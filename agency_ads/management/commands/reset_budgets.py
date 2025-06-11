from django.core.management.base import BaseCommand
from django.utils import timezone
from agency_ads.models import Brand, Campaign
from typing import Tuple
import datetime


class Command(BaseCommand):
    help = "Resets daily and monthly budgets for all brands and reactivates eligible campaigns."

    def handle(self, *args, **options) -> None:
        self.stdout.write("Starting budget reset process...")
        today: datetime.date = timezone.localdate(timezone.now())

        brands_processed: int = 0
        campaigns_reactivated: int = 0

        for brand in Brand.objects.all():
            self.stdout.write(f"Processing brand: {brand.name}")
            needs_daily_reset, needs_monthly_reset = self.reset_brand_budgets(
                brand, today
            )

            if needs_daily_reset or needs_monthly_reset:
                brands_processed += 1
                campaigns_reactivated += self.reactivate_campaigns(brand)
            else:
                self.stdout.write(f"  - No budget reset needed for '{brand.name}'.")

        self.stdout.write(
            self.style.SUCCESS(
                f"Budget reset process completed. {brands_processed} brands had budgets reset. {campaigns_reactivated} campaigns potentially reactivated."
            )
        )

    def reset_brand_budgets(
        self, brand: Brand, today: datetime.date
    ) -> Tuple[bool, bool]:
        needs_daily_reset: bool = False
        needs_monthly_reset: bool = False

        if brand.last_daily_reset < today:
            brand.reset_daily_budget()
            needs_daily_reset = True
            self.stdout.write(f"  - Daily budget reset for '{brand.name}'.")
        else:
            self.stdout.write(
                f"  - Daily budget for brand '{brand.name}' already reset today."
            )

        if (
            brand.last_monthly_reset.month != today.month
            or brand.last_monthly_reset.year != today.year
        ):
            brand.reset_monthly_budget()
            needs_monthly_reset = True
            self.stdout.write(f"  - Monthly budget reset for '{brand.name}'.")
        else:
            self.stdout.write(
                f"  - Monthly budget for brand '{brand.name}' not yet due for reset."
            )

        return needs_daily_reset, needs_monthly_reset

    def reactivate_campaigns(self, brand: Brand) -> int:
        campaigns_reactivated: int = 0
        for campaign in Campaign.objects.filter(brand=brand):
            old_is_active = campaign.is_active
            campaign.update_status_based_on_rules()
            if not old_is_active and campaign.is_active:
                campaigns_reactivated += 1
        return campaigns_reactivated
