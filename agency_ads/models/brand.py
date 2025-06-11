import logging
from django.db import models
from django.utils import timezone
from decimal import Decimal

logger = logging.getLogger(__name__)

class Brand(models.Model):
    name: models.CharField = models.CharField(
        max_length=255, unique=True, help_text="Unique name of the brand."
    )
    daily_budget: models.DecimalField = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Maximum allowed advertising spend per day for this brand.",
    )
    monthly_budget: models.DecimalField = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Maximum allowed advertising spend per month for this brand.",
    )
    current_daily_spend: models.DecimalField = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Current accumulated spend for the current day.",
    )
    current_monthly_spend: models.DecimalField = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Current accumulated spend for the current month.",
    )
    last_daily_reset: models.DateField = models.DateField(
        default=timezone.now, help_text="The date when the daily budget was last reset."
    )
    last_monthly_reset: models.DateField = models.DateField(
        default=timezone.now,
        help_text="The date when the monthly budget was last reset.",
    )

    class Meta:
        verbose_name = "Brand"

    def __str__(self) -> str:
        return self.name

    def reset_daily_budget(self) -> None:
        self.current_daily_spend = Decimal("0.00")
        self.last_daily_reset = timezone.localdate(timezone.now())
        self.save()
        logger.info(f"Daily budget for brand '{self.name}' reset to 0.")

    def reset_monthly_budget(self) -> None:
        self.current_monthly_spend = Decimal("0.00")
        self.last_monthly_reset = timezone.localdate(timezone.now())
        self.save()
        logger.info(f"Monthly budget for brand '{self.name}' reset to 0.")

    def can_run_campaign(self, current_cost=Decimal("0.00")) -> bool:
        logger.info(f"Checking if brand '{self.name}' can run campaign with cost ${current_cost}.")
        return (self.current_daily_spend + current_cost <= self.daily_budget) and (
            self.current_monthly_spend + current_cost <= self.monthly_budget
        )
