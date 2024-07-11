from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from van_management.models import VanProductStock

class Command(BaseCommand):
    help = 'Update or create opening counts for today based on yesterday\'s closing counts'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)

        yesterday_stocks = VanProductStock.objects.filter(created_date=yesterday)
        for yesterday_stock in yesterday_stocks:
            # Separate the lookup and creation logic
            today_stock = VanProductStock.objects.filter(
                product=yesterday_stock.product,
                van=yesterday_stock.van,
                created_date=today
            ).first()

            if today_stock:
                today_stock.opening_count = yesterday_stock.closing_count
                today_stock.stock += yesterday_stock.closing_count
                today_stock.save()
                self.stdout.write(self.style.SUCCESS(f'Updated opening count for {today_stock.id}'))
            else:
                VanProductStock.objects.create(
                    product=yesterday_stock.product,
                    van=yesterday_stock.van,
                    created_date=today,
                    opening_count=yesterday_stock.closing_count,
                    closing_count=yesterday_stock.closing_count, 
                    change_count=yesterday_stock.change_count,
                    damage_count=yesterday_stock.damage_count,
                    empty_can_count=yesterday_stock.empty_can_count,
                    return_count=yesterday_stock.return_count,
                    stock=yesterday_stock.closing_count
                )
                self.stdout.write(self.style.SUCCESS(f'Created new stock entry for product {yesterday_stock.product.pk} in van {yesterday_stock.van.pk}'))

        self.stdout.write(self.style.SUCCESS('Stock update process completed.'))
