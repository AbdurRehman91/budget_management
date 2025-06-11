import logging
from django.db import models
from django.utils import timezone
from typing import TYPE_CHECKING
from .brand import Brand

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .brand import Brand


class Campaign(models.Model):
    if TYPE_CHECKING:
        brand: Brand
    else:
        brand = models.ForeignKey(
            Brand, on_delete=models.CASCADE, related_name="campaigns"
        )
    name: models.CharField = models.CharField(
        max_length=255, help_text="Name of the campaign."
    )
    is_active: models.BooleanField = models.BooleanField(
        default=True,
        help_text="Determines if the campaign is currently running or paused. Controlled by budget and dayparting.",
    )
    # Dayparting fields
    start_time: models.TimeField = models.TimeField(
        null=True,
        blank=True,
        help_text="Optional: Start time (HH:MM:SS) for the campaign to be active. Blank means always active.",
    )
    end_time: models.TimeField = models.TimeField(
        null=True,
        blank=True,
        help_text="Optional: End time (HH:MM:SS) for the campaign to be active. Blank means always active.",
    )

    class Meta:
        verbose_name = "Campaign"
        unique_together = ("brand", "name")

    def __str__(self) -> str:
        return f"{self.brand.name} - {self.name}"

    def is_eligible_to_run(self):
        logger.info(f"Checking eligibility for campaign '{self.name}' (ID: {self.id})")
        now = timezone.localtime(timezone.now()).time()
        if self.start_time and self.end_time:
            if self.start_time <= self.end_time:
                return self.start_time <= now <= self.end_time
            else:  # Spans across midnight
                return now >= self.start_time or now <= self.end_time
        return True  # No dayparting set, always eligible within active status

    def is_eligible_by_dayparting(self) -> bool:
        logger.info("Checking for eligible_by_dayparting")
        if self.start_time is None or self.end_time is None:
            return True
        else:
            current_time = timezone.localtime(
                timezone.now()
            ).time()  # Get current time in local timezone

            if self.start_time <= self.end_time:
                # Campaign runs within the same day (e.g., 9:00 to 17:00)
                return self.start_time <= current_time <= self.end_time
            else:
                # Campaign spans across midnight (e.g., 22:00 to 06:00)
                return current_time >= self.start_time or current_time <= self.end_time

    def update_status_based_on_rules(self) -> None:
        logger.info(f"In updating status for campaign '{self.name}' (ID: {self.id})")
        brand_has_budget = (
            self.brand.can_run_campaign()
        )  # Check if brand has *any* budget remaining
        is_within_dayparting = self.is_eligible_by_dayparting()

        campaign_should_be_active = brand_has_budget and is_within_dayparting

        if self.is_active != campaign_should_be_active:
            self.is_active = campaign_should_be_active
            self.save(update_fields=["is_active"])
