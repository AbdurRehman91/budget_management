import logging
from celery import shared_task
from django.utils import timezone
from decimal import Decimal
from datetime import date
from .models import Brand, Campaign, AdImpression

logger = logging.getLogger(__name__)


@shared_task
def process_ad_spend(campaign_id: int, cost: Decimal) -> bool:
    """
    Tracks and updates daily and monthly ad spend for a given campaign.
    This task would be called whenever an ad impression occurs.
    """
    try:
        success: bool = AdImpression.record_impression(campaign_id, cost)
        if not success:
            logger.info(f"Celery task recording impression rejected.")
        return success
    except Exception as e:
        logger.error(f"getting exception for processing ad spend : {e}")
        return False


@shared_task
def reset_daily_budgets() -> None:
    """
    Resets daily budgets for all brands and reactivates eligible campaigns.
    Runs daily via Celery Beat.
    """

    today: date = timezone.localdate(
        timezone.now()
    )  # ensure we use timezone-aware date
    logger.info(f"Running daily budget reset for: {today}")
    for brand in Brand.objects.all():
        if brand.last_daily_reset < today:
            brand.current_daily_spend = Decimal("0.00")
            brand.last_daily_reset = today
            brand.save()
            logger.info(f"Daily budget for brand '{brand.name}' reset.")
            # Reactivate eligible campaigns
            reactivate_eligible_campaigns.delay(brand.pk)
        else:
            logger.info(f"Daily budget for brand '{brand.name}' already reset today.")


@shared_task
def reset_monthly_budgets() -> None:
    """
    Resets monthly budgets for all brands and reactivates eligible campaigns.
    Runs daily, but checks for month start.
    """
    today: date = timezone.localdate(timezone.now())
    logger.info("In resetting monthly budgets task")
    for brand in Brand.objects.all():
        if (
            brand.last_monthly_reset.month != today.month
            or brand.last_monthly_reset.year != today.year
        ):
            brand.current_monthly_spend = Decimal("0.00")
            brand.last_monthly_reset = today
            brand.save()
            logger.info(f"Monthly budget for brand '{brand.name}' reset.")
            # Reactivate eligible campaigns
            reactivate_eligible_campaigns.delay(brand.pk)
        else:
            logger.info(f"Monthly budget not yet due for reset.")


@shared_task
def reactivate_eligible_campaigns(brand_id: int) -> None:
    """
    Reactivates campaigns for a given brand if their budgets allow.
    This is called after daily/monthly resets.
    """
    try:
        brand: Brand = Brand.objects.get(id=brand_id)
        if (
            brand.current_daily_spend < brand.daily_budget
            and brand.current_monthly_spend < brand.monthly_budget
        ):
            for campaign in Campaign.objects.filter(
                brand=brand, is_active=False
            ):  # Only reactivate if not explicitly paused by an admin, for example
                # For now , we assume if it's inactive due to budget, we reactivate
                campaign.is_active = True
                campaign.save()
                logger.info(
                    f"Campaign '{campaign.name}' reactivated for brand '{brand.name}'."
                )
        else:
            logger.info(
                f"Brand '{brand.name}' is still over budget or has not reset fully"
            )
    except Brand.DoesNotExist:
        logger.info(f"Brand with ID {brand_id} not found.")


@shared_task
def check_and_toggle_campaigns() -> None:
    """
    Periodically checks all campaigns for dayparting and budget status,
    turning them on/off as necessary.
    Runs frequently via Celery Beat.
    """
    logger.info("Running check and toggle campaigns task.")
    for campaign in Campaign.objects.all():
        brand: Brand = campaign.brand
        is_within_budget: bool = (
            brand.current_daily_spend < brand.daily_budget
            and brand.current_monthly_spend < brand.monthly_budget
        )

        is_eligible_by_dayparting: bool = campaign.is_eligible_to_run()

        should_be_active: bool = is_within_budget and is_eligible_by_dayparting

        if campaign.is_active and not should_be_active:
            campaign.is_active = False
            campaign.save()
            logger.info(
                f"Campaign '{campaign.name}' turned OFF (Budget or Dayparting)."
            )
        elif not campaign.is_active and should_be_active:
            campaign.is_active = True
            campaign.save()
            logger.info(
                f"Campaign '{campaign.name}' turned ON (Budget and Dayparting allow)."
            )
        else:
            logger.info(
                f"Campaign '{campaign.name}' status unchanged ({'Active' if campaign.is_active else 'Inactive'})."
            )
