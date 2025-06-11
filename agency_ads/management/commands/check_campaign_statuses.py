from django.core.management.base import BaseCommand
from agency_ads.models import Campaign


class Command(BaseCommand):
    help = "Checks and updates the active status of all campaigns based on dayparting and budget."

    def handle(self, *args, **options) -> None:
        self.stdout.write("Starting campaign Status Check")

        updated_count: int = 0
        for campaign in Campaign.objects.select_related("brand").all():
            old_is_active: bool = campaign.is_active
            campaign.update_status_based_on_rules()
            if old_is_active != campaign.is_active:
                updated_count += 1
                self.stdout.write(
                    f"  - Campaign '{campaign.name}' status changed to {'Active' if campaign.is_active else 'Inactive'}."
                )
            else:
                self.stdout.write(
                    f"  - Campaign '{campaign.name}' status remains {'Active' if campaign.is_active else 'Inactive'}."
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Campaign status check completed. {updated_count} campaigns had their status updated."
            )
        )
