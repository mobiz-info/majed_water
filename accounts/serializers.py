from rest_framework import serializers
from . models import *
from client_management.models import CustomerSupplyItems
from django.db.models import Sum

class CustomUserSerializers(serializers.ModelSerializer):
    class Meta :
        model = CustomUser
        exclude = ['groups','user_permissions']
        extra_kwargs = {'password': {'write_only': True}}
        
    def create(self, validated_data):
        user = CustomUser.objects.create(
            username=validated_data['username'],
        )
        user.set_password(validated_data['password'])
        user.save()

        return user

class CustomersCreateSerializers(serializers.ModelSerializer):
    class Meta :
        model = Customers
        fields = '__all__'

class CustomersSerializers(serializers.ModelSerializer):
    location = serializers.SerializerMethodField()
    location_name = serializers.SerializerMethodField()
    total_supply_count = serializers.SerializerMethodField()
    class Meta :
        model = Customers
        fields = [
            'customer_id', 'created_by', 'created_date', 'custom_id', 'customer_name',
            'building_name', 'door_house_no', 'floor_no', 'sales_staff', 'routes', 'location',
            'emirate', 'mobile_no', 'whats_app', 'email_id', 'gps_latitude', 'gps_longitude',
            'customer_type', 'sales_type', 'no_of_bottles_required', 'max_credit_limit',
            'credit_days', 'no_of_permitted_invoices', 'trn', 'billing_address', 'preferred_time',
            'branch_id', 'is_active', 'visit_schedule', 'is_editable', 'user_id', 'rate',
            'coupon_count', 'five_g_count_limit', 'eligible_foc', 'is_calling_customer',
            'total_supply_count','location_name','location'
        ]

    def get_location(self, obj):
        location_id=""
        if obj.location:
            location_id=obj.location.pk
        return location_id
    
    def get_location_name(self, obj):
        location_name=""
        if obj.location:
            location_name=obj.location.location_name
        return location_name
    
    def get_total_supply_count(self, obj):
        total_quantity = CustomerSupplyItems.objects.filter(
            customer_supply__customer=obj
        ).aggregate(total_qty=Sum('quantity'))['total_qty'] or 0
        return total_quantity
        
class Create_Customers_Serializers(serializers.ModelSerializer):
    class Meta :
        model = Customers
        fields = '__all__'


class VisitScheduleSerializer(serializers.Serializer):
    week1 = serializers.ListField(
        child=serializers.ChoiceField(choices=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]),
        required=False
    )
    week2 = serializers.ListField(
        child=serializers.ChoiceField(choices=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]),
        required=False
    )
    week3 = serializers.ListField(
        child=serializers.ChoiceField(choices=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]),
        required=False
    )
    week4 = serializers.ListField(
        child=serializers.ChoiceField(choices=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]),
        required=False
    )
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        visit_schedule = {day: [] for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}

        for week_number in ["week1", "week2", "week3", "week4"]:
            days = data.get(week_number, [])
            for day in days:
                visit_schedule[day].append(week_number.capitalize())

        for day, weeks in visit_schedule.items():
            if not weeks:
                visit_schedule[day] = [""]
            else:
                visit_schedule[day] = [",".join(weeks)]

        return visit_schedule

        