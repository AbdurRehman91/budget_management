import logging
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal
from typing import Optional
from agency_ads.tasks import process_ad_spend
from .models import AdImpression

logger = logging.getLogger(__name__)


class AddImpressionAPIView(APIView):
    
    def post(self, request, *args, **kwargs) -> Response:
        logger.info("Received request to add ad impression.")
        campaign_id: Optional[int] = request.data.get("campaign_id", None)
        cost_str: Optional[str] = request.data.get("cost", None)

        if not campaign_id or not cost_str:
            return Response(
                {"error": "Missing campaign_id or cost."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            cost: Decimal = Decimal(cost_str)  # Ensure cost_str is a valid decimal
        except Exception as e:
            logger.error(f"Error parsing cost: {e}")
            return Response(
                {"error": "Invalid cost format."}, status=status.HTTP_400_BAD_REQUEST
            )

        process_ad_spend.delay(campaign_id, cost)

        return JsonResponse({"message": "Ad impression processing initiated. Check logs for final status."}, status=202
    )
