from django.core.management.base import BaseCommand
from accounts.models import CustomUser, Customers
from master.models import RouteMaster
from van_management.models import Van_Routes

class Command(BaseCommand):
    help = 'Generate usernames and passwords for customers based on their name and mobile number'

    def handle(self, *args, **kwargs):
        
        customers = Customers.objects.all()
        
        for customer in customers:
            route = RouteMaster.objects.get(pk=customer.routes.pk)
            sales_staff = Van_Routes.objects.get(routes=route).van.salesman
            
            customer.sales_staff = sales_staff
            customer.save()

        self.stdout.write(self.style.SUCCESS(f'Successfully updated username and password for customer ID {customer.customer_id}, {username}, {password}'))
