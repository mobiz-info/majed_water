import datetime
from decimal import Decimal

from django.core.management.base import BaseCommand

from accounts.models import Customers

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        
        Instances = Customers.objects.filter(rate__in=["5.5","5.50"])
        
        for customer in Instances:
            
            # if customer.rate != None:
            #     rate = Decimal(customer.rate)
            # else:
            #     rate = 0
                
            # customer.prevous_rate = rate
            # customer.save()
            
            self.stdout.write(self.style.WARNING(f'Successfully updated {customer.customer_name} -- {customer.rate}'))
            
        self.stdout.write(self.style.SUCCESS(f'Successfully updated all supplies are updated'))
