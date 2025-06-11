import logging
from decimal import Decimal
from django.db import models
from django.db import transaction
from typing import TYPE_CHECKING, cast
from .brand import Brand
from .campaign import Campaign

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .brand import Brand


class AdImpression(models.Model):
    if TYPE_CHECKING:
        campaign: Campaign
    else:
        campaign = models.ForeignKey(
            Campaign, on_delete=models.PROTECT, related_name="impressions"
        )
    cost: models.DecimalField = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Cost incurred for this single ad impression.",
    )
    timestamp: models.DateTimeField = models.DateTimeField(
        auto_now_add=True, help_text="Date and time when the impression occurred."
    )

    class Meta:
        verbose_name = "Ad Impression"
        ordering = ["-timestamp"]

    def __str__(self) -> str:
        return f"Impression for {self.campaign.name} - at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

    @classmethod
    def record_impression(cls, campaign_id: int, cost: Decimal) -> bool:
        try:
            logger.info(f"recording impression for campaign id: {campaign_id}")
            with transaction.atomic():
                campaign: Campaign = Campaign.objects.select_for_update().get(
                    id=campaign_id
                )
                brand: Brand = cast(Brand, campaign.brand)

                # Ensure campaign is active and within dayparting before processing cost
                if not campaign.is_active or not campaign.is_eligible_by_dayparting():
                    logger("Campaign is not active or not eligible by dayparting")
                    return False  # Don't record spend for an ineligible impression

                # Check if brand can actually afford this impression
                if not brand.can_run_campaign(cost):
                    logger("Budget exceeded for the campaign")
                    campaign.is_active = False
                    campaign.save(update_fields=["is_active"])
                    return False
                logger.info("now recording the impression")
                # Record the impression
                AdImpression.objects.create(campaign=campaign, cost=cost)

                # Update brand's spend
                brand.current_daily_spend += cost
                brand.current_monthly_spend += cost
                brand.save(
                    update_fields=["current_daily_spend", "current_monthly_spend"]
                )
                logger.info(f"Brand '{brand.name}' updated daily spend to {brand.current_daily_spend}.")
                # Immediately check and update campaign status if budgets are now exceeded
                campaign.update_status_based_on_rules()

                logger.info(f"Recorded impression for {campaign.name}. Cost: ${cost}.")
                return True

        except Campaign.DoesNotExist:
            logger.info("Campaign with ID {campaign_id} does not exist.")
            return False
        except Exception as ex:  # noqa
            logger.info("Exception occurred while recording impression: %s", ex)
            return False
