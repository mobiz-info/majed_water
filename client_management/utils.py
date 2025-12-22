from decimal import Decimal
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from invoice_management.models import Invoice

def get_customer_outstanding_amount(customer):
    """
    Single source of truth:
    Outstanding = SUM(invoice.total - invoice.received)

    Negative = customer credit
    """

    return Invoice.objects.filter(
        customer=customer,
        is_deleted=False
    ).aggregate(
        total=Sum(
            ExpressionWrapper(
                F("amout_total") - F("amout_recieved"),
                output_field=DecimalField()
            )
        )
    )["total"] or Decimal("0.00")
