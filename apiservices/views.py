import re
import uuid
import base64
import datetime
from datetime import datetime, date, time

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q, F
from decimal import Decimal
from django.http import Http404
from django.urls import reverse
from django.db import transaction
from django.http import JsonResponse
from django.db import transaction, IntegrityError

#from .models import *
from django.utils import timezone
from django.contrib.auth import authenticate,login
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Sum, Value, DecimalField, Min
######rest framwework section

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.serializers import Serializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import BasePermission, IsAuthenticated,IsAuthenticatedOrReadOnly

from accounts.models import *
from invoice_management.models import INVOICE_TYPES, Invoice, InvoiceDailyCollection, InvoiceItems
from client_management.forms import CoupenEditForm
from master.serializers import *
from master.functions import generate_serializer_errors, get_custom_id, get_next_visit_date
from master.models import *
from random import randint
from datetime import datetime as dt
from coupon_management.models import *
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated


from accounts.models import *
from master.models import *
from product.models import *
from sales_management.models import *
from van_management.models import *
from customer_care.models import *
from order.models import *


from master.serializers import *
from product.serializers import *
from van_management.serializers import *
from accounts.serializers import *
from .serializers import *
from client_management.serializers import VacationSerializer
from coupon_management.serializers import *
from order.serializers import *


import random
import string
from django.core.mail import EmailMessage
import threading
import pytz
import datetime as datim

from .serializers import CustomersOutstandingCouponSerializer
utc=pytz.UTC
import logging,traceback
from logging import *
from rest_framework.exceptions import (
 APIException,               #for api exception
 ValidationError
)
logger=logging.getLogger(__name__)

from datetime import timedelta
from django.db.models import Sum,Value
from django.db.models.functions import Coalesce
from django.utils.dateparse import parse_date

def log_activity(created_by, description, created_date=None):
    if created_date is None:
        created_date = timezone.now()
    Processing_Log.objects.create(
        created_by=created_by,
        description=description,
        created_date=created_date
    )


def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

class Login_Api(APIView):
    def post(self, request, *args, **kwargs):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            if username and password:
                user = authenticate(username=username, password=password)
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        user_obj = CustomUser.objects.filter(username=username).first()
                        token = generate_random_string(20)  # Adjust the token length as needed
                        data = {
                            'id': user_obj.id,
                            'username': username,
                            'user_type': user_obj.user_type,
                            'token': token
                        }
                        # Log the login activity
                        log_activity(
                            created_by=user_obj,
                            description=f"User '{username}' logged in."
                        )
                    else:
                        return Response({'status': False, 'message': 'User Inactive!'})
                    return Response({'status': True, 'data': data, 'message': 'Authenticated User!'})
                else:
                    return Response({'status': False, 'message': 'Unauthenticated User!'})
            else:
                return Response({'status': False, 'message': 'Enter a Valid Username and Password!'})
        except CustomUser.DoesNotExist:
            return Response({'status': False, 'message': 'User does not exist!'})
        except Exception as e:
            print(f'Something went wrong: {e}')
            return Response({'status': False, 'message': 'Something went wrong!'})
        
class StoreKeeperLoginApi(APIView):
    def post(self, request, *args, **kwargs):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            if username and password:
                user = authenticate(username=username, password=password, user_type="store_keeper")
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        user_obj = CustomUser.objects.filter(username=username).first()
                        token = generate_random_string(20)  # Adjust the token length as needed
                        data = {
                            'id': user_obj.id,
                            'username': username,
                            'user_type': user_obj.user_type,
                            'token': token
                        }
                        
                        log_activity(
                            created_by=user_obj,
                            description=f"Store Keeper '{username}' logged in."
                        )
                    else:
                        return Response({'status': False, 'message': 'User Inactive!'})
                    return Response({'status': True, 'data': data, 'message': 'Authenticated User!'})
                else:
                    return Response({'status': False, 'message': 'Unauthenticated User!'})
            else:
                return Response({'status': False, 'message': 'Unauthenticated User!'})
        except CustomUser.DoesNotExist:
            return Response({'status': False, 'message': 'User does not exist!'})
        except Exception as e:
            return Response({'status': False, 'message': 'Something went wrong!'})

class MarketingExecutiveLoginApi(APIView):
    def post(self, request, *args, **kwargs):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            if username and password:
                user = authenticate(username=username, password=password, user_type="marketing_executive")
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        user_obj = CustomUser.objects.filter(username=username).first()
                        token = generate_random_string(20)  # Adjust the token length as needed
                        data = {
                            'id': user_obj.id,
                            'username': username,
                            'user_type': user_obj.user_type,
                            'token': token
                        }
                        
                        log_activity(
                            created_by=user_obj,
                            description=f"Marketing Executive '{username}' logged in."
                        )
                    else:
                        return Response({'status': False, 'message': 'User Inactive!'})
                    return Response({'status': True, 'data': data, 'message': 'Authenticated User!'})
                else:
                    return Response({'status': False, 'message': 'Unauthenticated User!'})
            else:
                return Response({'status': False, 'message': 'Unauthenticated User!'})
        except CustomUser.DoesNotExist:
            return Response({'status': False, 'message': 'User does not exist!'})
        except Exception as e:
            return Response({'status': False, 'message': 'Something went wrong!'})


class RouteMaster_API(APIView):
    serializer_class = RouteMasterSerializers
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    # permission_classes = [IsAuthenticated]
    def get(self,request,id=None):
        try:
            if id :
                queryset=RouteMaster.objects.get(route_id=id)
                serializer=RouteMasterSerializers(queryset)
                return Response(serializer.data)
            queryset=RouteMaster.objects.all()
            serializer=RouteMasterSerializers(queryset,many=True)
            return Response(serializer.data)
        except  Exception as e:
            print(e)
            return Response({'status': False, 'message': 'Something went wrong!'})

    def post(self,request):
        try:
            serializer=RouteMasterSerializers(data=request.data)
            if serializer.is_valid():
                branch_id=request.user.branch_id.branch_id
                branch = BranchMaster.objects.get(branch_id=branch_id)
                route_master=serializer.save(created_by=request.user.id,branch_id=branch)
                log_activity(
                    created_by=request.user,
                    description=f"Route '{route_master.route_name}' was created by {request.user.username}."
                )
                data = {'data': 'successfully added'}
                return Response(data,status=status.HTTP_201_CREATED)
            return Response({'data':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except  Exception as e:
            print(e)
            return Response({'status': False, 'message': 'Something went wrong!'})

    def put(self, request, id):
        try:
            route = RouteMaster.objects.get(route_id=id)
            serializer = RouteMasterSerializers(route, data=request.data)
            if serializer.is_valid():
                updated_route = serializer.save(modified_by=request.user.id,modified_date = datetime.now())
                
                log_activity(
                    created_by=request.user,
                    description=f"Route '{updated_route.route_name}' was updated by {request.user.username}."
                )
                
                return Response(serializer.data,status=status.HTTP_200_OK)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        except  Exception as e:
            print(e)
            return Response({'status': False, 'message': 'Something went wrong!'})

    def delete(self, request, id):
        try:
            # Retrieve the object to be deleted
            instance = RouteMaster.objects.get(route_id=id)
            route_name = instance.route_name
            instance.delete()
            log_activity(
                created_by=request.user,
                description=f"Route '{route_name}' was deleted by {request.user.username}."
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        except RouteMaster.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)



class LocationMaster_API(APIView):
    serializer_class = LocationMasterSerializers
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self,request,id=None):
        try:
            if id :
                queryset=LocationMaster.objects.get(location_id=id)
                serializer=LocationMasterSerializers(queryset)
                return Response(serializer.data)
            queryset=LocationMaster.objects.all()
            serializer=LocationMasterSerializers(queryset,many=True)
            return Response(serializer.data)
        except  Exception as e:
            print(e)
            return Response({'status': False, 'message': 'Something went wrong!'})

    def post(self,request):
        try:
            serializer=LocationMasterSerializers(data=request.data)
            if serializer.is_valid():
                branch_id=request.user.branch_id.branch_id
                branch = BranchMaster.objects.get(branch_id=branch_id)
                location = serializer.save(created_by=request.user.id,branch_id=branch)
                log_activity(
                    created_by=request.user,
                    description=f"Location '{location.location_name}' was created by {request.user.username}."
                )
                data = {'data': 'successfully added'}
                return Response(data,status=status.HTTP_201_CREATED)
            return Response({'data':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except  Exception as e:
            print(e)
            return Response({'status': False, 'message': 'Something went wrong!'})

    def put(self, request, id):
        try:
            route = LocationMaster.objects.get(location_id=id)
            serializer = LocationMasterSerializers(route, data=request.data)
            if serializer.is_valid():
                updated_location = serializer.save(modified_by=request.user.id,modified_date = datetime.now())
                log_activity(
                    created_by=request.user,
                    description=f"Location '{updated_location.location_name}' was updated by {request.user.username}."
                )
                return Response(serializer.data,status=status.HTTP_200_OK)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        except  Exception as e:
            print(e)
            return Response({'status': False, 'message': 'Something went wrong!'})

    def delete(self, request, id):
        try:
            # Retrieve the object to be deleted
            instance = LocationMaster.objects.get(location_id=id)
            location_name = instance.location_name
            instance.delete()
            # Log the activity
            log_activity(
                created_by=request.user,
                description=f"Location '{location_name}' was deleted by {request.user.username}."
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        except LocationMaster.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class DesignationMaster_API(APIView):
    serializer_class = DesignationMasterSerializers
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self,request,id=None):
        if id :
            queryset=DesignationMaster.objects.get(designation_id=id)
            serializer=DesignationMasterSerializers(queryset)
            return Response(serializer.data)
        queryset=DesignationMaster.objects.all()
        serializer=DesignationMasterSerializers(queryset,many=True)
        return Response(serializer.data)

    def post(self,request):
        serializer=DesignationMasterSerializers(data=request.data)
        if serializer.is_valid():
            designation = serializer.save(created_by=request.user.id)
            log_activity(
                created_by=request.user,
                description=f"Designation '{designation.designation_name}' was created by {request.user.username}."
            )
            data = {'data': 'successfully added'}
            return Response(data,status=status.HTTP_201_CREATED)
        return Response({'data':serializer.errors},status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        route = DesignationMaster.objects.get(designation_id=id)
        serializer = DesignationMasterSerializers(route, data=request.data)
        if serializer.is_valid():
            updated_designation = serializer.save(modified_by=request.user.id,modified_date = datetime.now())
            log_activity(
                created_by=request.user,
                description=f"Designation '{updated_designation.designation_name}' was updated by {request.user.username}."
            )
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            # Retrieve the object to be deleted
            instance = DesignationMaster.objects.get(designation_id=id)
            designation_name = instance.designation_name
            instance.delete()
            # Log the activity
            log_activity(
                created_by=request.user,
                description=f"Designation '{designation_name}' was deleted by {request.user.username}."
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        except LocationMaster.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class BranchMaster_API(APIView):
        serializer_class = BranchMasterSerializers
        # authentication_classes = [BasicAuthentication]
        # permission_classes = [IsAuthenticated]

        def get(self,request,id=None):
            if id :
                queryset=BranchMaster.objects.get(branch_id=id)
                serializer=BranchMasterSerializers(queryset)
                return Response(serializer.data)
            queryset=BranchMaster.objects.all()
            serializer=BranchMasterSerializers(queryset,many=True)
            return Response(serializer.data)

        def post(self,request):
            serializer=BranchMasterSerializers(data=request.data)
            print(request.data['branch_id'],'branchid')
            if serializer.is_valid():

                saved_data=serializer.save()
                branch = BranchMaster.objects.get(branch_id=saved_data.branch_id)
                username=request.data["username"]
                password=request.data["password"]
                hashed_password=make_password(password)
                email=branch.email
                user_name=branch.name
                branch_data=CustomUser.objects.create(password=hashed_password,username=username,first_name=user_name,email=email,user_type='Branch User',branch_id=branch)
                log_activity(
                    created_by=request.user,
                    description=f"Branch '{branch.name}' was created by {request.user.username}."
                )
                data = {'data': 'successfully added'}
                return Response(data,status=status.HTTP_201_CREATED)
            return Response({'data':serializer.errors},status=status.HTTP_400_BAD_REQUEST)

        def put(self, request, id):
            route = BranchMaster.objects.get(branch_id=id)
            serializer = BranchMasterSerializers(route, data=request.data)
            if serializer.is_valid():
                updated_branch = serializer.save(modified_by=request.user.id,modified_date = datetime.now())
                log_activity(
                    created_by=request.user,
                    description=f"Branch '{updated_branch.name}' was updated by {request.user.username}."
                )
                return Response(serializer.data,status=status.HTTP_200_OK)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

        def delete(self, request, id):
            try:
                # Retrieve the object to be deleted
                instance = BranchMaster.objects.get(branch_id=id)
                branch_name = instance.name 
                instance.delete()
                log_activity(
                    created_by=request.user,
                    description=f"Branch '{branch_name}' was deleted by {request.user.username}."
                )
                return Response(status=status.HTTP_204_NO_CONTENT)
            except BranchMaster.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)




class CategoryMaster_API(APIView):
    serializer_class = CategoryMasterSerializers
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self,request,id=None):
        if id :
            queryset=CategoryMaster.objects.get(category_id=id)
            serializer=CategoryMasterSerializers(queryset)
            return Response(serializer.data)
        queryset=CategoryMaster.objects.all()
        serializer=CategoryMasterSerializers(queryset,many=True)
        return Response(serializer.data)

    def post(self,request):
        serializer=CategoryMasterSerializers(data=request.data)
        if serializer.is_valid():
            category = serializer.save(created_by=request.user.id)
            log_activity(
                created_by=request.user,
                description=f"Category '{category.category_name}' was created by {request.user.username}."
            )
            data = {'data': 'successfully added'}
            return Response(data,status=status.HTTP_201_CREATED)
        return Response({'data':serializer.errors},status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        category = CategoryMaster.objects.get(category_id=id)
        serializer = CategoryMasterSerializers(category, data=request.data)
        if serializer.is_valid():
            updated_category = serializer.save(modified_by=request.user.id,modified_date = datetime.now())
            log_activity(
                    created_by=request.user,
                    description=f"Category '{updated_category.name}' was updated by {request.user.username}."
                )
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            # Retrieve the object to be deleted
            instance = CategoryMaster.objects.get(category_id=id)
            category_name = instance.name  
            instance.delete()
            log_activity(
                created_by=request.user,
                description=f"Category '{category_name}' was deleted by {request.user.username}."
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CategoryMaster.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class EmirateMaster_API(APIView):
    serializer_class = EmirateMasterSerializers
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self,request,id=None):
        try:
            if id :
                queryset=EmirateMaster.objects.get(emirate_id=id)
                serializer=EmirateMasterSerializers(queryset)
                return Response(serializer.data)
            queryset=EmirateMaster.objects.all()
            serializer=EmirateMasterSerializers(queryset,many=True)
            return Response(serializer.data)
        except  Exception as e:
            print(e)
            return Response({'status': False, 'message': 'Something went wrong!'})

    def post(self,request):
        try:
            serializer=EmirateMasterSerializers(data=request.data)
            if serializer.is_valid():
                emirate = serializer.save(created_by=request.user.id)
                log_activity(
                    created_by=request.user,
                    description=f"Emirate '{emirate.name}' was created by {request.user.username}."
                )
                data = {'data': 'successfully added'}
                return Response(data,status=status.HTTP_201_CREATED)
            return Response({'data':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except  Exception as e:
            print(e)
            return Response({'status': False, 'message': 'Something went wrong!'})

    def put(self, request, id):
        try:
            category = EmirateMaster.objects.get(emirate_id=id)
            serializer = EmirateMasterSerializers(category, data=request.data)
            if serializer.is_valid():
                updated_emirate = serializer.save()
                log_activity(
                    created_by=request.user,
                    description=f"Emirate '{updated_emirate.name}' was updated by {request.user.username}."
                )
                return Response(serializer.data,status=status.HTTP_200_OK)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        except  Exception as e:
            print(e)
            return Response({'status': False, 'message': 'Something went wrong!'})

    def delete(self, request, id):
        try:
            # Retrieve the object to be deleted
            instance = EmirateMaster.objects.get(emirate_id=id)
            emirate_name = instance.name  
            instance.delete()
            log_activity(
                created_by=request.user,
                description=f"Emirate '{emirate_name}' was deleted by {request.user.username}."
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        except EmirateMaster.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


#########-------------------Product-------------------------############

class Product_API(APIView):
    serializer_class = ProductSerializers
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self,request,id=None):
        try:
            if id :
                queryset=Product.objects.get(product_id=id)
                serializer=ProductSerializers(queryset)
                return Response(serializer.data)
            queryset=Product.objects.all()
            serializer=ProductSerializers(queryset,many=True)
            return Response(serializer.data)
        except  Exception as e:
            print(e)
            return Response({'status': False, 'message': 'Something went wrong!'})

    def post(self,request):
        try:
            serializer=ProductSerializers(data=request.data)
            if serializer.is_valid():
                branch_id=request.user.branch_id.branch_id
                branch = BranchMaster.objects.get(branch_id=branch_id)
                product = serializer.save(created_by=request.user.id,branch_id=branch)
                log_activity(
                    created_by=request.user,
                    description=f"Product '{product.product_name}' was created by {request.user.username}."
                )
                data = {'data': 'successfully added'}
                return Response(data,status=status.HTTP_201_CREATED)
            return Response({'data':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except  Exception as e:
            print(e)
            return Response({'status': False, 'message': 'Something went wrong!'})

    def put(self, request, id):
        try:
            product = Product.objects.get(product_id=id)
            serializer = ProductSerializers(product, data=request.data)
            if serializer.is_valid():
                updated_product = serializer.save(modified_by=request.user.id,modified_date = datetime.now())
                log_activity(
                    created_by=request.user,
                    description=f"Product '{updated_product.product_name}' was updated by {request.user.username}."
                )
                return Response(serializer.data,status=status.HTTP_200_OK)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        except  Exception as e:
            print(e)
            return Response({'status': False, 'message': 'Something went wrong!'})

    def delete(self, request, id):
        try:
            # Retrieve the object to be deleted
            instance = Product.objects.get(product_id=id)
            product_name = instance.product_name  
            instance.delete()
            
            log_activity(
                created_by=request.user,
                description=f"Product '{product_name}' was deleted by {request.user.username}."
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Product.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)



class Product_Default_Price_API(APIView):
    serializer_class = Product_Default_Price_Level_Serializers
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self,request,id=None):
        if id :
            queryset=Product_Default_Price_Level.objects.get(def_price_id=id)
            serializer=Product_Default_Price_Level_Serializers(queryset)
            return Response(serializer.data)
        queryset=Product_Default_Price_Level.objects.all()
        serializer=Product_Default_Price_Level_Serializers(queryset,many=True)
        return Response(serializer.data)

    def post(self,request):
        serializer=Product_Default_Price_Level_Serializers(data=request.data)
        if serializer.is_valid():
            default_price_level = serializer.save()
            log_activity(
                created_by=request.user,
                description=f"Default Price Level '{default_price_level.def_price_id}' was created by {request.user.username}."
            )
            data = {'data': 'successfully added'}
            return Response(data,status=status.HTTP_201_CREATED)
        return Response({'data':serializer.errors},status=status.HTTP_400_BAD_REQUEST)


    def put(self, request, id):
        product = Product_Default_Price_Level.objects.get(def_price_id=id)
        serializer = Product_Default_Price_Level_Serializers(product, data=request.data)
        if serializer.is_valid():
            updated_price_level = serializer.save()
            log_activity(
                    created_by=request.user,
                    description=f"Default Price Level '{updated_price_level.def_price_id}' was updated by {request.user.username}."
                )
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            # Retrieve the object to be deleted
            instance = Product_Default_Price_Level.objects.get(def_price_id=id)
            instance_name = instance.def_price_id  
            instance.delete()
            log_activity(
                created_by=request.user,
                description=f"Default Price Level '{instance_name}' was deleted by {request.user.username}."
            )
            
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Product_Default_Price_Level.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


#############-------Van Mangement -------------------###############



class Van_API(APIView):
    serializer_class=VanSerializers
    # authentication_classes = [BasicAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self,request,id=None):
        if id :
            queryset=Van.objects.get(van_id=id)
            serializer=VanSerializers(queryset)
            return Response(serializer.data)
        queryset=Van.objects.all()
        serializer=VanSerializers(queryset,many=True)
        return Response(serializer.data)

    def post(self,request):
        username = request.headers['username']
        print(username,'username')
        serializer=VanSerializers(data=request.data)
        if serializer.is_valid():
            van_driver=Van.objects.filter(driver=request.data['driver']).first()
            van_sales=Van.objects.filter(salesman=request.data['salesman']).first()
            if van_driver :
                data={'data':"Driver is already assigned to van"}
                return Response(data,status=status.HTTP_200_OK)
            elif van_sales :
                data={'data':"Salesman is already assigned to van"}
                return Response(data,status=status.HTTP_200_OK)
            else :
                user=CustomUser.objects.get(api_token=username)
                branch_id=user.branch_id.branch_id
                branch = BranchMaster.objects.get(branch_id=branch_id)
                new_van = serializer.save(created_by=request.user.id,branch_id=branch)
                log_activity(
                    created_by=request.user,
                    description=f"Van '{new_van.van_make}' was created by {request.user.username}."
                )
                data = {'data': 'successfully added'}
                return Response(data,status=status.HTTP_201_CREATED)
        return Response({'data':serializer.errors},status=status.HTTP_400_BAD_REQUEST)


    def put(self, request, id):
        product = Van.objects.get(van_id=id)
        serializer = VanSerializers(product, data=request.data)
        if serializer.is_valid():
            updated_van = serializer.save(modified_by=request.user.id,modified_date = datetime.now())
            log_activity(
                created_by=request.user,
                description=f"Van '{updated_van.van_make}' was updated by {request.user.username}."
            )
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            # Retrieve the object to be deleted
            instance = Van.objects.get(van_id=id)
            instance_name = instance.van_make  
            instance.delete()

            log_activity(
                created_by=request.user,
                description=f"Van '{instance_name}' was deleted by {request.user.username}."
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Van.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)




class Route_Assign(APIView):
    serializer_class=VanRoutesSerializers
    # authentication_classes = [BasicAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self,request):
        queryset = Van_Routes.objects.all()
        serializer = VanRoutesSerializers(queryset,many=True)
        return Response(serializer.data)

    def post(self,request):
        username = request.headers['username']
        van_data = Van.objects.get(van_id = request.data['van'])
        serializer=VanRoutesSerializers(data=request.data)
        if serializer.is_valid():
            route_exists = Van_Routes.objects.filter(van = van_data,routes = request.data['routes']).exists()
            if route_exists:
                data = {'data':'Route is already assigned to this van'}
                return Response(data,status=status.HTTP_200_OK)
            else :
                user=CustomUser.objects.get(username=username)
                new_route = serializer.save(created_by=user.id)
                log_activity(
                    created_by=user.id,
                    description=f"Route '{new_route.routes.route_name}' assigned to van '{van_data.van_make}' by {username}."
                    )
                data = {'data':'Route is assigned'}
                return Response(data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, id):
        try:
            # Retrieve the object to be deleted
            instance = Van_Routes.objects.get(van_route_id=id)
            instance_name = instance.routes.route_name 
            instance.delete()

            log_activity(
                created_by=request.user.id,
                description=f"Route '{instance_name}' deleted."
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Van_Routes.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)



class Licence_API(APIView):
    serializer_class=Van_LicenseSerializers
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self,request):
        queryset = Van_License.objects.all()
        serializer = Van_LicenseSerializers(queryset,many=True)
        return Response(serializer.data)

    def post(self,request):
        van_data = Van.objects.get(van_id = request.data['van'])
        serializer=Van_LicenseSerializers(data=request.data)
        if serializer.is_valid():
            licence_exists = Van_License.objects.filter(van = van_data,emirate = request.data['emirate']).exists()
            if licence_exists:
                data = {'data':'Licence is already assigned to this van from this emirate'}
                return Response(data,status=status.HTTP_200_OK)
            else :
                van_data = serializer.save(created_by=request.user.id)
                log_activity(
                    created_by=request.user.id,
                    description=f"Licence created for van '{van_data.van.van_make}' from emirate '{request.data['emirate']}'."
                    )
                data = {'data':'Licence is created'}
                return Response(data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, id):
        try:
            # Retrieve the object to be deleted
            instance = Van_License.objects.get(van_route_id=id)
            instance_name = instance.emirate.name 
            instance.delete()

            log_activity(
                created_by=request.user.id,
                description=f"Licence for emirate '{instance_name}' deleted."
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Van_License.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)



#  Trip Schedule
def find_customers(request, def_date, route_id):
    from datetime import datetime
    date_str = def_date
    if date_str:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        day_of_week = date.strftime('%A')
        week_num = (date.day - 1) // 7 + 1
        week_number = f'Week{week_num}'
    
    route = get_object_or_404(RouteMaster, route_id=route_id)

    van_route = Van_Routes.objects.filter(routes=route).first()
    van_capacity = van_route.van.capacity if van_route else 200
    
    vocation_customer_ids = Vacation.objects.filter(start_date__gte=date,end_date__lte=date).values_list('customer__pk')
    
    todays_customers = []
    buildings = []
    for customer in Customers.objects.filter(routes=route,is_calling_customer=False).exclude(pk__in=vocation_customer_ids):
        if customer.visit_schedule:
            for day, weeks in customer.visit_schedule.items():
                if day in str(day_of_week) and week_number in str(weeks):
                    todays_customers.append(customer)
                    buildings.append(customer.building_name)
    # log_activity(f"Found {len(todays_customers)} customers for the day: {date_str} on route: {route.route_name}.")                    
    # Emergency customers
    special_customers = DiffBottlesModel.objects.filter(delivery_date=date)
    emergency_customers = []
    for client in special_customers:
        if client.customer in todays_customers:
            emergency_customers.append(client.customer)
        else:
            if client.customer.routes == route:
                todays_customers.append(client.customer)
                emergency_customers.append(client.customer)
                if client.customer.building_name not in buildings:
                    buildings.append(client.customer.building_name)
    
    # Calculate total bottle count
    co = sum(cus.no_of_bottles_required or 0 for cus in todays_customers)

    # print(f"Total bottle count: {co}, Van capacity: {van_capacity}")

    if buildings:
        building_count = {}
        for building in buildings:
            for customer in todays_customers:
                if customer.building_name == building:
                    no_of_bottles = customer.no_of_bottles_required or 0  # Use 0 if no_of_bottles_required is None
                    building_count[building] = building_count.get(building, 0) + no_of_bottles

        building_gps = []
        for building, bottle_count in building_count.items():
            c = Customers.objects.filter(building_name=building, routes=route).first()
            building_gps.append((building, c.gps_longitude, c.gps_latitude, bottle_count))

        # Sort buildings by GPS coordinates
        sorted_building_gps = sorted(building_gps, key=lambda x: (x[1] if x[1] is not None else '', x[2] if x[2] is not None else ''))
        sorted_buildings = [item[0] for item in sorted_building_gps]

        # Check if total bottle count exceeds van capacity
        if co <= van_capacity:
            # All buildings can fit into one trip
            trips = {"Trip1": sorted_buildings}
        else:
            # Initialize trips
            trips = {}
            trip_count = 1
            current_trip_bottle_count = 0
            trip_buildings = []

            for building in sorted_buildings:
                bottle_count = building_count[building]
                # print(f"Processing building: {building}, Bottle count: {bottle_count}, Current trip bottle count: {current_trip_bottle_count}")

                if current_trip_bottle_count + bottle_count > van_capacity:
                    # print(f"Creating new trip. Current trip bottle count ({current_trip_bottle_count}) + bottle count ({bottle_count}) exceeds van capacity ({van_capacity}).")
                    trips[f"Trip{trip_count}"] = trip_buildings
                    trip_count += 1
                    trip_buildings = [building]
                    current_trip_bottle_count = bottle_count
                else:
                    trip_buildings.append(building)
                    current_trip_bottle_count += bottle_count

            if trip_buildings:
                trips[f"Trip{trip_count}"] = trip_buildings

            # Merge trips if possible to optimize
            merging_occurred = True
            while merging_occurred:
                merging_occurred = False
                for trip_num in range(1, trip_count):
                    for other_trip_num in range(trip_num + 1, trip_count + 1):
                        trip_key = f"Trip{trip_num}"
                        other_trip_key = f"Trip{other_trip_num}"
                        if trip_key in trips and other_trip_key in trips:
                            combined_buildings = trips[trip_key] + trips[other_trip_key]
                            total_bottles = sum(building_count.get(building, 0) for building in combined_buildings)
                            if total_bottles <= van_capacity:
                                # print(f"Merging trips {trip_key} and {other_trip_key}. Combined bottle count: {total_bottles}")
                                trips[trip_key] = combined_buildings
                                del trips[other_trip_key]
                                trip_count -= 1
                                merging_occurred = True
                                break
                    if merging_occurred:
                        break

        # List to store trip-wise customer details
        trip_customers = []
        for trip, buildings in trips.items():
            for building in buildings:
                for customer in todays_customers:
                    if customer.building_name == building:
                        trip_customer = {
                            "customer_id": customer.customer_id,
                            "custom_id": customer.custom_id,
                            "customer_name": customer.customer_name,
                            "mobile": customer.mobile_no,
                            "trip": trip,
                            "building": customer.building_name,
                            "route": customer.routes.route_name,
                            "no_of_bottles": customer.no_of_bottles_required,
                            "location": customer.location.location_name if customer.location else "",
                            "door_house_no": customer.door_house_no,
                            "floor_no": customer.floor_no,
                            "gps_longitude": customer.gps_longitude,
                            "gps_latitude": customer.gps_latitude,
                            "customer_type": customer.sales_type,
                        }
                        if customer in emergency_customers:
                            trip_customer['type'] = 'Emergency'
                            dif = DiffBottlesModel.objects.filter(customer=customer, delivery_date=date).latest('created_date')
                            trip_customer['no_of_bottles'] = dif.quantity_required
                        else:
                            trip_customer['type'] = 'Default'
                        if customer.sales_type in ['CASH', 'CREDIT']:
                            trip_customer['rate'] = customer.rate

                        trip_customers.append(trip_customer)
        # log_activity(f"Created trip details for {len(trip_customers)} customers.")     
        return trip_customers

# def find_customers(request, def_date, route_id):
#     from datetime import datetime
#     date_str = def_date
#     if date_str:
#         date = datetime.strptime(date_str, '%Y-%m-%d')
#         day_of_week = date.strftime('%A')
#         week_num = (date.day - 1) // 7 + 1
#         week_number = f'Week{week_num}'
    
#     route = get_object_or_404(RouteMaster, route_id=route_id)

#     van_route = Van_Routes.objects.filter(routes=route).first()
#     van_capacity = van_route.van.capacity if van_route else 200
    
#     todays_customers = []
#     buildings = []
#     for customer in Customers.objects.filter(routes=route):
#         if customer.visit_schedule:
#             for day, weeks in customer.visit_schedule.items():
#                 if day in str(day_of_week) and week_number in str(weeks):
#                     todays_customers.append(customer)
#                     buildings.append(customer.building_name)
                        
#     # Customers on vacation
#     date = datetime.strptime(def_date, '%Y-%m-%d').date()
#     for vacation in Vacation.objects.all():
#         if vacation.start_date <= date <= vacation.end_date:
#             if vacation.customer in todays_customers:
#                 todays_customers.remove(vacation.customer)
   
#     # Emergency customers
#     special_customers = DiffBottlesModel.objects.filter(delivery_date=date)
#     emergency_customers = []
#     emergency_customers_dict = {}
#     for client in special_customers:
#         if client.customer in todays_customers:
#             emergency_customers.append(client.customer)
#             # Update bottle count for the existing customer
#             client.customer.no_of_bottles_required += client.quantity_required
#         else:
#             if client.customer.routes == route:
#                 todays_customers.append(client.customer)
#                 emergency_customers.append(client.customer)
#                 if client.customer.building_name not in buildings:
#                     buildings.append(client.customer.building_name)
#             emergency_customers_dict[client.customer.customer_id] = client.quantity_required
    
#     # Calculate total bottle count
#     co = sum(cus.no_of_bottles_required or 0 for cus in todays_customers)

#     if buildings:
#         building_count = {}
#         for building in buildings:
#             for customer in todays_customers:
#                 if customer.building_name == building:
#                     no_of_bottles = customer.no_of_bottles_required or 0
#                     building_count[building] = building_count.get(building, 0) + no_of_bottles

#         building_gps = []
#         for building, bottle_count in building_count.items():
#             c = Customers.objects.filter(building_name=building, routes=route).first()
#             building_gps.append((building, c.gps_longitude, c.gps_latitude, bottle_count))

#         sorted_building_gps = sorted(building_gps, key=lambda x: (x[1] if x[1] is not None else '', x[2] if x[2] is not None else ''))
#         sorted_buildings = [item[0] for item in sorted_building_gps]

#         if co <= van_capacity:
#             trips = {"Trip1": sorted_buildings}
#         else:
#             trips = {}
#             trip_count = 1
#             current_trip_bottle_count = 0
#             trip_buildings = []

#             for building in sorted_buildings:
#                 bottle_count = building_count[building]
#                 if current_trip_bottle_count + bottle_count > van_capacity:
#                     trips[f"Trip{trip_count}"] = trip_buildings
#                     trip_count += 1
#                     trip_buildings = [building]
#                     current_trip_bottle_count = bottle_count
#                 else:
#                     trip_buildings.append(building)
#                     current_trip_bottle_count += bottle_count

#             if trip_buildings:
#                 trips[f"Trip{trip_count}"] = trip_buildings

#             merging_occurred = True
#             while merging_occurred:
#                 merging_occurred = False
#                 for trip_num in range(1, trip_count):
#                     for other_trip_num in range(trip_num + 1, trip_count + 1):
#                         trip_key = f"Trip{trip_num}"
#                         other_trip_key = f"Trip{other_trip_num}"
#                         if trip_key in trips and other_trip_key in trips:
#                             combined_buildings = trips[trip_key] + trips[other_trip_key]
#                             total_bottles = sum(building_count.get(building, 0) for building in combined_buildings)
#                             if total_bottles <= van_capacity:
#                                 trips[trip_key] = combined_buildings
#                                 del trips[other_trip_key]
#                                 trip_count -= 1
#                                 merging_occurred = True
#                                 break
#                     if merging_occurred:
#                         break
                    
#         trip_customers=[]
#         for trip, buildings in trips.items():
#             for building in buildings:
#                 for customer in todays_customers:
#                     if customer.building_name == building:
#                         trip_customer = {
#                             "customer_id": customer.customer_id,
#                             "custom_id": customer.custom_id,
#                             "customer_name": customer.customer_name,
#                             "mobile": customer.mobile_no,
#                             "trip": trip,
#                             "building": customer.building_name,
#                             "route": customer.routes.route_name,
#                             # Initially set the bottle count to the default value
#                             "no_of_bottles": customer.no_of_bottles_required,
#                             "location": customer.location.location_name if customer.location else "",
#                             "door_house_no": customer.door_house_no,
#                             "floor_no": customer.floor_no,
#                             "gps_longitude": customer.gps_longitude,
#                             "gps_latitude": customer.gps_latitude,
#                             "customer_type": customer.sales_type,
#                         }
                        
#                         if customer in emergency_customers:
#                             trip_customer['type'] = 'Emergency'
#                             # Override the bottle count to show only the emergency order count
#                             trip_customer['no_of_bottles'] = emergency_customers_dict[customer.customer_id]
#                         else:
#                             trip_customer['type'] = 'Default'
                        
#                         if customer.sales_type in ['CASH', 'CREDIT']:
#                             trip_customer['rate'] = customer.rate

#                         trip_customers.append(trip_customer)


#         return trip_customers




class ScheduleView(APIView):
    def get(self, request, date_str):
        if date_str:
            date = datetime.strptime(date_str, '%Y-%m-%d')
        else:
            return Response({'error': 'Date parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        routes = RouteMaster.objects.all()
        route_details = []
        for route in routes:
            trip_count = 0
            customer_count = 0
            bottle_count=0
            todays_customers = find_customers(request, date_str, route.route_id)
            trips=[]
            for customer in todays_customers:
                customer_count+=1
                bottle_count+=customer['no_of_bottles']
                if customer['trip'] not in trips:
                    trips.append(customer['trip'])
            route_details.append({
                'route_name':route.route_name,
                'route_id':route.route_id,
                'no_of_customers':customer_count,
                'no_of_bottles':bottle_count,
                'no_of_trips':len(trips),
                'trips': trips
            })
        return Response({'def_date': date_str, 'details': route_details}, status=status.HTTP_200_OK)


class ScheduleByRoute(APIView):
    def get(self, request, date_str, route_id, trip):
        route = RouteMaster.objects.get(route_id=route_id)
        todays_customers = find_customers(request, date_str, route_id)
        customers = [customer for customer in todays_customers if customer['trip'] == trip]
        return Response({
            'def_date': date_str,
            'route': {
                'route_id': route.route_id,
                'route_name': route.route_name,
                'trip' : trip
            },
            'todays_customers': customers,
        }, status=status.HTTP_200_OK)

# Expense

class ExpenseHeadListAPI(APIView):
    def get(self, request):
        expense_heads = ExpenseHead.objects.all()
        serializer = ExpenseHeadSerializer(expense_heads, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ExpenseHeadSerializer(data=request.data)
        if serializer.is_valid():
            expense_head = serializer.save()
            log_activity(
                created_by=request.user.id,  
                description=f'Created expense head: {expense_head.name}' 
            )
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ExpenseHeadDetailAPI(APIView):
    def get_object(self, pk):
        try:
            return ExpenseHead.objects.get(pk=pk)
        except ExpenseHead.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        expense_head = self.get_object(pk)
        serializer = ExpenseHeadSerializer(expense_head)
        return Response(serializer.data)

    def put(self, request, pk):
        expense_head = self.get_object(pk)
        serializer = ExpenseHeadSerializer(expense_head, data=request.data)
        if serializer.is_valid():
            updated_expense_head = serializer.save()
            log_activity(
                created_by=request.user.id,  
                description=f'Updated expense head: {updated_expense_head.name}'
            )
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        expense_head = self.get_object(pk)
        expense_head_name = expense_head.name  
        expense_head.delete()
        log_activity(
            created_by=request.user.id,  
            description=f'Deleted expense head: {expense_head_name}' 
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

class ExpenseListAPI(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        date = request.GET.get('date')
        if date:
            date = datetime.strptime(date, '%Y-%m-%d').date()
        else:
            date = datetime.today().date()
        
        van_route = Van_Routes.objects.get(van__salesman=request.user,expense_date=date)
        expenses = Expense.objects.filter(route=van_route.routes,van=van_route.van)
        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data)

    def post(self, request):
        try:
            van_route = Van_Routes.objects.get(van__salesman=request.user)
        except Van_Routes.DoesNotExist:
            return Response({"detail": "Van route not found."}, status=status.HTTP_404_NOT_FOUND)
        
        expense_type_id = request.data.get('expence_type')
        amount = request.data.get('amount')
        remarks = request.data.get('remarks', '')
        expense_date = request.data.get('expense_date')

        if not all([expense_type_id, amount, expense_date]):
            return Response({"detail": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            expense_type = ExpenseHead.objects.get(pk=expense_type_id)
        except ObjectDoesNotExist:
            return Response({"detail": "Expense type not found."}, status=status.HTTP_404_NOT_FOUND)

        expense = Expense(
            expence_type=expense_type,
            route=van_route.routes,
            van=van_route.van,
            amount=amount,
            remarks=remarks,
            expense_date=expense_date
        )

        expense.save()
        
        log_activity(
            created_by=request.user.id,  
            description=f'Created expense of type {expense_type.name} with amount {amount}' 
        )

        # Serialize the saved expense instance for the response
        serializer = ExpenseSerializer(expense)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ExpenseDetailAPI(APIView):
    def get(self, request, expense_id):
        expense = Expense.objects.get(expense_id = expense_id)
        serializer = ExpenseSerializer(expense)
        return Response(serializer.data)

    def put(self, request, expense_id):
        expense = Expense.objects.get(expense_id = expense_id)
        serializer = ExpenseSerializer(expense, data=request.data)
        if serializer.is_valid():
            serializer.save()
            log_activity(
                created_by=request.user.id, 
                description=f'Updated expense ID {expense_id} with new data: {serializer.validated_data}'  
            )
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, expense_id):
        expense = Expense.objects.get(expense_id = expense_id)
        expense.delete()
        log_activity(
            created_by=request.user.id, 
            description=f'Deleted expense ID {expense_id}' 
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

 ####################################Order####################################

# Reason
class ChangeReasonListAPI(APIView):
    def get(self, request):
        change_reason = Change_Reason.objects.all()
        serializer = ChangeReasonSerializer(change_reason, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ChangeReasonSerializer(data=request.data)
        if serializer.is_valid():
            change_reason = serializer.save()
            log_activity(
                created_by=request.user.id,  
                description=f'Created a new change reason: {change_reason.reason_name}' 
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangeReasonDetailAPI(APIView):
    def get(self, request, change_reason_id):
        change_reason = Change_Reason.objects.get(id = change_reason_id)
        serializer = ChangeReasonSerializer(change_reason)
        return Response(serializer.data)

    def put(self, request, change_reason_id):
        change_reason = Change_Reason.objects.get(id = change_reason_id)
        serializer = ChangeReasonSerializer(change_reason, data=request.data)
        if serializer.is_valid():
            serializer.save()
            log_activity(
                created_by=request.user.id, 
                description=f'Updated change reason: {change_reason.reason_name}' 
            )
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, change_reason_id):
        change_reason = Change_Reason.objects.get(id = change_reason_id)
        change_reason.delete()
        log_activity(
            created_by=request.user.id, 
            description=f'Deleted change reason : {change_reason.reason_name}'
        )
        return Response(status=status.HTTP_204_NO_CONTENT)





# order Change
class OrderChangeListAPI(APIView):
    def get(self, request):
        order_change = Order_change.objects.all()
        serializer = OrderChangeSerializer(order_change, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = OrderChangeSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid():
            order_change_instance = serializer.save()
            log_activity(
                created_by=request.user.id,  
                description=f'Created new order change: {order_change_instance}'  
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from uuid import UUID
class OrderChangeDetailAPI(APIView):
    def get_object(self, order_change_id):
        try:
            return Order_change.objects.get(order_change_id=order_change_id)
        except Order_change.DoesNotExist:
            raise Http404

    def get(self, request, order_change_id):
        order_change = self.get_object(order_change_id)
        serializer = OrderChangeSerializer(order_change)
        return Response(serializer.data)

    def put(self, request, order_change_id):
        order_change = self.get_object(order_change_id)  
        serializer = OrderChangeSerializer(order_change, data=request.data, partial=True)
        print(request.data)
        if serializer.is_valid():  
            updated_order_change_instance = serializer.save()  
            log_activity(
                created_by=request.user.id,  
                description=f'Updated order change: {updated_order_change_instance}'  
            )
            return Response(serializer.data)  
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

    def delete(self, request, order_change_id):
        order_change = self.get_object(order_change_id)
        order_change.delete()
        log_activity(
            created_by=request.user.id,  
            description=f'Deleted order change: {order_change}'  
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

# Return
class OrderReturnListAPI(APIView):
    def get(self, request):
        order_retrn = Order_return.objects.all()
        serializer = OrderReturnSerializer(order_retrn, many=True)
        print(serializer.data)
        return Response(serializer.data)

    def post(self, request):
        serializer = OrderReturnSerializer(data=request.data)
        if serializer.is_valid():
            order_return_instance = serializer.save()
            log_activity(
                created_by=request.user.id,  
                description=f'Created order return: {order_return_instance}' 
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderReturnDetailAPI(APIView):
    def get_object(self, order_return_id):
        try:
            return Order_return.objects.get(order_return_id=order_return_id)
        except Order_return.DoesNotExist:
            raise Http404

    def get(self, request, order_return_id):
        order_return = self.get_object(order_return_id)
        serializer = OrderReturnSerializer(order_return)
        return Response(serializer.data)

    def put(self, request, order_return_id):
        order_return = self.get_object(order_return_id)
        serializer = OrderReturnSerializer(order_return, data=request.data, partial=True)
        if serializer.is_valid():
            updated_order_return_instance = serializer.save()
            log_activity(
                created_by=request.user.id, 
                description=f'Updated order return: {updated_order_return_instance}' 
            )
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, order_return_id):
        order_return = self.get_object(order_return_id)
        order_return.delete()
        log_activity(
            created_by=request.user.id, 
            description=f'Deleted order return: {order_return}'
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

####################################Account####################################


class UserSignUpView(APIView):

    serializer_class=CustomUserSerializers
    def get(self, request,id=None):
        if id :
            queryset=Customers.objects.get(customer_id=id)
            serializer=CustomersSerializers(queryset)
            log_activity(
                created_by=request.user.id,
                description=f"Fetched details for customer {queryset.customer_name}"
            )
            return Response(serializer.data)
        queryset = CustomUser.objects.all()
        serializer = CustomUserSerializers(queryset,many=True)
        log_activity(
            created_by=request.user.id,
            description="Fetched all users"
        )
        return Response({'data':serializer.data})

    def post(self, request, *args, **kwargs):
        serializer=CustomUserSerializers(data=request.data)
        if serializer.is_valid():

            passw = make_password(request.data['password'])
            user_instance = serializer.save(password=passw)
            log_activity(
                created_by=request.user.id,
                description=f"Registered new user: {user_instance}"
            )
            data = {'data':"Succesfully registerd"}
            return Response(data,status=status.HTTP_201_CREATED)
        else:
            data={'data':serializer.errors}
            return Response(data,status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        product = CustomUser.objects.get(id=id)
        serializer = CustomUserSerializers(product, data=request.data)
        if serializer.is_valid():
            serializer.save(modified_by=request.user.id,modified_date = datetime.now())
            log_activity(
                created_by=request.user.id,
                description=f"Updated user details for ID {id}"
            )
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

#--------------------------------------Sign Up Api--------------------------------------#

class Customer_API(APIView):
    serializer_class = CustomersSerializers
    permission_classes = [IsAuthenticated]
    authentication_classes = [BasicAuthentication]

    def get(self, request, id=None):
        try:
            if id:
                queryset = Customers.objects.get(customer_id=id)
                serializer = CustomersSerializers(queryset)
                log_activity(
                    created_by=request.user.id,
                    description=f"Fetched details for customer  {queryset.customer_name}"
                )
                return Response(serializer.data, status=status.HTTP_200_OK)
            queryset = Customers.objects.all()
            serializer = CustomersSerializers(queryset, many=True)
            log_activity(
                created_by=request.user.id,
                description="Fetched all customers"
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Customers.DoesNotExist:
            return Response({'status': False, 'message': 'Customer not found!'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # print(e)
            return Response({'status': False, 'message': 'Something went wrong!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            serializer = CustomersCreateSerializers(data=request.data)
            if serializer.is_valid(raise_exception=True):
                if request.data["mobile_no"] and Customers.objects.filter(mobile_no=request.data["mobile_no"]).exists():
                    return Response({'data': 'Customer with this mobile number already exists! Try another number'}, status=status.HTTP_400_BAD_REQUEST)
                
                if request.data["email_id"] and Customers.objects.filter(email_id=request.data["email_id"]).exists():
                    return Response({'data': 'Customer with this Email Id already exists! Try another Email Id'}, status=status.HTTP_400_BAD_REQUEST)
                
                if request.data["mobile_no"]:
                    username = request.data["mobile_no"]
                    password = request.data["password"]
                    hashed_password = make_password(password)
                    
                    customer_data = CustomUser.objects.create(
                        password=hashed_password,
                        username=username,
                        first_name=request.data['customer_name'],
                        email=request.data['email_id'],
                        user_type='Customer'
                    )

                data = serializer.save(
                    custom_id=get_custom_id(Customers)
                )
                
                if request.data["mobile_no"]:
                    data.user_id = customer_data
                    data.save()
                    
                Staff_Day_of_Visit.objects.create(customer=data)
                log_activity(
                    created_by=request.user.id,
                    description=f"Added new customer {data.customer_name}"
                )
                return Response({'data': 'Successfully added'}, status=status.HTTP_201_CREATED)
            return Response({'status': False, 'data': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            if CustomUser.objects.filter(username=request.data['mobile_no']).exists():
                user_obj = CustomUser.objects.get(username=request.data['mobile_no'])
                user_obj.delete()
            print(e)
            return Response({'status': False, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, id):
        try:
            customer = Customers.objects.get(customer_id=id)
            serializer = CustomersCreateSerializers(customer, data=request.data)
            if serializer.is_valid():
                log_activity(
                    created_by=request.user.id,
                    description=f"Updated customer details for {customer.customer_name}"
                )
                serializer.save(modified_by=request.user.id, modified_date=datetime.now())
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Customers.DoesNotExist:
            return Response({'status': False, 'message': 'Customer not found!'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return Response({'status': False, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class Customer_Custody_Item_API(APIView):
    serializer_class = CustomerCustodyItemSerializers
    def get(self,request):
        customer = request.data['customer_id']
        custodyitems = CustodyCustomItems.objects.filter(customer=customer).all()
        cus_list=list(custodyitems)
        customerser=CustomerCustodyItemSerializers(cus_list,many=True).data
        
        log_activity(
            created_by=request.user.id,
            description=f"Fetched custody items for customer  {custodyitems.custody_custom.customer.customer_name}"
        )
        return JsonResponse({'customerser':customerser})


#############-------------- Coupon Management ----------------#########################

class CouponType_API(APIView):
    serializer_class = couponTypeserializers
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self,request):
        queryset = CouponType.objects.all()
        serializer = couponTypeserializers(queryset,many=True)
        log_activity(
            created_by=request.user.id,
            description="Retrieved all coupon types"
        )
        return Response(serializer.data)

    def post(self,request):
        couponType_data = CouponType.objects.filter(coupon_type_id = request.data['coupon_type_id'])
        for i in couponType_data:
            coupontypedata=i.coupon_type_id
        serializer=couponTypeCreateserializers(data=request.data)
        if serializer.is_valid():
            coupon_Typess = CouponType.objects.filter(coupon_type_id = coupontypedata).exists()
            if coupon_Typess:
                data = {'data':'CouponType already created'}
                return Response(data,status=status.HTTP_200_OK)
            else :
                serializer.save(created_by=request.user.id)
                log_activity(
                    created_by=request.user.id,
                    description=f"Created a new coupon type with ID {serializer.data['coupon_type_id']}"
                )
                data = {'data':'Coupon Type created successfully!'}
                return Response(data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
            coupon_TYPE = CouponType.objects.get(coupon_type_id=id)
            serializer = couponTypeCreateserializers(coupon_TYPE, data=request.data)
            if serializer.is_valid():
                serializer.save(modified_by=request.user.id,modified_date = datetime.now())
                log_activity(
                    created_by=request.user.id,
                    description=f"Updated coupon type with ID {id}"
                )
                return Response(serializer.data,status=status.HTTP_200_OK)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            # Retrieve the object to be deleted
            instance = CouponType.objects.get(coupon_type_id=id)
            instance.delete()
            log_activity(
                created_by=request.user.id,
                description=f"Deleted coupon type with ID {id}"
            )
            data={"data":"successfully deleted"}
            return Response(data,status=status.HTTP_204_NO_CONTENT)
        except CouponType.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class Coupon_API(APIView):
    serializer_class = couponserializers
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self,request):
        queryset = Coupon.objects.all()
        serializer = couponserializers(queryset,many=True)
        log_activity(
            created_by=request.user.id,
            description="Retrieved all coupons"
        )
        return Response(serializer.data)

    def post(self,request):
        coupon_data = Coupon.objects.filter(coupon_id = request.data['coupon_id'])
        for i in coupon_data:
            coupondata=i.coupon_id
        serializer=couponserializers(data=request.data)
        if serializer.is_valid():
            coupon= Coupon.objects.filter(coupon_id = coupondata).exists()
            if coupon:
                data = {'data':'Coupon already created'}
                return Response(data,status=status.HTTP_200_OK)
            else :
                serializer.save(created_by=request.user.id)
                log_activity(
                    created_by=request.user.id,
                    description=f"Created a new coupon with ID {serializer.data['coupon_id']}"
                )
                data = {'data':'Coupon created successfully!'}
                return Response(data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        coupon = Coupon.objects.get(coupon_id=id)
        serializer = couponTypeserializers(coupon, data=request.data)
        if serializer.is_valid():
            serializer.save(modified_by=request.user.id,modified_date = datetime.now())
            log_activity(
                    created_by=request.user.id,
                    description=f"Updated coupon with ID {id}"
                )
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            # Retrieve the object to be deleted
            instance = Coupon.objects.get(coupon_id=id)
            instance.delete()
            log_activity(
                created_by=request.user.id,
                description=f"Deleted coupon with ID {id}"
            )
            data={"data":"successfully deleted"}

            return Response(data,status=status.HTTP_204_NO_CONTENT)
        except Coupon.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class CouponRequest_API(APIView):
    serializer_class = couponRequestserializers
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self,request):
            queryset = CouponRequest.objects.all()
            serializer = couponRequestserializers(queryset,many=True)
            log_activity(
                created_by=request.user.id,
                description="Retrieved all coupon requests"
            )
            return Response(serializer.data)
    def post(self,request):
        print("HIIIIIIIIIIIIIIII",request.data)
        quantity = request.data.get('quantity')
        print("quantity",quantity)
        coupon_type_id = request.data.get('coupon_type_id')
        print("coupon_type_id",coupon_type_id)

        # Create a dictionary with the required data
        data = {
            'quantity': quantity,
            'coupon_type_id': coupon_type_id,
        }
        log_activity(
            created_by=request.user.id,
            description=f"Attempting to create a coupon request with quantity {quantity} and coupon_type_id {coupon_type_id}"
        )
        # Use the serializer to create a new CouponRequest instance
        serializer=couponRequestserializers(data=request.data)
        print("serializerDATAAAAAAAAAAAAA",serializer)
        if serializer.is_valid():
            # Check if a CouponRequest with the same quantity and coupon_type_id already exists
            coupon_request_exists = CouponRequest.objects.filter(quantity=quantity, coupon_type_id=coupon_type_id).exists()

            if coupon_request_exists:
                log_activity(
                    created_by=request.user.id,
                    description=f"Duplicate coupon request with quantity {quantity} and coupon_type_id {coupon_type_id} found"
                )
                data = {'detail': 'CouponRequest already exists with the same quantity and coupon_type_id.'}
                return Response(data, status=status.HTTP_200_OK)
            else:
                # Save the new CouponRequest
                serializer.save()
                log_activity(
                    created_by=request.user.id,
                    description=f"Created new coupon request with quantity {quantity} and coupon_type_id {coupon_type_id}"
                )
                data = {'detail': 'CouponRequest created successfully!'}
                return Response(data, status=status.HTTP_201_CREATED)
        else:
            log_activity(
                created_by=request.user.id,
                description=f"Failed to create coupon request due to validation errors: {serializer.errors}"
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AssignStaffCoupon_API(APIView):
    serializer_class = assignStaffCouponserializers
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self,request):
            queryset = AssignStaffCoupon.objects.all()
            serializer = assignStaffCouponserializers(queryset,many=True)
            return Response(serializer.data)
    def post(self,request):

        alloted_quantity = Decimal(request.data.get('alloted_quantity', 0))
        coupon_request=request.data.get('coupon_request')
        coupon_request_data = CouponRequest.objects.values('quantity').get(coupon_request_id=coupon_request)
        quantity = Decimal(coupon_request_data['quantity'])
        remaining_quantity=quantity- alloted_quantity


        data ={
           "alloted_quantity":alloted_quantity ,
           "quantity":quantity,
           'remaining_quantity': Decimal(coupon_request_data['quantity']) - Decimal(request.data.get('alloted_quantity', 0)),
           'status': 'Pending' if remaining_quantity > 0 else 'Closed',
           'coupon_request':coupon_request,
           'created_by': str(request.user.id),
           'modified_by': str(request.user.id),
           'modified_date': datetime.now(),
           'created_date': datetime.now()

        }


        serializer=assignStaffCouponserializers(data=data)
        if serializer.is_valid():
            # Check if a CouponRequest with the same quantity and coupon_type_id already exists
            assignstaff = AssignStaffCoupon.objects.filter(alloted_quantity=alloted_quantity, coupon_request=coupon_request).exists()

            if assignstaff:
                data = {'detail': ' already exists '}
                return Response(data, status=status.HTTP_200_OK)
            else:
                # Save the new CouponRequest
                serializer.save()
                data = {'detail': ' created successfully!'}
                log_activity(
                    created_by=request.user.id,
                    description="Assigned staff coupon created"
                )
                return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AssigntoCustomer_API(APIView):
    # authentication_classes = [BasicAuthentication]
    # permission_classes = [IsAuthenticated]
    serializers = assigncustomerCouponserializers
    def get(self,request):
            queryset = AssignStaffCouponDetails.objects.all()
            serializer = assigncustomerCouponserializers(queryset,many=True)
            return Response(serializer.data)
    def post(self,request):
        print("DATA",request.data)
        staff_coupon_assign=request.data.get('staff_coupon_assign')
        print("staff_coupon_assign",staff_coupon_assign)

        to_customer=request.data.get('to_customer')
        print("to_customer",to_customer)
        coupon=request.data.get('coupon')
        print("coupon",coupon)

        assign_staff_coupon_instance = AssignStaffCoupon.objects.get(assign_id=staff_coupon_assign)
        print("assign_staff_coupon_instance",assign_staff_coupon_instance)
        if to_customer:
            status_value = 'Assigned To Customer'
        else:
            if assign_staff_coupon_instance.status == 'Closed':
                status_value = 'Assigned To Staff'
            else:
                status_value = 'Pending'
        print("status_value",status_value)
        initial_status = status_value  # Set the initial status value

        data ={
            'staff_coupon_assign':staff_coupon_assign,
            'to_customer':to_customer,
            'created_by': str(request.user.id),
            'modified_by': str(request.user.id),
            'modified_date': datetime.now(),
            'created_date': datetime.now(),
            'status':status_value


        }
        serializer=assigncustomerCouponserializers(data=data,initial={'status': initial_status})
        if serializer.is_valid():
                # Save the new CouponRequest
                serializer.save()
                data = {'detail': ' created successfully!'}
                log_activity(
                    created_by=request.user.id,
                    description=f"Coupon assigned to customer with status: {status_value}"
                )
                return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#------------------------------------Attendance Log------------------------------------#

class PunchIn_Api(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializers = Attendance_Serializers

    def post(self, request, *args, **kwargs):
        try:
            userid = request.data["id"]
            staff = CustomUser.objects.get(id=userid)
            check_already_logged = Attendance_Log.objects.filter(staff=staff, punch_in_date=date.today())
            if len(check_already_logged) >= 1:
                return Response({'status': False, 'message': 'Already Logged In!'})
            else:
                data = Attendance_Log.objects.create(staff=staff, created_by=staff.first_name)
                return_data = Attendance_Log.objects.filter(attendance_id=data.attendance_id).select_related('staff')
                result = self.serializers(return_data, many=True)
                log_activity(
                    created_by=staff.id,
                    description=f"{staff.first_name} punched in at {data.punch_in_time}"
                )
                return Response({'status': True, 'data': result.data, 'message': 'Successfully Logged In!'})
        except Exception as e:
            print(e)
            return Response({'status': False, 'message': 'Something went wrong!'})


class PunchOut_Api(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializers = Attendance_Serializers

    def post(self, request, *args, **kwargs):
        try:
            userid = request.data["id"]
            staff = CustomUser.objects.get(id=userid)
            Attendance_Log.objects.filter(staff=staff, punch_in_date=datetime.now().date()).update(
                staff=staff,
                created_by=staff.first_name,
                punch_out_date=datetime.now().date(),
                punch_out_time=datetime.now().time())
            return_data = Attendance_Log.objects.filter(punch_out_date=datetime.now().date()).select_related('staff')
            result = self.serializers(return_data, many=True)
            log_activity(
                created_by=staff.id,
                description=f"{staff.first_name} punched out at {datetime.now().time()}"
            )
            return Response({'status': True, 'data': result.data, 'message': 'Successfully Logged In!'})
        except Exception as e:
            print(e)
            return Response({'status': False, 'message': 'Something went wrong!'})

#----------------------------------------Customer --------------------------------------------#

@api_view(['GET'])
def location_based_on_emirates(request):
    emirate = request.query_params.get('emirate', None)
    if emirate is None:
        return Response({'error': 'Emirate parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
    location_list = LocationMaster.objects.filter(emirate=emirate).all()
    locations = LocationMasterSerializers(location_list, many=True).data
    log_activity(
        created_by=request.user.id,
        description=f"Retrieved locations for emirate: {emirate}"
    )
    return Response({'locations': locations})

@api_view(['GET'])
def emirates_based_locations(request):
    branch_id = ""
    if request.GET.get('branch_id'):
        branch_id = request.GET.get('branch_id')
        
    instances = EmirateMaster.objects.all()
    serialized_data = EmiratesBasedLocationsSerializers(instances, many=True, context={'branch_id': branch_id}).data
    
    log_activity(
        created_by=request.user.id,
        description=f"Retrieved locations for branch_id: {branch_id}"
    )
    
    return Response({
        'status': True, 
        'data': serialized_data,
        'message': 'Success'
        })

class Route_Assign_Staff_Api(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = Staff_Assigned_Route_Details_Serializer

    def post(self, request, *args, **kwargs):
        # try:
            userid = request.data["id"]
            staff = CustomUser.objects.get(id=userid)
            vans = Van.objects.filter(Q(driver=staff) | Q(salesman=staff)).first()
            if vans is not None:
                van = Van.objects.get(van_id=vans.pk)
                assign_routes = Van_Routes.objects.filter(van=van).values_list('routes', flat=True)
                routes_list = RouteMaster.objects.filter(route_id__in = assign_routes)
                serializer = self.serializer_class(routes_list, many=True)
                data = {
                    'id':staff.id,
                    'staff':staff.first_name,
                    'van_id':van.van_id,
                    'van_name':van.van_make,
                    'branch':van.branch_id.name,
                    'branch_id':van.branch_id.branch_id,
                    'assigned_routes':serializer.data
                }
                log_activity(
                    created_by=staff.id,
                    description=f"Assigned routes retrieved for staff ID: {userid} with van: {van.van_make}"
                )
                return Response({'status': True, 'data':data, 'message': 'Assigned Routes List!'})
            else:
                log_activity(
                    created_by=staff.id,
                    description=f"No van found for staff ID: {userid}"
                )
                return Response({'status': False, 'data':[],'message': 'No van found for the given staff.'})
        # except Exception as e:
        #     print(e)
        #     return Response({'status': False, 'message': str(e) })


class Create_Customer(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CustomersSerializers

    def post(self, request, *args, **kwargs):
        try:
            username = request.headers['username']
            user=CustomUser.objects.get(username=username)
            # print(request.data,"<--request.data")
            serializer=Create_Customers_Serializers(data=request.data)

            if serializer.is_valid():
                serializer.save(created_by=user.id,branch_id=user.branch_id)
                log_activity(
                    created_by=user.id,
                    description=f"Customer created by user: {user.username}"
                )
                return Response({'status':True,'message':'Customer Succesfully Created'},status=status.HTTP_201_CREATED)
            else :
                return Response({'status':False,'message':serializer.errors},status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(e)
            return Response({'status': False, 'message': 'Something went wrong!'})

    def get(self,request,id=None):
        try:
            if id :
                queryset = Customers.objects.get(customer_id=id)
                serializer = Create_Customers_Serializers(queryset)
                return Response(serializer.data)
            queryset = Customers.objects.all()
            serializer = Create_Customers_Serializers(queryset,many=True)
            return Response({'status':True,'data':serializer.data,'message':'Fetched Customer Details'},status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response({'status': False, 'message': 'Something went wrong!'})

    def put(self, request, id):
        try:
            customers = Customers.objects.get(customer_id=id)
            serializer = Create_Customers_Serializers(customers, data=request.data)
            if serializer.is_valid():
                serializer.save(modified_by=request.user.id,branch_id=request.user.branch_id,modified_date = datetime.now())
                log_activity(
                    created_by=request.user.id,
                    description=f"Fetched details for customer: {customers.customer_name}",
                    created_date=timezone.now()
                )
                return Response({'status':True,'data':serializer.data,'message':'Customer Succesfully Created'},status=status.HTTP_201_CREATED)
            else:
                return Response({'status':True,'data':[],'message':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({'status': False, 'message': 'Something went wrong!'})

class Get_Items_API(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = Items_Serializers
    product_serializer = Products_Serializers

    def get(self,request,id=None):
        try:
            #customer = request.data['id']
            customer_exists = Customers.objects.filter(customer_id=id).exists()
            if customer_exists:
                customer_data = Customers.objects.get(customer_id=id)
                print(customer_data.branch_id)
                branch_id = customer_data.branch_id.branch_id
                branch = BranchMaster.objects.get(branch_id=branch_id)
                products = Product.objects.filter(branch_id=branch).exists()
                if products:
                    products = Product.objects.filter(branch_id=branch)
                    data = []
                    for product in products:
                        item_price_level_list = Product_Default_Price_Level.objects.filter(product_id=product,customer_type=customer_data.customer_type).exists()
                        if item_price_level_list:
                            item_price_level = Product_Default_Price_Level.objects.get(product_id=product,customer_type=customer_data.customer_type)
                            serializer = self.serializer_class(item_price_level)
                            data.append(serializer.data)
                        else:
                            serializer_1 = self.product_serializer(product)
                            data.append(serializer_1.data)
                    data2 = {'customer_id':customer_data.customer_id,'customer_name':customer_data.customer_name,
                             'default_water_rate':customer_data.rate, 'items_count':len(data)}
                    
                    log_activity(
                        created_by=request.user,
                        description=f"Fetched items for customer {customer_data.customer_name} (ID: {customer_data.customer_id})"
                    )
                    
                    return Response({'status': True, 'data': {'items':data,'customer':data2}, 'message': 'Data fetched Successfully'})
                else:
                    return Response({'status': True, 'data': [], 'message': 'Data fetched Successfully'})
            else:
                return Response({'status': False,'message': 'Customer Not Exists'})

        except Exception as e:
            print(e)
            return Response({'status': False, 'message': 'Something went wrong!'})

class Add_Customer_Custody_Item_API(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        try:
            user = CustomUser.objects.get(username=request.user.username)
            data = request.data.get('data_list', {})
            customer_id = data.get('customer_id')
            agreement_no = data.get('agreement_no')
            total_amount = data.get('total_amount')
            deposit_type = data.get('deposit_type')
            reference_no = data.get('reference_no')
            amount_collected = data.get('amount_collected')
            product_id = data.get('product')
            quantity = data.get('quantity')
            serialnumber = data.get('serialnumber')
            amount = data.get('amount')
            can_deposite_chrge = data.get('can_deposite_chrge')
            five_gallon_water_charge = data.get('five_gallon_water_charge')

            with transaction.atomic():
                # Create CustodyCustom instance
                custody_data = CustodyCustom.objects.create(
                    customer=Customers.objects.get(pk=customer_id),
                    agreement_no=agreement_no,
                    total_amount=total_amount,
                    deposit_type=deposit_type,
                    reference_no=reference_no,
                    amount_collected=amount_collected,
                    created_by=user.pk,
                    created_date=datetime.today(),
                )

                # Create CustodyCustomItems instance
                product_instance = ProdutItemMaster.objects.get(pk=product_id)
                custody_item_data = {
                    "custody_custom": custody_data,
                    "product": product_instance,
                    "quantity": quantity,
                    "serialnumber": serialnumber,
                    "amount": amount,
                    "can_deposite_chrge": can_deposite_chrge,
                    "five_gallon_water_charge": five_gallon_water_charge,
                }
                item_instance = CustodyCustomItems.objects.create(**custody_item_data)

                # Update bottle count if necessary
                if product_instance.product_name == "5 Gallon":
                    bottle_count, created = BottleCount.objects.get_or_create(
                        van__salesman=request.user,
                        created_date__date=custody_data.created_date.date(),
                        defaults={'custody_issue': quantity}
                    )
                    if not created:
                        bottle_count.custody_issue += quantity
                        bottle_count.save()

                # Update or create CustomerCustodyStock
                if CustomerCustodyStock.objects.filter(customer=custody_data.customer, product=product_instance).exists():
                    stock_instance = CustomerCustodyStock.objects.get(customer=custody_data.customer, product=product_instance)
                    stock_instance.quantity += quantity
                    stock_instance.serialnumber = (stock_instance.serialnumber + ',' + serialnumber) if stock_instance.serialnumber else serialnumber
                    stock_instance.agreement_no = (stock_instance.agreement_no + ',' + agreement_no) if stock_instance.agreement_no else agreement_no
                    stock_instance.save()
                else:
                    CustomerCustodyStock.objects.create(
                        customer=custody_data.customer,
                        agreement_no=agreement_no,
                        deposit_type=deposit_type,
                        reference_no=reference_no,
                        product=product_instance,
                        quantity=quantity,
                        serialnumber=serialnumber,
                        amount=amount,
                        can_deposite_chrge=can_deposite_chrge,
                        five_gallon_water_charge=five_gallon_water_charge,
                        amount_collected=amount_collected
                    )

                log_activity(
                    created_by=user,
                    description=f"Created custody item for customer {customer_id}"
                )
                
                return Response({'status': True, 'message': 'Customer Custody Item Successfully Created'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            log_activity(
                created_by=request.user,
                description=f"Error creating custody item for customer {customer_id} - {str(e)}"
            )
            return Response({'status': False, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self,request,id=None):
        try:
            customer_exists = Customers.objects.filter(customer_id=id).exists()
            if customer_exists:
                customer = Customers.objects.get(customer_id=id)
                custody_list = CustomerCustodyStock.objects.filter(customer=customer)
                if custody_list:
                    serializer = CustomerCustodyStockProductsSerializer(custody_list, many=True)
                    log_activity(
                        created_by=request.user,
                        description=f"Fetched custody items for customer {id}"
                    )
                    return Response({'status': True,'data':serializer.data,'message':'data fetched successfully'},status=status.HTTP_200_OK)
                else:
                    return Response({'status': True,'data':[],'message':'No custody items'},status=status.HTTP_200_OK)
            else :
                return Response({'status': False,'message':'Customer not exists'},status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(e)
            return Response({'status': False, 'message': str(e)})

    def put(self, request, *args, **kwargs):
        try:
            data_list = request.data.get('data_list', [])
            objects_to_update = CustodyCustomItems.objects.filter(pk__in=[item['id'] for item in data_list])

            for data_item in data_list:
                obj = objects_to_update.get(pk=data_item['id'])
                serializer = CustomerCustodyItemSerializer(obj, data=data_item, partial=True)
                if serializer.is_valid():
                    serializer.save()
            log_activity(
                created_by=request.user,
                description="Updated custody items for multiple customers"
            )
            return Response({'status': True, 'message': 'Customer custody item Updated Successful'}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'status': False, 'message': 'Something went wrong!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Add_No_Coupons(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerInhandCouponsSerializers

    def post(self,request, *args, **kwargs):
        try:
            username = request.headers['username']
            user = CustomUser.objects.get(username=username)
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save(created_by=user.id)
                log_activity(
                    created_by=user.id,
                    description=f'Added new coupon for customer '
                )
                return Response({'status': True,'data':serializer.data,'message':'data added Succesfully'},status=status.HTTP_201_CREATED)
            else :
                return Response({'status': False,'message':serializer.errors},status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(e)
            return Response({'status': False, 'message': 'Something went wrong!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self,request,id=None):
        try:
            customer_exists = Customers.objects.filter(customer_id=id).exists()
            if customer_exists:
                customer_exists = Customers.objects.get(customer_id=id)
                custody_list = Customer_Inhand_Coupons.objects.filter(customer=customer_exists.customer_id)
                if custody_list:
                    serializer = GetCustomerInhandCouponsSerializers(custody_list, many=True)
                    log_activity(
                        created_by=request.user.id,
                        description=f'Fetched coupons for customer {id}'
                    )
                    return Response({'status': True,'data':serializer.data,'message':'data fetched successfully'},status=status.HTTP_200_OK)
                else:
                    return Response({'status': True,'data':[],'message':'No coupons available'},status=status.HTTP_200_OK)
            else :
                return Response({'status': False,'message':'Customer not exists'},status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(e)
            return Response({'status': False, 'message': 'Something went wrong!'})

    def put(self, request, id, *args, **kwargs):
        try:
            customers_coupon = Customer_Inhand_Coupons.objects.get(cust_inhand_id=id)
            serializer = CustomerInhandCouponsSerializers(customers_coupon,data=request.data)
            if serializer.is_valid():
                serializer.save(modified_by=request.user.id,branch_id=request.user.branch_id,modified_date = datetime.now())
                log_activity(
                    created_by=request.user.id,
                    description=f'Updated coupon with ID {id}'
                )
                return Response({'status':True,'data':serializer.data,'message':'Update coupons successfully'},status=status.HTTP_201_CREATED)
            else :
                return Response({'status': False,'message':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({'status': False, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from collections import defaultdict

@api_view(['GET'])
def product_items(request):
    log_activity(
            created_by=request.user.id,
            description="Fetching product items"
        )
    if (instances:=ProdutItemMaster.objects.all()).exists():
        if request.GET.get("non_coupon"):
            instances = instances.exclude(category__category_name="Coupons")
            log_activity(
                    created_by=request.user.id,
                    description="Excluding coupons from the product items"
                )
        serializer = ProdutItemMasterSerializer(instances, many=True, context={"request": request})

        status_code = status.HTTP_200_OK
        response_data = {
            "status": status_code,
            "StatusCode": 6000,
            "data": serializer.data,
        }
    else:
        status_code = status.HTTP_400_BAD_REQUEST
        response_data = {
            "status": status_code,
            "StatusCode": 6001,
            "message": "No data",
        }
        log_activity(
            created_by=request.user.id,
            description=f"Error fetching product items"
        )

    return Response(response_data, status_code)

class Staff_New_Order(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    staff_order_serializer = StaffOrderSerializers
    staff_order_details_serializer = StaffOrderDetailsSerializers

    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                log_activity(
                    created_by=request.user.id,
                    description="Attempting to place a new staff order"
                )
                data_list = request.data.get('data_list', [])
                last_order = Staff_Orders.objects.all()
                if last_order.exists():
                    last_order_number = last_order.latest("created_date").order_number
                    new_order_number = int(last_order_number) + 1
                else:
                    new_order_number = 1

                order_number = f"{new_order_number}"
                order_date = request.data.get('order_date')

                # delivery_date = request.data.get('delivery_date')
                
                if order_date:
                    order_date = datetime.strptime(order_date, '%Y-%m-%d').date()
                else:
                    order_date = datetime.today().date()
                
                # if delivery_date:
                #     delivery_date = datetime.strptime(delivery_date, '%Y-%m-%d').date()
                # else:
                #     delivery_date = datetime.today().date()

                serializer_1 = self.staff_order_serializer(data=request.data)
                if serializer_1.is_valid(raise_exception=True):
                    order_data = serializer_1.save(
                        created_by=request.user.id,
                        order_number=order_number.upper(),
                        order_date=order_date,
                        # delivery_date=delivery_date
                    )
                    staff_order = order_data.staff_order_id
                    
                    log_activity(
                        created_by=request.user.id,
                        description=f"Staff order {order_number} created successfully"
                    )

                    # Aggregate products by ID
                    product_dict = defaultdict(int)
                    for data in data_list:
                        product_id = data.get("product_id")
                        count = Decimal(data.get("count", 0))
                        product_dict[product_id] += count
                        
                    # Create order details for each product
                    order_details_data = []
                    for product_id, count in product_dict.items():
                        order_details_data.append({
                            "created_by": request.user.id,
                            "staff_order_id": staff_order,
                            "product_id": product_id,
                            "count": count
                        })
                        
                    serializer_2 = self.staff_order_details_serializer(data=order_details_data, many=True)

                    if serializer_2.is_valid(raise_exception=True):
                        serializer_2.save()
                        log_activity(
                            created_by=request.user.id,
                            description=f"Order details for staff order {order_number} saved successfully"
                        )
                        return Response({'status': True, 'message': 'Order Placed Successfully'}, status=status.HTTP_201_CREATED)
                    else:
                        log_activity(
                            created_by=request.user.id,
                            description=f"Error saving order details for staff order {order_number}: {serializer_2.errors}"
                        )
                        return Response({'status': False, 'message': serializer_2.errors}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    log_activity(
                        created_by=request.user.id,
                        description=f"Error creating staff order {order_number}: {serializer_1.errors}"
                    )
                    return Response({'status': False, 'message': serializer_1.errors}, status=status.HTTP_400_BAD_REQUEST)

        except IntegrityError as e:
                # Handle database integrity error
                response_data = {"status": "false","title": "Failed","message": str(e),}

        except Exception as e:
            # Handle other exceptions
            response_data = {"status": "false","title": "Failed","message": str(e),}
        return Response(response_data)


class Customer_Create(APIView):
    serializer_class = CustomersSerializers

    def post(self, request, *args, **kwargs):
        try:
            username=request.data["mobile_no"]
            print('username',username)
            password=request.data["password"]
            print('password',password)
            hashed_password=make_password(password)

            if Customers.objects.filter(mobile_no=request.data["mobile_no"]).exists():
                return Response({'status':True,'message':'Customer with this mobile number already exist !! Try another number'},status=status.HTTP_201_CREATED)

            customer_data=CustomUser.objects.create(
                password=hashed_password,
                username=username,
                first_name=request.data['customer_name'],
                email=request.data['email_id'],
                user_type='Customer'
                )
            request.data["user_id"]=customer_data.id
            request.data["created_by"]=str(request.data["customer_name"])
            serializer=CustomersSerializers(
                custom_id = get_custom_id(Customers),
                data=request.data
                )

            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response({'status':True, 'data':request.data, 'message':'Customer Succesfully Created'},status=status.HTTP_201_CREATED)
            else:
                return Response({'status': False,'data':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            user_exist = CustomUser.objects.filter(phone=request.data['mobile_no']).exists()
            if user_exist:
                user_obj = CustomUser.objects.get(phone=request.data['mobile_no'])
                user_obj.delete()
                return Response({"status": False, 'data': e, "message": "Something went wrong!"})
            print(e)
            return Response({'status': False, 'message': 'Something went wrong!'})

class CustomerDetails(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self,request,id=None):
        try:
            if id :
                queryset = Customers.objects.get(customer_id=id)
                serializer = CustomersSerializers(queryset)
                return Response(serializer.data)
            queryset = Customers.objects.all()
            serializer = CustomersSerializers(queryset,many=True)
            return Response({'status':True,'data':serializer.data,'message':'Fetched Customer Details'},status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response({'status': False, 'message': 'Something went wrong!'})

    def put(self, request, id):
        try:
            customers = Customers.objects.get(customer_id=id)
            serializer = CustomersSerializers(customers, data=request.data)
            if serializer.is_valid():
                serializer.save(modified_by=request.user.id,modified_date = datetime.now())
                return Response({'status':True,'data':serializer.data,'message':'Customer Succesfully Created'},status=status.HTTP_201_CREATED)
            else:
                return Response({'status':True,'data':[],'message':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({'status': False, 'message': 'Something went wrong!'})

def is_valid_mobile(mobile):
    return len(mobile) == 10 and mobile.isdigit()

class Check_Customer(APIView):
    def post(self, request, *args, **kwargs):
        try:
            mobile = request.data['mobile']
            user_exists = Customers.objects.filter(mobile_no=mobile).exists()
            if user_exists:
                user = Customers.objects.get(mobile_no=mobile)
                custom_user_instance = user.user_id
                if is_valid_mobile(mobile):
                    number = randint(1111, 9999)
                    future_time = dt.now() + timedelta(minutes=5)
                    usr_otpcheck = UserOTP.objects.filter(user=custom_user_instance).first()
                    print("usr_otpcheck", usr_otpcheck)
                    if usr_otpcheck is None:
                        usr_otp = UserOTP.objects.create(
                            expire_time=future_time, user=custom_user_instance, mobile=mobile, otp=str(number),
                            created_on=timezone.now()
                        )
                        return Response({'status':True,'message': 'OTP sent successfully', 'otp': str(number)},
                                        status=status.HTTP_200_OK)
                    else:
                        usr_otpcheck.otp = str(number)
                        usr_otpcheck.expire_time = future_time
                        usr_otpcheck.created_on = timezone.now()
                        usr_otpcheck.save()
                        return Response({'status':True,'message': 'OTP sent successfully', 'otp': str(number)},
                                        status=status.HTTP_200_OK)
                else:
                    return Response({'status':False,'error': 'Invalid mobile number'}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'status':False,'message': 'user not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            print(e)
            return Response({'status': False, 'message': 'Something went wrong!'})


class Verify_otp(APIView):
    def post(self, request, *args, **kwargs):
        try:
            mobile = request.data['mobile']
            code = request.data['code']
            cust_user = Customers.objects.get(mobile_no=mobile).user_id
            if cust_user is not None:
                user_id = CustomUser.objects.get(username=cust_user).id
                usr_otpcheck = UserOTP.objects.filter(user=user_id).first()
                if usr_otpcheck and usr_otpcheck.expire_time > str(timezone.now()):
                    if usr_otpcheck.otp == code:
                        return Response({'status':True,'message': 'OTP validation successful'}, status=status.HTTP_200_OK)
                    else:
                        return Response({'status':False,'error': 'OTP has expired or not found'}, status=status.HTTP_404_NOT_FOUND)
                else:
                    return Response({'status':False,'error': 'OTP has expired or not found'}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'status':False,'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return Response({'status': False, 'message': 'Something went wrong!'})


##################################  Client Management #################################


# Vacation

class VacationListAPI(APIView):
    def get(self, request):
        vacation = Vacation.objects.all()
        serializer = VacationSerializer(vacation, many=True)
        return Response(serializer.data)

class VacationAddAPI(APIView):
    def post(self, request):
        serializer=VacationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VacationEditAPI(APIView):
    def put(self, request, vacation_id):
        vacation = Vacation.objects.get(vacation_id=vacation_id)
        serializer = VacationSerializer(vacation, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VacationDeleteAPI(APIView):
    def delete(self, request, vacation_id):
        vacation = Vacation.objects.get(vacation_id=vacation_id)
        vacation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ScheduleView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, date_str):
        if date_str:
            date = datetime.strptime(date_str, '%Y-%m-%d')
        else:
            return Response({'error': 'Date parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        staff = CustomUser.objects.get(id=request.user.id)
        if staff.user_type not in ['Driver', 'Salesman', 'Supervisor', 'Manager']:
            return Response({'error': 'Invalid user type'}, status=status.HTTP_400_BAD_REQUEST)

        if staff.user_type == "Driver":
            van = Van.objects.filter(driver=staff)
        elif staff.user_type == "Salesman":
            van = Van.objects.filter(salesman=staff)

        routes = []
        for v in van:
            van_routes = Van_Routes.objects.filter(van=v)
            for v_r in van_routes:
                if v_r.routes not in routes:
                    routes.append(v_r.routes)

        route_details = []
        for route in routes:
            trip_count = 0
            customer_count = 0
            bottle_count = 0
            todays_customers = find_customers(request, date_str, route.route_id)
            trips = []

            if todays_customers is None:
                todays_customers = []
                trips.append('trip1')
            else:
                for customer in todays_customers:
                    customer_count += 1
                    if not customer['no_of_bottles']:
                        customer_no_of_bottles = 0
                    else :
                        customer_no_of_bottles = customer['no_of_bottles']
                    bottle_count += customer_no_of_bottles
                    if customer['trip'] not in trips:
                        trips.append(customer['trip'])

            if not trips:
                trips.append('trip1')

            route_details.append({
                'route_name': route.route_name,
                'route_id': route.route_id,
                'no_of_customers': customer_count,
                'no_of_bottles': bottle_count,
                'no_of_trips': len(trips),
                'trips': trips
            })

        return Response({'def_date': date_str, 'staff': staff.first_name, 'details': route_details}, status=status.HTTP_200_OK)


class ScheduleByRoute(APIView):

    def get(self, request, date_str, route_id, trip):
        route = RouteMaster.objects.get(route_id=route_id)
        
        totale_bottle = 0
        customers = []
        todays_customers = find_customers(request, date_str, route_id)

        if todays_customers:
            customers = [
                {
                    **customer,
                    'emergency': 1 if DiffBottlesModel.objects.filter(customer__pk=customer["customer_id"], delivery_date__date=datetime.today().date()).exists() else 0,
                    'is_supplied': CustomerSupply.objects.filter(customer__pk=customer["customer_id"], created_date__date=datetime.today().date()).exists()
                }
                for customer in todays_customers 
                if customer['trip'] == trip.capitalize()
            ]
            is_supplied = False
            for customer in customers:
                totale_bottle+=customer['no_of_bottles']
                
            return Response({
                'def_date': date_str,
                'totale_bottle':totale_bottle,
                'route': {
                    'route_id': route.route_id,
                    'route_name': route.route_name,
                    'trip' : trip
                },
                'todays_customers': customers,
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'def_date': date_str,
                'totale_bottle':totale_bottle,
                'route': {
                    'route_id': route.route_id,
                    'route_name': route.route_name,
                    'trip' : trip
                },
                'todays_customers': customers,
            }, status=status.HTTP_200_OK)

class Get_Category_API(APIView):
    def get(self, request):
        category_id = request.GET.get('category_id')
        products = Product.objects.filter(category_id=category_id).values('product_id', 'product_name','rate')
        return JsonResponse({'products': list(products)})

class Myclient_API(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CustomersSerializers

    def post(self, request, *args, **kwargs):
        try:
            userid = request.data.get("id")
            route_id = request.data.get("route_id")

            # Fetch the staff user
            staff = CustomUser.objects.get(id=userid)

            # Fetch van details where the staff is either a driver or a salesman
            vans = Van.objects.filter(Q(driver=staff) | Q(salesman=staff)).first()

            if vans is not None:
                if not route_id:
                    van = Van.objects.get(van_id=vans.pk)
                    assign_routes = Van_Routes.objects.filter(van=van).values_list('routes', flat=True)
                    routes_list = RouteMaster.objects.filter(route_id__in=assign_routes).values_list('route_id', flat=True)

                    customer_list = Customers.objects.filter(routes__pk__in=routes_list)
                else:
                    customer_list = Customers.objects.filter(routes__pk=route_id)

                # Serialize the filtered customers
                serializer = self.serializer_class(customer_list, many=True)

                return Response(serializer.data)

            return Response({'status': False, 'message': 'No van assigned to the user'})

        except CustomUser.DoesNotExist:
            return Response({'status': False, 'message': 'User not found'})
        except Exception as e:
            return Response({'status': False, 'message': str(e)})

class GetCustodyItem_API(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerCustodyItemSerializer
    def get(self, request, *args, **kwargs):
        try:
            user_id=request.user.id
            customerobj=Customers.objects.filter(sales_staff=user_id)
            for customer in customerobj:
                customerid=customer.customer_id
                custody_items=CustodyCustomItems.objects.filter(customer=customerid)
                serializer=self.serializer_class(custody_items,many=True)
                return Response({'status': True, 'data':serializer.data, 'message': 'custody items lis passed!'})
        except Exception as e:
            return Response({'status': False, 'data': str(e), 'message': str(e)})


# coupon sales
@api_view(['GET'])
# @permission_classes((AllowAny,))
# @renderer_classes((JSONRenderer,))
def get_lower_coupon_customers(request):
    if not (inhand_instances:=CustomerCouponStock.objects.filter(count__lte=5)).exists():
        customers_ids = inhand_instances.values_list('customer__customer_id', flat=True)
        instances = Customers.objects.filter(sales_type="CASH COUPON",pk__in=customers_ids)

        serialized = LowerCouponCustomersSerializer(instances, many=True, context={"request": request})

        status_code = status.HTTP_200_OK
        response_data = {
            "status": status_code,
            "StatusCode": 6000,
            "data": serialized.data,
        }
    else:
        status_code = status.HTTP_400_BAD_REQUEST
        response_data = {
            "status": status_code,
            "StatusCode": 6001,
            "message": "No data",
        }

    return Response(response_data, status_code)

@api_view(['GET'])
# @permission_classes((AllowAny,))
# @renderer_classes((JSONRenderer,))
def fetch_coupon(request):
    coupon_type = request.GET.get("coupon_type")
    book_no = request.GET.get("book_no")
    
    date = request.GET.get('date')
    if date:
        date = datetime.strptime(date, '%Y-%m-%d').date()
    else:
        date = datetime.today().date()

    van_stocks = VanCouponStock.objects.filter(created_date=date,coupon__coupon_type_id__coupon_type_name=coupon_type,coupon__book_num=book_no)

    if van_stocks.exists():
        coupons = van_stocks.first().coupon.all()

        serialized = VanCouponStockSerializer(coupons, many=True, context={"request": request})

        status_code = status.HTTP_200_OK
        response_data = {
            "status": status_code,
            "StatusCode": 6000,
            "data": serialized.data,
        }
    else:
        status_code = status.HTTP_400_BAD_REQUEST
        response_data = {
            "status": status_code,
            "StatusCode": 6001,
            "message": "No data",
        }

    return Response(response_data, status_code)

def delete_coupon_recharge(invoice_no):
    """
    Delete a customer coupon recharge and reverse all related transactions.
    """
    try:
        with transaction.atomic():
            invoice = Invoice.objects.get(invoice_no=invoice_no)
            customer_coupon = CustomerCoupon.objects.get(invoice_no=invoice_no)
            
            coupon_items = CustomerCouponItems.objects.filter(customer_coupon=customer_coupon)
            for item in coupon_items:
                coupon_stock = CustomerCouponStock.objects.get(customer=customer_coupon.customer,coupon_type_id=item.coupon.coupon_type)
                coupon_stock.count -= int(item.coupon.coupon_type.no_of_leaflets)
                coupon_stock.save()
                                                
                van_coupon_stock = VanCouponStock.objects.get(coupon=item.coupon)
                van_coupon_stock.stock += 1
                van_coupon_stock.save()
                item.delete()
                
                coupon_stock_status = CouponStock.objects.get(couponbook=item.coupon)
                coupon_stock_status.coupon_stock = "van"
                coupon_stock_status.save()

            InvoiceDailyCollection.objects.filter(invoice=invoice).delete()

            ChequeCouponPayment.objects.filter(customer_coupon=customer_coupon).delete()
            
            balance_amount = invoice.amout_total - invoice.amout_recieved
                
            if invoice.amout_total > invoice.amout_recieved:
                if CustomerOutstandingReport.objects.filter(customer=customer_coupon.customer, product_type="amount").exists():
                    customer_outstanding_report_instance = CustomerOutstandingReport.objects.get(customer=customer_coupon.customer, product_type="amount")
                    customer_outstanding_report_instance.value -= Decimal(balance_amount)
                    customer_outstanding_report_instance.save()
                    
            elif invoice.amout_total < invoice.amout_recieved:
                customer_outstanding_report_instance = CustomerOutstandingReport.objects.get(customer=customer_coupon.customer, product_type="amount")
                customer_outstanding_report_instance.value += Decimal(balance_amount)
                customer_outstanding_report_instance.save()
            
            customer_coupon.delete()
            
            return True

    except Invoice.DoesNotExist:
        return {"status": "error", "message": "Invoice not found."}
    except CustomerCoupon.DoesNotExist:
        return {"status": "error", "message": "Customer coupon not found."}
    except Exception as e:
        return {"status": "error", "message": f"An error occurred: {str(e)}"}

class CustomerCouponRecharge(APIView):
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                coupons_data = request.data.get('coupons', [])
                payment_data = request.data.get('payment', {})

                coupon_instances = []
                for coupon_data in coupons_data:
                    customer = Customers.objects.get(pk=coupon_data.pop("customer"))
                    salesman = CustomUser.objects.get(pk=coupon_data.pop("salesman"))
                    items_data = coupon_data.pop('items', [])
                    
                    customer_coupon = CustomerCoupon.objects.create(
                        customer=customer,
                        salesman=salesman,
                        created_date=datetime.today(),
                        **coupon_data
                        )
                    
                    coupon_instances.append(customer_coupon)
                    
                    balance_amount = Decimal(coupon_data.pop("balance"))
                    coupon_method = coupon_data.pop("coupon_method")
                    
                    if balance_amount != 0 :
                        
                        customer_outstanding = CustomerOutstanding.objects.create(
                            customer=customer,
                            product_type="amount",
                            created_by=request.user.id,
                            created_date=datetime.today(),
                        )

                        outstanding_amount = OutstandingAmount.objects.create(
                            amount=balance_amount,
                            customer_outstanding=customer_outstanding,
                        )
                        outstanding_instance = ""

                        try:
                            outstanding_instance=CustomerOutstandingReport.objects.get(customer=customer,product_type="amount")
                            outstanding_instance.value += Decimal(outstanding_amount.amount)
                            outstanding_instance.save()
                        except:
                            outstanding_instance = CustomerOutstandingReport.objects.create(
                                product_type='amount',
                                value=outstanding_amount.amount,
                                customer=outstanding_amount.customer_outstanding.customer
                            )

                    # Create CustomerCouponItems instances
                    if coupon_method == "manual":
                        
                        for item_data in items_data:
                            coupon = NewCoupon.objects.get(pk=item_data.pop("coupon"))
                            items = CustomerCouponItems.objects.create(
                                customer_coupon=customer_coupon,
                                coupon=coupon,
                                rate=item_data.pop("rate")
                            )

                            # Update CustomerCouponStock based on coupons
                            for coupon_instance in coupon_instances:
                                coupon_method = coupon.coupon_method
                                customer_id = customer
                                coupon_type_id = CouponType.objects.get(pk=coupon.coupon_type_id)

                                try:
                                    customer_coupon_stock = CustomerCouponStock.objects.get(
                                        coupon_method=coupon_method,
                                        customer_id=customer_id.pk,
                                        coupon_type_id=coupon_type_id
                                    )
                                except CustomerCouponStock.DoesNotExist:
                                    customer_coupon_stock = CustomerCouponStock.objects.create(
                                        coupon_method=coupon_method,
                                        customer_id=customer_id.pk,
                                        coupon_type_id=coupon_type_id,
                                        count=0
                                    )

                                customer_coupon_stock.count += Decimal(coupon.no_of_leaflets)
                                customer_coupon_stock.save()
                                
                                van_coupon_stock = VanCouponStock.objects.get(created_date=datetime.today().date(),coupon=coupon)
                                van_coupon_stock.stock -= 1
                                van_coupon_stock.sold_count += 1
                                van_coupon_stock.save()
                                
                            CouponStock.objects.filter(couponbook=coupon).update(coupon_stock="customer")
                                
                    elif coupon_method == "digital":
                        digital_coupon_data = request.data.get('digital_coupon', {})
                        try:
                            customer_coupon_stock = CustomerCouponStock.objects.get(
                                coupon_method=coupon_method,
                                customer_id=customer.pk,
                                coupon_type_id=CouponType.objects.get(coupon_type_name="Digital")
                            )
                        except CustomerCouponStock.DoesNotExist:
                            customer_coupon_stock = CustomerCouponStock.objects.create(
                                coupon_method=coupon_method,
                                customer_id=customer.pk,
                                coupon_type_id=CouponType.objects.get(coupon_type_name="Digital"),
                                count=0
                            )
                        customer_coupon_stock.count += digital_coupon_data.get("count")
                        customer_coupon_stock.save()
                    
                    date_part = timezone.now().strftime('%Y%m%d')
                    try:
                        invoice_last_no = Invoice.objects.filter(is_deleted=False).latest('created_date')
                        last_invoice_number = invoice_last_no.invoice_no

                        # Validate the format of the last invoice number
                        parts = last_invoice_number.split('-')
                        if len(parts) == 3 and parts[0] == 'WTR' and parts[1] == date_part:
                            prefix, old_date_part, number_part = parts
                            new_number_part = int(number_part) + 1
                            invoice_number = f'{prefix}-{date_part}-{new_number_part:04d}'
                        else:
                            # If the last invoice number is not in the expected format, generate a new one
                            random_part = str(random.randint(1000, 9999))
                            invoice_number = f'WTR-{date_part}-{random_part}'
                    except Invoice.DoesNotExist:
                        random_part = str(random.randint(1000, 9999))
                        invoice_number = f'WTR-{date_part}-{random_part}'

                    # Create the invoice
                    invoice_instance = Invoice.objects.create(
                        invoice_no=invoice_number,
                        created_date=datetime.today(),
                        net_taxable=customer_coupon.net_amount,
                        discount=customer_coupon.discount,
                        amout_total=customer_coupon.total_payeble,
                        amout_recieved=customer_coupon.amount_recieved,
                        customer=customer_coupon.customer,
                        reference_no=customer_coupon.reference_number
                    )
                    
                    customer_coupon.invoice_no = invoice_instance.invoice_no
                    customer_coupon.save()
                    
                    if invoice_instance.amout_total == invoice_instance.amout_recieved:
                        invoice_instance.invoice_status = "paid"
                    else:
                        invoice_instance.invoice_status = "non_paid"
                    invoice_instance.save()
                    
                    coupon_items = CustomerCouponItems.objects.filter(customer_coupon=customer_coupon) 
                    
                    # Create invoice items
                    for item_data in coupon_items:
                        category = CategoryMaster.objects.get(category_name__iexact="coupons")
                        product_item = ProdutItemMaster.objects.get(product_name=item_data.coupon.coupon_type.coupon_type_name)
                        # print(product_item)
                        InvoiceItems.objects.create(
                            category=category,
                            product_items=product_item,
                            qty=1,
                            rate=product_item.rate,
                            invoice=invoice_instance,
                            remarks='invoice genereted from recharge coupon items reference no : ' + invoice_instance.reference_no
                        )
                        
                    InvoiceDailyCollection.objects.create(
                        invoice=invoice_instance,
                        created_date=datetime.today(),
                        customer=invoice_instance.customer,
                        salesman=request.user,
                        amount=invoice_instance.amout_recieved,
                    ) 
                    
                    # Generate receipt number
                    try:
                        receipt_last_no = Receipt.objects.all().latest('created_date')
                        last_receipt_number = receipt_last_no.receipt_number

                        # Validate the format of the last receipt number
                        parts = last_receipt_number.split('-')
                        if len(parts) == 3 and parts[0] == 'RCT' and parts[1] == date_part:
                            prefix, old_date_part, number_part = parts
                            new_number_part = int(number_part) + 1
                            receipt_number = f'{prefix}-{date_part}-{new_number_part:04d}'
                        else:
                            # If the last receipt number is not in the expected format, generate a new one
                            random_part = str(random.randint(1000, 9999))
                            receipt_number = f'RCT-{date_part}-{random_part}'
                    except Receipt.DoesNotExist:
                        random_part = str(random.randint(1000, 9999))
                        receipt_number = f'RCT-{date_part}-{random_part}'

                    invoice_numbers = []
                    invoice_numbers.append(invoice_instance.invoice_no)
                    
                    receipt = Receipt.objects.create(
                        transaction_type='coupon_rechange',
                        instance_id=str(customer_coupon.id),  
                        amount_received=customer_coupon.amount_recieved,
                        receipt_number=receipt_number,
                        invoice_number=",".join(invoice_numbers),
                        customer=customer_coupon.customer
                    )

                # Create ChequeCouponPayment instanceno_of_leaflets
                cheque_payment_instance = None
                if coupon_data.pop("payment_type") == 'cheque':
                    cheque_payment_instance = ChequeCouponPayment.objects.create(**payment_data)

                return Response({"message": "Recharge successful"}, status=status.HTTP_200_OK)

        except IntegrityError as e:
            # Handle database integrity error
            response_data = {
                "status": "false",
                "title": "Failed",
                "message": str(e),
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            # Handle other exceptions
            response_data = {
                "status": "false",
                "title": "Failed",
                "message": str(e),
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        """
        API endpoint to delete a customer coupon recharge.
        """
        try:
            customer_coupon = CustomerCoupon.objects.get(pk=pk)
            if (customer_coupon):
                return Response({"message": "Customer coupon recharge deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"message": "Failed to delete customer coupon recharge."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except CustomerCoupon.DoesNotExist:
            return Response({"message": "Customer coupon recharge not found."}, status=status.HTTP_404_NOT_FOUND)

        except IntegrityError as e:
            return Response({"message": f"IntegrityError: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({"message": f"Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



from django.shortcuts import get_object_or_404


class GetProductAPI(APIView):

    def get(self, request, *args, **kwargs):
        try:
            product_names = ["5 Gallon", "Hot and  Cool", "Dispenser"]
            product_items = ProdutItemMaster.objects.filter(product_name__in=product_names)
            # print('product_items',product_items)
            serializer = ProdutItemMasterSerializerr(product_items, many=True)          
            return Response({"products": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            print(e, "error")
            return Response({"status": False, "data": str(e), "message": "Something went wrong!"})


# class CustodyCustomAPIView(APIView):
#     def post(self, request):
#         try:
#             customer = Customers.objects.get(customer_id=request.data['customer_id'])
#             agreement_no = request.data['agreement_no']
#             total_amount = int(request.data['total_amount'])
#             deposit_type = request.data['deposit_type']
#             reference_no = request.data['reference_no']
#             product = ProdutItemMaster.objects.get(id=request.data['product_id'])
#             quantity = int(request.data['quantity'])
#             serialnumber = request.data['serialnumber']
#             amount_collected = request.data['amount_collected']
#             can_deposite_chrge = request.data.get('can_deposite_chrge', 0)
            
#             # Calculate the five_gallon_water_charge based on the quantity and customer's rate
#             five_gallon_water_charge = quantity * total_amount

#             # Create CustodyCustom instance
#             custody_custom_instance = CustodyCustom.objects.create(
#                 customer=customer,
#                 agreement_no=agreement_no,
#                 total_amount=total_amount,
#                 deposit_type=deposit_type,
#                 reference_no=reference_no
#             )

#             # Create CustodyCustomItems instance
#             CustodyCustomItems.objects.create(
#                 custody_custom=custody_custom_instance,
#                 product=product,
#                 quantity=quantity,
#                 serialnumber=serialnumber,
#                 amount=total_amount,
#                 can_deposite_chrge=can_deposite_chrge,
#                 five_gallon_water_charge=five_gallon_water_charge,
#                 amount_collected=amount_collected
#             )

#             try:
#                 stock_instance = CustomerCustodyStock.objects.get(customer=customer, product=product)
#                 stock_instance.agreement_no += ', ' + agreement_no
#                 stock_instance.serialnumber += ', ' + serialnumber
#                 stock_instance.amount += total_amount
#                 stock_instance.quantity += quantity
#                 stock_instance.save()
#             except CustomerCustodyStock.DoesNotExist:
#                 CustomerCustodyStock.objects.create(
#                     customer=customer,
#                     agreement_no=agreement_no,
#                     deposit_type=deposit_type,
#                     reference_no=reference_no,
#                     product=product,
#                     quantity=quantity,
#                     serialnumber=serialnumber,
#                     amount=total_amount,
#                     can_deposite_chrge=can_deposite_chrge,
#                     five_gallon_water_charge=five_gallon_water_charge,
#                     amount_collected=amount_collected
#                 )

#             if product.product_name.lower() == "5 gallon":
#                 random_part = str(random.randint(1000, 9999))
#                 invoice_number = f'WTR-{random_part}'

#                 net_taxable = total_amount
#                 discount = 0  
#                 amount_total = total_amount + can_deposite_chrge + five_gallon_water_charge
#                 amount_received = amount_collected

#                 invoice_instance = Invoice.objects.create(
#                     invoice_no=invoice_number,
#                     created_date=datetime.today(),
#                     net_taxable=net_taxable,
#                     discount=discount,
#                     amount_total=total_amount,
#                     amount_received=amount_collected,
#                     customer=customer,
#                     reference_no=reference_no
#                 )
                
#                 if invoice_instance.amount_total == invoice_instance.amount_received:
#                     invoice_instance.invoice_status = "paid"
#                     invoice_instance.save()

#                 InvoiceItems.objects.create(
#                     category=product.category,
#                     product_items=product,
#                     qty=quantity,
#                     rate=product.rate,
#                     invoice=invoice_instance,
#                     remarks='Invoice generated from custody item creation'
#                 )

#                 # Create daily collection record
#                 InvoiceDailyCollection.objects.create(
#                     invoice=invoice_instance,
#                     created_date=datetime.today(),
#                     customer=invoice_instance.customer,
#                     salesman=request.user,
#                     amount=invoice_instance.amount_received,
#                 )

#             return Response({'status': True, 'message': 'Created Successfully'})
#         except Exception as e:
#             print(e)
#             return Response({'status': False, 'data': str(e), 'message': 'Something went wrong!'})

class CustodyCustomAPIView(APIView):
    def post(self, request):
        try:
            customer = Customers.objects.get(customer_id=request.data['customer_id'])
            agreement_no = request.data['agreement_no']
            total_amount = int(request.data['total_amount'])
            deposit_type = request.data['deposit_type']
            reference_no = request.data['reference_no']
            product = ProdutItemMaster.objects.get(id=request.data['product_id'])
            quantity = int(request.data['quantity'])
            serialnumber = request.data['serialnumber']
            amount_collected = request.data['amount_collected']
            can_deposite_chrge = request.data.get('can_deposite_chrge', 0)
            
            # Calculate the five_gallon_water_charge based on the quantity and customer's rate
            five_gallon_water_charge = quantity * float(customer.rate)
            
            vanstock = VanProductStock.objects.get(created_date=datetime.today().date(),product=product,van__salesman=request.user)
                    
            if vanstock.stock >= quantity:

                # Create CustodyCustom instance
                custody_custom_instance = CustodyCustom.objects.create(
                    customer=customer,
                    agreement_no=agreement_no,
                    total_amount=total_amount,
                    deposit_type=deposit_type,
                    reference_no=reference_no,
                    amount_collected=amount_collected,
                    created_by=request.user.pk,
                    created_date=datetime.today(),
                )

                # Create CustodyCustomItems instance
                CustodyCustomItems.objects.create(
                    custody_custom=custody_custom_instance,
                    product=product,
                    quantity=quantity,
                    serialnumber=serialnumber,
                    amount=total_amount,
                    can_deposite_chrge=can_deposite_chrge,
                    five_gallon_water_charge=five_gallon_water_charge
                )

                try:
                    stock_instance = CustomerCustodyStock.objects.get(customer=customer, product=product)
                    stock_instance.agreement_no += ', ' + agreement_no
                    stock_instance.serialnumber += ', ' + serialnumber
                    stock_instance.amount += total_amount
                    stock_instance.quantity += quantity
                    stock_instance.save()
                except CustomerCustodyStock.DoesNotExist:
                    CustomerCustodyStock.objects.create(
                        customer=customer,
                        agreement_no=agreement_no,
                        deposit_type=deposit_type,
                        reference_no=reference_no,
                        product=product,
                        quantity=quantity,
                        serialnumber=serialnumber,
                        amount=total_amount,
                        can_deposite_chrge=can_deposite_chrge,
                        five_gallon_water_charge=five_gallon_water_charge,
                        amount_collected=amount_collected
                    )
                    
                vanstock.stock -= quantity
                if customer.sales_type != "FOC" :
                    vanstock.sold_count += quantity
                if customer.sales_type == "FOC" :
                    vanstock.foc += quantity
                # if product.product_name == "5 Gallon" :
                    # total_fivegallon_qty += Decimal(quantity)
                    # vanstock.empty_can_count += collected_empty_bottle
                vanstock.save()

                if product.product_name.lower() == "5 gallon":
                    date_part = timezone.now().strftime('%Y%m%d')
                    try:
                        invoice_last_no = Invoice.objects.filter(is_deleted=False).latest('created_date')
                        last_invoice_number = invoice_last_no.invoice_no

                        # Validate the format of the last invoice number
                        parts = last_invoice_number.split('-')
                        if len(parts) == 3 and parts[0] == 'WTR' and parts[1] == date_part:
                            prefix, old_date_part, number_part = parts
                            new_number_part = int(number_part) + 1
                            invoice_number = f'{prefix}-{date_part}-{new_number_part:04d}'
                        else:
                            # If the last invoice number is not in the expected format, generate a new one
                            random_part = str(random.randint(1000, 9999))
                            invoice_number = f'WTR-{date_part}-{random_part}'
                    except Invoice.DoesNotExist:
                        random_part = str(random.randint(1000, 9999))
                        invoice_number = f'WTR-{date_part}-{random_part}'

                    net_taxable = total_amount
                    discount = 0  
                    amount_total = total_amount
                    amount_received = amount_collected

                    invoice_instance = Invoice.objects.create(
                        invoice_no=invoice_number,
                        created_date=datetime.today(),
                        net_taxable=net_taxable,
                        discount=discount,
                        amout_total=amount_total,  # Corrected field name
                        amout_recieved=amount_received,  # Corrected field name
                        customer=customer,
                        reference_no=reference_no
                    )
                    
                    if invoice_instance.amout_total == invoice_instance.amout_recieved:
                        invoice_instance.invoice_status = "paid"
                        invoice_instance.save()

                    InvoiceItems.objects.create(
                        category=product.category,
                        product_items=product,
                        qty=quantity,
                        rate=product.rate,
                        invoice=invoice_instance,
                        remarks='Invoice generated from custody item creation'
                    )

                    # Create daily collection record
                    InvoiceDailyCollection.objects.create(
                        invoice=invoice_instance,
                        created_date=datetime.today(),
                        customer=invoice_instance.customer,
                        salesman=request.user,
                        amount=invoice_instance.amout_recieved,
                    )

                return Response({'status': True, 'message': 'Created Successfully'})
            
            else:
                status_code = status.HTTP_400_BAD_REQUEST
                response_data = {
                    "status": "false",
                    "title": "Failed",
                    "message": f"No stock available in {product.product_name}, only {vanstock.stock} left",
                }
                return Response(response_data, status=status_code)
            
        except Exception as e:
            return Response({'status': False, 'data': str(e), 'message': str(e)})

class supply_product(APIView):
    def get(self, request, *args, **kwargs):
        route_id = request.GET.get("route_id")
        customer_id = request.query_params.get("customer_id")

        customers = Customers.objects.all()

        if route_id:
            customers = customers.filter(routes__pk=route_id)
            
        if customer_id:
            customers = customers.filter(pk=customer_id)
            
        serializer = SupplyItemCustomersSerializer(customers, many=True, context={"request": request})

        status_code = status.HTTP_200_OK
        response_data = {
            "status": status_code,
            "StatusCode": 6000,
            "data": serializer.data,
        }

        return Response(response_data, status_code)

# @api_view(['GET'])
# def supply_product(request):
#     if (instances:=VanProductStock.objects.filter(product__pk=product_id)).exists():
#         product = instances.first().product
#         customer = Customers.objects.get(pk=customer_id)

#         if product.product_name.product_name=="5 Gallon":
#             serializer = SupplyItemFiveCanWaterProductGetSerializer(product, many=False, context={"request": request,"customer":customer.pk})
#         else:
#             serializer = SupplyItemProductGetSerializer(product, many=False, context={"request": request,"customer":customer.pk})

#         status_code = status.HTTP_200_OK
#         response_data = {
#             "status": status_code,
#             "StatusCode": 6000,
#             "data": serializer.data,
#         }
#     else:
#         status_code = status.HTTP_400_BAD_REQUEST
#         response_data = {
#             "status": status_code,
#             "StatusCode": 6001,
#             "message": "No data",
#         }

#     return Response(response_data, status_code)

class create_customer_supply(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Extract data from the request
        customer_supply_data = request.data.get('customer_supply')
        items_data = request.data.get('items')
        collected_empty_bottle = request.data.get('collected_empty_bottle')
        allocate_bottle_to_pending = request.data.get('allocate_bottle_to_pending')
        allocate_bottle_to_custody = request.data.get('allocate_bottle_to_custody')
        allocate_bottle_to_paid = request.data.get('allocate_bottle_to_paid')
        allocate_bottle_to_free = int(request.data.get('allocate_bottle_to_free') or 0)
        reference_no = request.data.get('reference_number')
        date_part = timezone.now().strftime('%Y%m%d')
        
        customer_outstanding_coupon = None
        customer_outstanding_empty_can = None
        customer_outstanding_amount = None
        
        try:
            with transaction.atomic():
                # Create CustomerSupply instance
                customer_supply = CustomerSupply.objects.create(
                    customer_id=customer_supply_data['customer'],
                    salesman_id=customer_supply_data['salesman'],
                    grand_total=customer_supply_data['grand_total'],
                    discount=customer_supply_data['discount'],
                    net_payable=customer_supply_data['net_payable'],
                    vat=customer_supply_data['vat'],
                    subtotal=customer_supply_data['subtotal'],
                    amount_recieved=customer_supply_data['amount_recieved'],
                    reference_number=reference_no,
                    collected_empty_bottle=collected_empty_bottle,
                    allocate_bottle_to_pending=allocate_bottle_to_pending,
                    allocate_bottle_to_custody=allocate_bottle_to_custody,
                    allocate_bottle_to_paid=allocate_bottle_to_paid,
                    allocate_bottle_to_free=allocate_bottle_to_free,
                    created_by=request.user.id,
                    created_date=datetime.today()
                )

                # Create CustomerSupplyItems instances
                total_fivegallon_qty = 0
                van = Van.objects.get(salesman=request.user)
                
                for item_data in items_data:
                    suply_items = CustomerSupplyItems.objects.create(
                        customer_supply=customer_supply,
                        product_id=item_data['product'],
                        quantity=item_data['quantity'],
                        amount=item_data['amount']
                    )
                    
                    vanstock = VanProductStock.objects.get(created_date=datetime.today().date(),product=suply_items.product,van=van)
                    
                    if vanstock.stock >= item_data['quantity']:
                    
                        vanstock.stock -= suply_items.quantity
                        if customer_supply.customer.sales_type != "FOC" :
                            vanstock.sold_count += suply_items.quantity
                        
                        if customer_supply.customer.sales_type == "FOC" :
                            vanstock.foc += suply_items.quantity
                        
                        if suply_items.product.product_name == "5 Gallon" :
                            total_fivegallon_qty += Decimal(suply_items.quantity)
                            vanstock.empty_can_count += collected_empty_bottle
                            
                            if customer_supply.customer.customer_type == "WATCHMAN" :
                                vanstock.foc += customer_supply.allocate_bottle_to_free
                        vanstock.save()
                        
                    else:
                        status_code = status.HTTP_400_BAD_REQUEST
                        response_data = {
                            "status": "false",
                            "title": "Failed",
                            "message": f"No stock available in {vanstock.product.product_name}, only {vanstock.stock} left",
                        }
                        return Response(response_data, status=status_code)
                        
                
                if allocate_bottle_to_custody > 0:
                    custody_instance = CustodyCustom.objects.create(
                        customer=customer_supply.customer,
                        created_by=request.user.id,
                        created_date=datetime.today(),
                        deposit_type="non_deposit",
                        reference_no=f"supply {customer_supply.customer.custom_id} - {customer_supply.created_date}"
                    )

                    CustodyCustomItems.objects.create(
                        product=ProdutItemMaster.objects.get(product_name="5 Gallon"),
                        quantity=allocate_bottle_to_custody,
                        custody_custom=custody_instance
                    )
                    
                    custody_stock, created = CustomerCustodyStock.objects.get_or_create(
                        customer=customer_supply.customer,
                        product=ProdutItemMaster.objects.get(product_name="5 Gallon"),
                    )
                    custody_stock.reference_no = f"supply {customer_supply.customer.custom_id} - {customer_supply.created_date}"   
                    custody_stock.quantity = allocate_bottle_to_custody
                    custody_stock.save()
                    
                    if (bottle_count := BottleCount.objects.filter(van=van, created_date__date=customer_supply.created_date.date())).exists():
                        bottle_count = bottle_count.first()
                        bottle_count.custody_issue += allocate_bottle_to_custody
                        bottle_count.save()
                    
                invoice_generated = False
                
                if customer_supply.customer.sales_type != "FOC" :
                    # empty bottle calculate
                    if total_fivegallon_qty < Decimal(customer_supply.collected_empty_bottle) :
                        balance_empty_bottle = Decimal(collected_empty_bottle) - total_fivegallon_qty
                        if CustomerOutstandingReport.objects.filter(customer=customer_supply.customer,product_type="emptycan").exists():
                            outstanding_instance = CustomerOutstandingReport.objects.get(customer=customer_supply.customer,product_type="emptycan")
                            outstanding_instance.value -= Decimal(balance_empty_bottle)
                            outstanding_instance.save()
                    
                    elif total_fivegallon_qty > Decimal(customer_supply.collected_empty_bottle) :
                        balance_empty_bottle = total_fivegallon_qty - Decimal(customer_supply.collected_empty_bottle)
                        customer_outstanding_empty_can = CustomerOutstanding.objects.create(
                            customer=customer_supply.customer,
                            product_type="emptycan",
                            created_by=request.user.id,
                            created_date=datetime.today(),
                        )

                        outstanding_product = OutstandingProduct.objects.create(
                            empty_bottle=balance_empty_bottle,
                            customer_outstanding=customer_outstanding_empty_can,
                        )
                        outstanding_instance = {}

                        try:
                            outstanding_instance=CustomerOutstandingReport.objects.get(customer=customer_supply.customer,product_type="emptycan")
                            outstanding_instance.value += Decimal(outstanding_product.empty_bottle)
                            outstanding_instance.save()
                        except:
                            outstanding_instance = CustomerOutstandingReport.objects.create(
                                product_type='emptycan',
                                value=outstanding_product.empty_bottle,
                                customer=outstanding_product.customer_outstanding.customer
                            )
                
                    supply_items = CustomerSupplyItems.objects.filter(customer_supply=customer_supply) # supply items
                    
                    # Update CustomerSupplyStock
                    for item_data in supply_items:
                        customer_supply_stock, _ = CustomerSupplyStock.objects.get_or_create(
                            customer=customer_supply.customer,
                            product=item_data.product,
                        )
                        
                        customer_supply_stock.stock_quantity += item_data.quantity
                        customer_supply_stock.save()
                        
                        if Customers.objects.get(pk=customer_supply_data['customer']).sales_type == "CASH COUPON" :
                            # print("cash coupon")
                            total_coupon_collected = request.data.get('total_coupon_collected')
                            
                            if request.data.get('coupon_method') == "manual" :
                                collected_coupon_ids = request.data.get('collected_coupon_ids')
                                
                                customer_supply_coupon = CustomerSupplyCoupon.objects.create(
                                    customer_supply=customer_supply,
                                )
                                for c_id in collected_coupon_ids:
                                    if CouponLeaflet.objects.filter(pk=c_id).exists():
                                        leaflet_instance = CouponLeaflet.objects.get(pk=c_id)
                                        customer_supply_coupon.leaf.add(leaflet_instance)
                                        leaflet_instance.used=True
                                        leaflet_instance.save()
                                    else:
                                        leaflet_instance = FreeLeaflet.objects.get(pk=c_id)
                                        customer_supply_coupon.free_leaf.add(leaflet_instance)
                                        leaflet_instance.used=True
                                        leaflet_instance.save()
                                    
                                    if CustomerCouponStock.objects.filter(customer__pk=customer_supply_data['customer'],coupon_method="manual",coupon_type_id=leaflet_instance.coupon.coupon_type).exists() :
                                        customer_stock = CustomerCouponStock.objects.get(customer__pk=customer_supply_data['customer'],coupon_method="manual",coupon_type_id=leaflet_instance.coupon.coupon_type)
                                        customer_stock.count -= 1
                                        customer_stock.save()
                                        
                                if total_fivegallon_qty < len(collected_coupon_ids):
                                    balance_coupon = Decimal(total_fivegallon_qty) - Decimal(len(collected_coupon_ids))
                                    
                                    customer_outstanding_coupon = CustomerOutstanding.objects.create(
                                        customer=customer_supply.customer,
                                        product_type="coupons",
                                        created_by=request.user.id,
                                        created_date=datetime.today()
                                    )
                                    
                                    if (customer_coupon:=CustomerCouponStock.objects.filter(customer__pk=customer_supply_data['customer'],coupon_method="manual")).exists():
                                        customer_coupon_type = customer_coupon.first().coupon_type_id
                                    else:
                                        customer_coupon_type = CouponType.objects.get(coupon_type_name="Digital")
                                    outstanding_coupon = OutstandingCoupon.objects.create(
                                        count=balance_coupon,
                                        customer_outstanding=customer_outstanding_coupon,
                                        coupon_type=customer_coupon_type
                                    )
                                    outstanding_instance = ""

                                    try:
                                        outstanding_instance=CustomerOutstandingReport.objects.get(customer=customer_supply.customer,product_type="coupons")
                                        outstanding_instance.value += Decimal(outstanding_coupon.count)
                                        outstanding_instance.save()
                                    except:
                                        outstanding_instance = CustomerOutstandingReport.objects.create(
                                            product_type='coupons',
                                            value=outstanding_coupon.count,
                                            customer=outstanding_coupon.customer_outstanding.customer
                                        )
                                
                                elif total_fivegallon_qty > len(collected_coupon_ids) :
                                    balance_coupon = total_fivegallon_qty - len(collected_coupon_ids)
                                    
                                    customer_outstanding_coupon = CustomerOutstanding.objects.create(
                                        customer=customer_supply.customer,
                                        product_type="coupons",
                                        created_by=request.user.id,
                                        created_date=datetime.today()
                                    )
                                    
                                    if (customer_coupon:=CustomerCouponStock.objects.filter(customer__pk=customer_supply_data['customer'],coupon_method="manual")).exists():
                                        customer_coupon_type = customer_coupon.first().coupon_type_id
                                    else:
                                        customer_coupon_type = CouponType.objects.get(coupon_type_name="Digital")
                                    outstanding_coupon = OutstandingCoupon.objects.create(
                                        count=balance_coupon,
                                        customer_outstanding=customer_outstanding_coupon,
                                        coupon_type=customer_coupon_type
                                    )
                                    outstanding_instance = ""
                                    
                                    try :
                                        outstanding_instance=CustomerOutstandingReport.objects.get(customer=customer_supply.customer,product_type="coupons")
                                        outstanding_instance.value += Decimal(balance_coupon)
                                        outstanding_instance.save()
                                    except:
                                        outstanding_instance=CustomerOutstandingReport.objects.create(
                                            product_type="coupons",
                                            value=balance_coupon,
                                            customer=customer_supply.customer,
                                            )
                                        
                            elif request.data.get('coupon_method') == "digital" :
                                try : 
                                    customer_coupon_digital = CustomerSupplyDigitalCoupon.objects.get(
                                        customer_supply=customer_supply,
                                        )
                                except:
                                    customer_coupon_digital = CustomerSupplyDigitalCoupon.objects.create(
                                        customer_supply=customer_supply,
                                        count = 0,
                                        )
                                customer_coupon_digital.count += total_coupon_collected
                                customer_coupon_digital.save()
                                
                                customer_stock = CustomerCouponStock.objects.get(customer__pk=customer_supply_data['customer'],coupon_method="digital",coupon_type_id__coupon_type_name="Digital")
                                customer_stock.count -= Decimal(total_coupon_collected)
                                customer_stock.save()
                                
                                if total_fivegallon_qty < Decimal(total_coupon_collected):
                                    balance_coupon = Decimal(total_fivegallon_qty) - Decimal(total_coupon_collected)
                                    
                                    customer_outstanding_coupon = CustomerOutstanding.objects.create(
                                        customer=customer_supply.customer,
                                        product_type="coupons",
                                        created_by=request.user.id,
                                        created_date=datetime.today()
                                    )
                                    
                                    customer_coupon_type = CouponType.objects.get(coupon_type_name="Digital")
                                    outstanding_coupon = OutstandingCoupon.objects.create(
                                        count=balance_coupon,
                                        customer_outstanding=customer_outstanding_coupon,
                                        coupon_type=customer_coupon_type
                                    )
                                    outstanding_instance = ""

                                    try:
                                        outstanding_instance=CustomerOutstandingReport.objects.get(customer=customer_supply.customer,product_type="coupons")
                                        outstanding_instance.value += Decimal(outstanding_coupon.count)
                                        outstanding_instance.save()
                                    except:
                                        outstanding_instance = CustomerOutstandingReport.objects.create(
                                            product_type='coupons',
                                            value=outstanding_coupon.count,
                                            customer=outstanding_coupon.customer_outstanding.customer
                                        )
                                
                                elif total_fivegallon_qty > Decimal(total_coupon_collected) :
                                    balance_coupon = total_fivegallon_qty - Decimal(total_coupon_collected)
                                    
                                    customer_outstanding_coupon = CustomerOutstanding.objects.create(
                                        customer=customer_supply.customer,
                                        product_type="coupons",
                                        created_by=request.user.id,
                                        created_date=datetime.today()
                                    )
                                    
                                    customer_coupon_type = CouponType.objects.get(coupon_type_name="Digital")
                                    outstanding_coupon = OutstandingCoupon.objects.create(
                                        count=balance_coupon,
                                        customer_outstanding=customer_outstanding_coupon,
                                        coupon_type=customer_coupon_type
                                    )
                                    outstanding_instance = ""
                                    
                                    try :
                                        outstanding_instance=CustomerOutstandingReport.objects.get(customer=customer_supply.customer,product_type="coupons")
                                        outstanding_instance.value += Decimal(balance_coupon)
                                        outstanding_instance.save()
                                    except:
                                        outstanding_instance=CustomerOutstandingReport.objects.create(
                                            product_type="coupons",
                                            value=balance_coupon,
                                            customer=customer_supply.customer,
                                            )
                        elif Customers.objects.get(pk=customer_supply_data['customer']).sales_type == "CASH" or Customers.objects.get(pk=customer_supply_data['customer']).sales_type == "CREDIT" :
                            if customer_supply.amount_recieved < customer_supply.subtotal:
                                balance_amount = customer_supply.subtotal - customer_supply.amount_recieved
                                
                                customer_outstanding_amount = CustomerOutstanding.objects.create(
                                    product_type="amount",
                                    created_by=request.user.id,
                                    customer=customer_supply.customer,
                                    created_date=datetime.today()
                                )

                                outstanding_amount = OutstandingAmount.objects.create(
                                    amount=balance_amount,
                                    customer_outstanding=customer_outstanding_amount,
                                )
                                outstanding_instance = {}

                                try:
                                    outstanding_instance=CustomerOutstandingReport.objects.get(customer=customer_supply.customer,product_type="amount")
                                    outstanding_instance.value += Decimal(outstanding_amount.amount)
                                    outstanding_instance.save()
                                except:
                                    outstanding_instance = CustomerOutstandingReport.objects.create(
                                        product_type='amount',
                                        value=outstanding_amount.amount,
                                        customer=outstanding_amount.customer_outstanding.customer
                                    )
                                    
                            elif customer_supply.amount_recieved > customer_supply.subtotal:
                                balance_amount = customer_supply.amount_recieved - customer_supply.subtotal
                                
                                customer_outstanding_amount = CustomerOutstanding.objects.create(
                                    product_type="amount",
                                    created_by=request.user.id,
                                    customer=customer_supply.customer,
                                )

                                outstanding_amount = OutstandingAmount.objects.create(
                                    amount=balance_amount,
                                    customer_outstanding=customer_outstanding_amount,
                                )
                                
                                outstanding_instance=CustomerOutstandingReport.objects.get(customer=customer_supply.customer,product_type="amount")
                                outstanding_instance.value -= Decimal(balance_amount)
                                outstanding_instance.save()
                                
                        # elif Customers.objects.get(pk=customer_supply_data['customer']).sales_type == "CREDIT" :
                            # pass
                    
                    # if customer_supply.customer.sales_type == "CASH" or customer_supply.customer.sales_type == "CREDIT":
                    # Generate a unique receipt number
                    try:
                        reciept_last_no = Receipt.objects.all().latest('created_date')
                        last_reciept_number = reciept_last_no.receipt_number

                        # Validate the format of the last invoice number
                        parts = last_reciept_number.split('-')
                        if len(parts) == 3 and parts[0] == 'RCT' and parts[1] == date_part:
                            prefix, old_date_part, number_part = parts
                            r_new_number_part = int(number_part) + 1
                            receipt_number = f'{prefix}-{date_part}-{r_new_number_part:04d}'
                        else:
                            # If the last invoice number is not in the expected format, generate a new one
                            random_part = str(random.randint(1000, 9999))
                            receipt_number = f'RCT-{date_part}-{random_part}'
                    except Receipt.DoesNotExist:
                        random_part = str(random.randint(1000, 9999))
                        receipt_number = f'RCT-{date_part}-{random_part}'
                    
                    invoice_generated = True
                    
                    try:
                        invoice_last_no = Invoice.objects.filter(is_deleted=False).latest('created_date')
                        last_invoice_number = invoice_last_no.invoice_no

                        # Validate the format of the last invoice number
                        parts = last_invoice_number.split('-')
                        if len(parts) == 3 and parts[0] == 'WTR' and parts[1] == date_part:
                            prefix, old_date_part, number_part = parts
                            new_number_part = int(number_part) + 1
                            invoice_number = f'{prefix}-{date_part}-{new_number_part:04d}'
                        else:
                            # If the last invoice number is not in the expected format, generate a new one
                            random_part = str(random.randint(1000, 9999))
                            invoice_number = f'WTR-{date_part}-{random_part}'
                    except Invoice.DoesNotExist:
                        random_part = str(random.randint(1000, 9999))
                        invoice_number = f'WTR-{date_part}-{random_part}'
                    
                    # Create the invoice
                    invoice = Invoice.objects.create(
                        invoice_no=invoice_number,
                        created_date=datetime.today(),
                        net_taxable=customer_supply.net_payable,
                        vat=customer_supply.vat,
                        discount=customer_supply.discount,
                        amout_total=customer_supply.subtotal,
                        amout_recieved=customer_supply.amount_recieved,
                        customer=customer_supply.customer,
                        reference_no=reference_no
                    )
                    
                    customer_supply.invoice_no = invoice.invoice_no
                    customer_supply.save()
                    
                    if customer_outstanding_empty_can:
                        customer_outstanding_empty_can.invoice_no = invoice.invoice_no
                        customer_outstanding_empty_can.save()
                        
                    # print("customer_outstanding_coupon",customer_outstanding_coupon)

                    if customer_outstanding_coupon:
                        customer_outstanding_coupon.invoice_no = invoice.invoice_no
                        customer_outstanding_coupon.save()

                    if customer_outstanding_amount:
                        customer_outstanding_amount.invoice_no = invoice.invoice_no
                        customer_outstanding_amount.save()
                    
                    if customer_supply.customer.sales_type == "CREDIT":
                        invoice.invoice_type = "credit_invoive"
                        invoice.save()

                    # Create invoice items
                    for item_data in supply_items:
                        item = CustomerSupplyItems.objects.get(pk=item_data.pk)
                        
                        if item.product.product_name == "5 Gallon":
                            if VanProductStock.objects.filter(created_date=datetime.today().date(),product=item.product,van__salesman=request.user).exists():
                                vanstock = VanProductStock.objects.get(created_date=datetime.today().date(),product=item.product,van=van)
                                vanstock.pending_count += item.customer_supply.allocate_bottle_to_pending
                                vanstock.save()
                            else:
                                status_code = status.HTTP_400_BAD_REQUEST
                                response_data = {
                                    "status": "false",
                                    "title": "Failed",
                                    "message": f"No stock available in this van",
                                }
                                return Response(response_data, status=status_code)
                            
                        
                        InvoiceItems.objects.create(
                            category=item.product.category,
                            product_items=item.product,
                            qty=item.quantity,
                            rate=item.amount,
                            invoice=invoice,
                            remarks='invoice genereted from supply items reference no : ' + invoice.reference_no
                        )
                        # print("invoice generate")
                        InvoiceDailyCollection.objects.create(
                            invoice=invoice,
                            created_date=datetime.today(),
                            customer=invoice.customer,
                            salesman=request.user,
                            amount=invoice.amout_recieved,
                        )

                    DiffBottlesModel.objects.filter(
                        delivery_date__date=date.today(),
                        assign_this_to=customer_supply.salesman_id,
                        customer=customer_supply.customer_id
                        ).update(status='supplied')
                    
                    invoice_numbers = []
                    invoice_numbers.append(invoice.invoice_no)
                    
                    receipt = Receipt.objects.create(
                        transaction_type="supply",
                        instance_id=str(customer_supply.id),  
                        amount_received=customer_supply.amount_recieved,
                        receipt_number=receipt_number,
                        customer=customer_supply.customer,
                        invoice_number=",".join(invoice_numbers)
                    )
                else:
                    if customer_supply.customer.eligible_foc > 0:
                        foc_count = min(customer_supply.customer.eligible_foc, suply_items.quantity)
                        sold_count = suply_items.quantity - foc_count
                        customer_supply.customer.eligible_foc -= foc_count  
                        customer_supply.customer.save()
                    else:
                        foc_count = 0
                        sold_count = suply_items.quantity

                    
                if invoice_generated:
                    response_data = {
                        "status": "true",
                        "title": "Successfully Created",
                        "message": "Customer Supply created successfully and Invoice generated.",
                        "invoice_id": str(invoice.invoice_no)
                    }
                    return Response(response_data, status=status.HTTP_201_CREATED)
                
                else:
                    response_data = {
                        "status": "true",
                        "title": "Successfully Created",
                        "message": "Customer Supply created successfully.",
                    }
                    return Response(response_data, status=status.HTTP_201_CREATED)

        except IntegrityError as e:
            # Handle database integrity error
            response_data = {
                "status": "false",
                "title": "Failed",
                "message": str(e),
            }

        except Exception as e:
            # Handle other exceptions
            response_data = {
                "status": "false",
                "title": "Failed",
                "message": str(e),
            }
        return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class edit_customer_supply(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request,pk, *args, **kwargs):
        try:
            supply_instance = CustomerSupply.objects.get(pk=pk)
            supply_items_instances = CustomerSupplyItems.objects.filter(customer_supply=supply_instance)

            supply_data = {
                "customer_supply": {
                    "customer": str(supply_instance.customer.pk),
                    "salesman": str(supply_instance.salesman.pk),
                    "grand_total": supply_instance.grand_total,
                    "discount": supply_instance.discount,
                    "net_payable": supply_instance.net_payable,
                    "vat": supply_instance.vat,
                    "subtotal": supply_instance.subtotal,
                    "amount_recieved": supply_instance.amount_recieved
                },
                "items": [
                    {
                        "product": str(item.product.id),
                        "quantity": item.quantity,
                        "amount": item.amount
                    }
                    for item in supply_items_instances
                ],
                "collected_empty_bottle": supply_instance.collected_empty_bottle,
                "allocate_bottle_to_pending": supply_instance.allocate_bottle_to_pending,
                "allocate_bottle_to_custody": supply_instance.allocate_bottle_to_custody,
                "allocate_bottle_to_paid": supply_instance.allocate_bottle_to_paid,
                "reference_number": supply_instance.reference_number,
                # "total_coupon_collected": supply_instance.total_coupon_collected,
                # "collected_coupon_ids": [
                #     str(coupon.id) for coupon in supply_instance.collected_coupon_ids.all()
                # ]
            }

            return Response(supply_data, status=status.HTTP_200_OK)

        except CustomerSupply.DoesNotExist:
            return Response({"detail": "Customer Supply not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def post(self, request,pk, *args, **kwargs):
        try:
            with transaction.atomic():
                old_supply_date = CustomerSupply.objects.get(pk=pk).created_date
                
                supply_instance = CustomerSupply.objects.get(pk=pk)
                supply_items_instances = CustomerSupplyItems.objects.filter(customer_supply=supply_instance)
                five_gallon_qty = supply_items_instances.filter(product__product_name="5 Gallon").aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
                
                DiffBottlesModel.objects.filter(
                    delivery_date__date=supply_instance.created_date.date(),
                    assign_this_to=supply_instance.salesman,
                    customer=supply_instance.customer_id
                    ).update(status='pending')
                
                invoice_instance = Invoice.objects.get(created_date__date=supply_instance.created_date.date(),customer=supply_instance.customer,reference_no=supply_instance.reference_number)
                invoice_items_instances = InvoiceItems.objects.filter(invoice=invoice_instance)
                InvoiceDailyCollection.objects.filter(
                    invoice=invoice_instance,
                    created_date__date=supply_instance.created_date.date(),
                    customer=supply_instance.customer,
                    salesman=supply_instance.salesman
                    ).delete()
                invoice_items_instances.delete()
                invoice_instance.delete()
                
                balance_amount = supply_instance.subtotal - supply_instance.amount_recieved
                if supply_instance.amount_recieved < supply_instance.subtotal:
                    OutstandingAmount.objects.filter(
                        customer_outstanding__product_type="amount",
                        customer_outstanding__customer=supply_instance.customer,
                        customer_outstanding__created_by=supply_instance.salesman.pk,
                        customer_outstanding__created_date=supply_instance.created_date,
                        amount=balance_amount
                    ).delete()
                    
                    customer_outstanding_report_instance=CustomerOutstandingReport.objects.get(customer=supply_instance.customer,product_type="amount")
                    customer_outstanding_report_instance.value -= Decimal(balance_amount)
                    customer_outstanding_report_instance.save()
                    
                elif supply_instance.amount_recieved > supply_instance.subtotal:
                    OutstandingAmount.objects.filter(
                        customer_outstanding__product_type="amount",
                        customer_outstanding__customer=supply_instance.customer,
                        customer_outstanding__created_by=supply_instance.salesman.pk,
                        customer_outstanding__created_date=supply_instance.created_date,
                        amount=balance_amount
                    ).delete()
                    
                    customer_outstanding_report_instance=CustomerOutstandingReport.objects.get(customer=supply_instance.customer,product_type="amount")
                    customer_outstanding_report_instance.value += Decimal(balance_amount)
                    customer_outstanding_report_instance.save()
                    
                if (digital_coupons_instances:=CustomerSupplyDigitalCoupon.objects.filter(customer_supply=supply_instance)).exists():
                    digital_coupons_instance = digital_coupons_instances.first()
                    CustomerCouponStock.objects.get(
                        coupon_method="digital",
                        customer=supply_instance.customer,
                        coupon_type_id__coupon_type_name="Digital"
                        ).count += digital_coupons_instance.count
                
                elif (manual_coupon_instances := CustomerSupplyCoupon.objects.filter(customer_supply=supply_instance)).exists():
                    manual_coupon_instance = manual_coupon_instances.first()
                    leaflets_to_update = manual_coupon_instance.leaf.filter(used=True)
                    updated_count = leaflets_to_update.count()

                    if updated_count > 0:
                        first_leaflet = leaflets_to_update.first()

                        if first_leaflet and CustomerCouponStock.objects.filter(
                                customer=supply_instance.customer,
                                coupon_method="manual",
                                coupon_type_id=first_leaflet.coupon.coupon_type
                            ).exists():
                            # Update the CustomerCouponStock
                            customer_stock_instance = CustomerCouponStock.objects.get(
                                customer=supply_instance.customer,
                                coupon_method="manual",
                                coupon_type_id=first_leaflet.coupon.coupon_type
                            )
                            customer_stock_instance.count += Decimal(updated_count)
                            customer_stock_instance.save()
                            
                            if five_gallon_qty < Decimal(supply_instance.collected_empty_bottle) :
                                balance_empty_bottle = Decimal(supply_instance.collected_empty_bottle) - five_gallon_qty
                                if CustomerOutstandingReport.objects.filter(customer=supply_instance.customer,product_type="emptycan").exists():
                                    outstanding_instance = CustomerOutstandingReport.objects.get(customer=supply_instance.customer,product_type="emptycan")
                                    outstanding_instance.value += Decimal(balance_empty_bottle)
                                    outstanding_instance.save()
                                    
                            elif five_gallon_qty > Decimal(supply_instance.collected_empty_bottle) :
                                balance_empty_bottle = five_gallon_qty - Decimal(supply_instance.collected_empty_bottle)
                                
                                outstanding_instance = CustomerOutstanding.objects.filter(
                                    product_type="emptycan",
                                    created_by=supply_instance.salesman.pk,
                                    customer=supply_instance.customer,
                                    created_date=supply_instance.created_date,
                                ).first()

                                outstanding_product = OutstandingProduct.objects.filter(
                                    empty_bottle=balance_empty_bottle,
                                    customer_outstanding=outstanding_instance,
                                )
                                outstanding_instance = {}

                                try:
                                    outstanding_instance=CustomerOutstandingReport.objects.get(customer=supply_instance.customer,product_type="emptycan")
                                    outstanding_instance.value -= Decimal(outstanding_product.aggregate(total_empty_bottle=Sum('empty_bottle'))['total_empty_bottle'])
                                    outstanding_instance.save()
                                except:
                                    pass
                            leaflets_to_update.update(used=False)
                            outstanding_product.delete()

                for item_data in supply_items_instances:
                    if VanProductStock.objects.filter(product=item_data.product,created_date=supply_instance.created_date.date(),van__salesman=supply_instance.salesman).exists():
                        if item_data.product.product_name == "5 Gallon" :
                            # total_fivegallon_qty -= Decimal(five_gallon_qty)
                            if VanProductStock.objects.filter(product=item_data.product,created_date=supply_instance.created_date.date(),van__salesman=supply_instance.salesman).exists():
                                empty_bottle = VanProductStock.objects.get(
                                    created_date=supply_instance.created_date.date(),
                                    product=item_data.product,
                                    van__salesman=supply_instance.salesman,
                                )
                                empty_bottle.empty_can_count -= supply_instance.collected_empty_bottle
                                empty_bottle.save()
                            
                        vanstock = VanProductStock.objects.get(product=item_data.product,created_date=supply_instance.created_date.date(),van__salesman=supply_instance.salesman)
                        vanstock.stock += item_data.quantity
                        vanstock.save()
                
                supply_instance.delete()
                supply_items_instances.delete()
                    
                # edit section start here
                customer_supply_data = request.data.get('customer_supply')
                items_data = request.data.get('items')
                collected_empty_bottle = request.data.get('collected_empty_bottle')
                allocate_bottle_to_pending = request.data.get('allocate_bottle_to_pending')
                allocate_bottle_to_custody = request.data.get('allocate_bottle_to_custody')
                allocate_bottle_to_paid = request.data.get('allocate_bottle_to_paid')
                reference_no = request.data.get('reference_number')

                # Create CustomerSupply instance
                customer_supply = CustomerSupply.objects.create(
                    customer_id=customer_supply_data['customer'],
                    salesman_id=customer_supply_data['salesman'],
                    grand_total=customer_supply_data['grand_total'],
                    discount=customer_supply_data['discount'],
                    net_payable=customer_supply_data['net_payable'],
                    vat=customer_supply_data['vat'],
                    subtotal=customer_supply_data['subtotal'],
                    amount_recieved=customer_supply_data['amount_recieved'],
                    reference_number=reference_no,
                    collected_empty_bottle=collected_empty_bottle,
                    allocate_bottle_to_pending=allocate_bottle_to_pending,
                    allocate_bottle_to_custody=allocate_bottle_to_custody,
                    allocate_bottle_to_paid=allocate_bottle_to_paid,
                    created_by=request.user.id,
                    created_date=old_supply_date
                )

                # Create CustomerSupplyItems instances
                total_fivegallon_qty = 0
                van = Van.objects.get(salesman=request.user)
                
                for item_data in items_data:
                    suply_items = CustomerSupplyItems.objects.create(
                        customer_supply=customer_supply,
                        product_id=item_data['product'],
                        quantity=item_data['quantity'],
                        amount=item_data['amount']
                    )
                    
                    vanstock = VanProductStock.objects.get(created_date=customer_supply.created_date.date(),product=suply_items.product,van=van)
                    
                    if vanstock.stock >= item_data['quantity']:
                    
                        vanstock.stock -= suply_items.quantity
                        if customer_supply.customer.sales_type != "FOC" :
                            vanstock.sold_count += suply_items.quantity
                        if customer_supply.customer.sales_type == "FOC" :
                            vanstock.foc += suply_items.quantity
                        if suply_items.product.product_name == "5 Gallon" :
                            total_fivegallon_qty += Decimal(suply_items.quantity)
                            vanstock.empty_can_count += collected_empty_bottle
                        vanstock.save()
                        
                    else:
                        status_code = status.HTTP_400_BAD_REQUEST
                        response_data = {
                            "status": "false",
                            "title": "Failed",
                            "message": f"No stock available in {vanstock.product.product_name}, only {vanstock.stock} left",
                        }
                        return Response(response_data, status=status_code)
                
                # empty bottle calculate
                if total_fivegallon_qty < Decimal(customer_supply.collected_empty_bottle) :
                    balance_empty_bottle = Decimal(collected_empty_bottle) - total_fivegallon_qty
                    if CustomerOutstandingReport.objects.filter(customer=customer_supply.customer,product_type="emptycan").exists():
                        outstanding_instance = CustomerOutstandingReport.objects.get(customer=customer_supply.customer,product_type="emptycan")
                        outstanding_instance.value -= Decimal(balance_empty_bottle)
                        outstanding_instance.save()
                
                elif total_fivegallon_qty > Decimal(customer_supply.collected_empty_bottle) :
                    balance_empty_bottle = total_fivegallon_qty - Decimal(customer_supply.collected_empty_bottle)
                    customer_outstanding = CustomerOutstanding.objects.create(
                        customer=customer_supply.customer,
                        product_type="emptycan",
                        created_by=request.user.id,
                    )

                    outstanding_product = OutstandingProduct.objects.create(
                        empty_bottle=balance_empty_bottle,
                        customer_outstanding=customer_outstanding,
                    )
                    outstanding_instance = {}

                    try:
                        outstanding_instance=CustomerOutstandingReport.objects.get(customer=customer_supply.customer,product_type="emptycan")
                        outstanding_instance.value += Decimal(outstanding_product.empty_bottle)
                        outstanding_instance.save()
                    except:
                        outstanding_instance = CustomerOutstandingReport.objects.create(
                            product_type='emptycan',
                            value=outstanding_product.empty_bottle,
                            customer=outstanding_product.customer_outstanding.customer
                        )
            
                supply_items = CustomerSupplyItems.objects.filter(customer_supply=customer_supply) # supply items
                
                # Update CustomerSupplyStock
                for item_data in supply_items:
                    customer_supply_stock, _ = CustomerSupplyStock.objects.get_or_create(
                        customer=customer_supply.customer,
                        product=item_data.product,
                    )
                    
                    customer_supply_stock.stock_quantity += item_data.quantity
                    customer_supply_stock.save()
                    
                    if Customers.objects.get(pk=customer_supply_data['customer']).sales_type == "CASH COUPON" :
                        # print("cash coupon")
                        total_coupon_collected = request.data.get('total_coupon_collected')
                        
                        if request.data.get('coupon_method') == "manual" :
                            collected_coupon_ids = request.data.get('collected_coupon_ids')
                            
                            for c_id in collected_coupon_ids:
                                customer_supply_coupon = CustomerSupplyCoupon.objects.create(
                                    customer_supply=customer_supply,
                                )
                                leaflet_instance = CouponLeaflet.objects.get(pk=c_id)
                                customer_supply_coupon.leaf.add(leaflet_instance)
                                leaflet_instance.used=True
                                leaflet_instance.save()
                                
                                if CustomerCouponStock.objects.filter(customer__pk=customer_supply_data['customer'],coupon_method="manual",coupon_type_id=leaflet_instance.coupon.coupon_type).exists() :
                                    customer_stock = CustomerCouponStock.objects.get(customer__pk=customer_supply_data['customer'],coupon_method="manual",coupon_type_id=leaflet_instance.coupon.coupon_type)
                                    customer_stock.count -= Decimal(len(collected_coupon_ids))
                                    customer_stock.save()
                                    
                            if total_fivegallon_qty < len(collected_coupon_ids):
                                # print("total_fivegallon_qty < len(collected_coupon_ids)", total_fivegallon_qty, "------------------------", len(collected_coupon_ids))
                                balance_coupon = Decimal(total_fivegallon_qty) - Decimal(len(collected_coupon_ids))
                                
                                customer_outstanding = CustomerOutstanding.objects.create(
                                    customer=customer_supply.customer,
                                    product_type="coupons",
                                    created_by=request.user.id,
                                )
                                
                                customer_coupon = CustomerCouponStock.objects.filter(customer__pk=customer_supply_data['customer'],coupon_method="manual").first()
                                outstanding_coupon = OutstandingCoupon.objects.create(
                                    count=balance_coupon,
                                    customer_outstanding=customer_outstanding,
                                    coupon_type=customer_coupon.coupon_type_id
                                )
                                outstanding_instance = ""

                                try:
                                    outstanding_instance=CustomerOutstandingReport.objects.get(customer=customer_supply.customer,product_type="coupons")
                                    outstanding_instance.value += Decimal(outstanding_coupon.count)
                                    outstanding_instance.save()
                                except:
                                    outstanding_instance = CustomerOutstandingReport.objects.create(
                                        product_type='coupons',
                                        value=outstanding_coupon.count,
                                        customer=outstanding_coupon.customer_outstanding.customer
                                    )
                            
                            elif total_fivegallon_qty > len(collected_coupon_ids) :
                                balance_coupon = total_fivegallon_qty - len(collected_coupon_ids)
                                try :
                                    outstanding_instance=CustomerOutstandingReport.objects.get(customer=customer_supply.customer,product_type="coupons")
                                    outstanding_instance.value += Decimal(balance_coupon)
                                    outstanding_instance.save()
                                except:
                                    outstanding_instance=CustomerOutstandingReport.objects.create(
                                        product_type="coupons",
                                        value=balance_coupon,
                                        customer=customer_supply.customer,
                                        )
                                    
                        elif request.data.get('coupon_method') == "digital" :
                            try : 
                                customer_coupon_digital = CustomerSupplyDigitalCoupon.objects.get(
                                    customer_supply=customer_supply,
                                    )
                            except:
                                customer_coupon_digital = CustomerSupplyDigitalCoupon.objects.create(
                                    customer_supply=customer_supply,
                                    count = 0,
                                    )
                            customer_coupon_digital.count += total_coupon_collected
                            customer_coupon_digital.save()
                            
                            customer_stock = CustomerCouponStock.objects.get(customer__pk=customer_supply_data['customer'],coupon_method="digital",coupon_type_id__coupon_type_name="Digital")
                            customer_stock.count -= Decimal(total_coupon_collected)
                            customer_stock.save()
                            
                    elif Customers.objects.get(pk=customer_supply_data['customer']).sales_type == "CREDIT COUPON" :
                        pass
                    elif Customers.objects.get(pk=customer_supply_data['customer']).sales_type == "CASH" or Customers.objects.get(pk=customer_supply_data['customer']).sales_type == "CREDIT" :
                        if customer_supply.amount_recieved < customer_supply.subtotal:
                            balance_amount = customer_supply.subtotal - customer_supply.amount_recieved
                            
                            customer_outstanding = CustomerOutstanding.objects.create(
                                product_type="amount",
                                created_by=request.user.id,
                                customer=customer_supply.customer,
                            )

                            outstanding_amount = OutstandingAmount.objects.create(
                                amount=balance_amount,
                                customer_outstanding=customer_outstanding,
                            )
                            outstanding_instance = {}

                            try:
                                outstanding_instance=CustomerOutstandingReport.objects.get(customer=customer_supply.customer,product_type="amount")
                                outstanding_instance.value += Decimal(outstanding_amount.amount)
                                outstanding_instance.save()
                            except:
                                outstanding_instance = CustomerOutstandingReport.objects.create(
                                    product_type='amount',
                                    value=outstanding_amount.amount,
                                    customer=outstanding_amount.customer_outstanding.customer
                                )
                                
                        elif customer_supply.amount_recieved > customer_supply.subtotal:
                            balance_amount = customer_supply.amount_recieved - customer_supply.subtotal
                            
                            customer_outstanding = CustomerOutstanding.objects.create(
                                product_type="amount",
                                created_by=request.user.id,
                                customer=customer_supply.customer,
                            )

                            outstanding_amount = OutstandingAmount.objects.create(
                                amount=balance_amount,
                                customer_outstanding=customer_outstanding,
                            )
                            
                            outstanding_instance=CustomerOutstandingReport.objects.get(customer=customer_supply.customer,product_type="amount")
                            outstanding_instance.value -= Decimal(balance_amount)
                            outstanding_instance.save()
                            
                    # elif Customers.objects.get(pk=customer_supply_data['customer']).sales_type == "CREDIT" :
                        # pass
                invoice_generated = False
                
                if customer_supply.customer.sales_type == "CASH" or customer_supply.customer.sales_type == "CREDIT":
                    invoice_generated = True
                    
                    date_part = old_supply_date.strftime('%Y%m%d')
                    try:
                        invoice_last_no = Invoice.objects.filter(is_deleted=False).latest('created_date')
                        last_invoice_number = invoice_last_no.invoice_no

                        # Validate the format of the last invoice number
                        parts = last_invoice_number.split('-')
                        if len(parts) == 3 and parts[0] == 'WTR' and parts[1] == date_part:
                            prefix, old_date_part, number_part = parts
                            new_number_part = int(number_part) + 1
                            invoice_number = f'{prefix}-{date_part}-{new_number_part:04d}'
                        else:
                            # If the last invoice number is not in the expected format, generate a new one
                            random_part = str(random.randint(1000, 9999))
                            invoice_number = f'WTR-{date_part}-{random_part}'
                    except Invoice.DoesNotExist:
                        random_part = str(random.randint(1000, 9999))
                        invoice_number = f'WTR-{date_part}-{random_part}'
                    
                    # Create the invoice
                    invoice = Invoice.objects.create(
                        invoice_no=invoice_number,
                        created_date=old_supply_date,
                        net_taxable=customer_supply.net_payable,
                        vat=customer_supply.vat,
                        discount=customer_supply.discount,
                        amout_total=customer_supply.subtotal,
                        amout_recieved=customer_supply.amount_recieved,
                        customer=customer_supply.customer,
                        reference_no=reference_no
                    )
                    
                    customer_supply.invoice_no = invoice.invoice_no
                    customer_supply.save()
                    
                    if customer_supply.customer.sales_type == "CREDIT":
                        invoice.invoice_type = "credit_invoive"
                        invoice.save()

                    # Create invoice items
                    for item_data in supply_items:
                        item = CustomerSupplyItems.objects.get(pk=item_data.pk)
                        InvoiceItems.objects.create(
                            category=item.product.category,
                            product_items=item.product,
                            qty=item.quantity,
                            rate=item.amount,
                            invoice=invoice,
                            remarks='invoice genereted from supply items reference no : ' + invoice.reference_no
                        )
                    # print("invoice generate")
                    InvoiceDailyCollection.objects.create(
                        invoice=invoice,
                        created_date=old_supply_date,
                        customer=invoice.customer,
                        salesman=request.user,
                        amount=invoice.amout_recieved,
                    )

                DiffBottlesModel.objects.filter(
                    delivery_date__date=old_supply_date.date(),
                    assign_this_to=customer_supply.salesman_id,
                    customer=customer_supply.customer_id
                    ).update(status='supplied')

                if invoice_generated:
                    response_data = {
                        "status": "true",
                        "title": "Successfully Created",
                        "message": "Customer Supply created successfully and Invoice generated.",
                        "invoice_id": str(invoice.invoice_no)
                    }
                    return Response(response_data, status=status.HTTP_201_CREATED)
                
                else:
                    response_data = {
                        "status": "true",
                        "title": "Successfully Created",
                        "message": "Customer Supply created successfully.",
                    }
                    return Response(response_data, status=status.HTTP_201_CREATED)
        
        except IntegrityError as e:
            # Handle database integrity error
            response_data = {
                "status": "false",
                "title": "Failed",
                "message": str(e),
            }

        except Exception as e:
            # Handle other exceptions
            response_data = {
                "status": "false",
                "title": "Failed",
                "message": str(e),
            }
            
        return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class edit_customer_supply(APIView):
#     authentication_classes = [BasicAuthentication]
#     permission_classes = [IsAuthenticated]
    
#     def get(self, request, pk, *args, **kwargs):
#         try:
#             supply_instance = CustomerSupply.objects.get(pk=pk)
#             supply_items_instances = CustomerSupplyItems.objects.filter(customer_supply=supply_instance)
            
#             # Assuming CustomerSupplyCoupon has a ManyToMany relationship with Leaf model
#             supply_coupons = CustomerSupplyCoupon.objects.filter(customer_supply=supply_instance)
#             supply_coupons_leaves = []
#             for coupon in supply_coupons:
#                 supply_coupons_leaves.extend(coupon.leaf.all())
            
#             supply_data = {
#                 "customer_supply": {
#                     "customer": str(supply_instance.customer.pk),
#                     "salesman": str(supply_instance.salesman.pk),
#                     "grand_total": supply_instance.grand_total,
#                     "discount": supply_instance.discount,
#                     "net_payable": supply_instance.net_payable,
#                     "vat": supply_instance.vat,
#                     "subtotal": supply_instance.subtotal,
#                     "amount_recieved": supply_instance.amount_recieved
#                 },
#                 "items": [
#                     {
#                         "product": str(item.product.id),
#                         "quantity": item.quantity,
#                         "amount": item.amount
#                     }
#                     for item in supply_items_instances
#                 ],
#                 "collected_empty_bottle": supply_instance.collected_empty_bottle,
#                 "allocate_bottle_to_pending": supply_instance.allocate_bottle_to_pending,
#                 "allocate_bottle_to_custody": supply_instance.allocate_bottle_to_custody,
#                 "allocate_bottle_to_paid": supply_instance.allocate_bottle_to_paid,
#                 "reference_number": supply_instance.reference_number,
#                 "total_coupon_collected": len(supply_coupons_leaves),
#                 "collected_coupon_ids": [
#                     str(coupon.pk) for coupon in supply_coupons_leaves
#                 ]
#             }

#             return Response(supply_data, status=status.HTTP_200_OK)
        
#         except CustomerSupply.DoesNotExist:
#             return Response({"error": "CustomerSupply not found"}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class delete_customer_supply(APIView):
#     authentication_classes = [BasicAuthentication]
#     permission_classes = [IsAuthenticated]
       
#     def get(self, request,pk, *args, **kwargs):
#         try:
#             with transaction.atomic():
#                 customer_supply_instance = get_object_or_404(CustomerSupply, pk=pk)
#                 supply_items_instances = CustomerSupplyItems.objects.filter(customer_supply=customer_supply_instance)
#                 five_gallon_qty = supply_items_instances.filter(product__product_name="5 Gallon").aggregate(total_quantity=Sum('quantity', output_field=DecimalField()))['total_quantity'] or 0
                
#                 DiffBottlesModel.objects.filter(
#                     delivery_date__date=customer_supply_instance.created_date.date(),
#                     assign_this_to=customer_supply_instance.salesman,
#                     customer=customer_supply_instance.customer_id
#                     ).update(status='pending')
                
#                 # Handle invoice related deletions
#                 handle_invoice_deletion(customer_supply_instance)
                
#                 # Handle outstanding amount adjustments
#                 handle_outstanding_amounts(customer_supply_instance, five_gallon_qty)
                
#                 # Handle coupon deletions and adjustments
#                 handle_coupons(customer_supply_instance, five_gallon_qty)
                
#                 # Update van product stock and empty bottle counts
#                 update_van_product_stock(customer_supply_instance, supply_items_instances, five_gallon_qty)
                
#                 # Mark customer supply and items as deleted
#                 customer_supply_instance.delete()
#                 supply_items_instances.delete()
                    
#                 response_data = {
#                     "status": "true",
#                     "title": "success",
#                     "message": "successfuly deleted",
#                 }
#                 return Response(response_data,status=status.HTTP_200_OK)
            
#         except IntegrityError as e:
#             # Handle database integrity error
#             response_data = {
#                 "status": "false",
#                 "title": "Failed",
#                 "message": str(e),
#             }

#         except Exception as e:
#             # Handle other exceptions
#             response_data = {
#                 "status": "false",
#                 "title": "Failed",
#                 "message": str(e),
#             }
            
#         return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# @api_view(['GET'])
# def customer_coupon_stock(request):
#     if (instances:=CustomerCouponStock.objects.all()).exists():

#         serializer = CustomerCouponStockSerializer(instances, many=True, context={"request": request})

#         status_code = status.HTTP_200_OK
#         response_data = {
#             "status": status_code,
#             "StatusCode": 6000,
#             "data": serializer.data,
#         }
#     else:
#         status_code = status.HTTP_400_BAD_REQUEST
#         response_data = {
#             "status": status_code,
#             "StatusCode": 6001,
#             "message": "No data",
#         }

#     return Response(response_data, status_code)

class customerCouponStock(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        if (customers:=Customers.objects.filter(sales_staff=request.user)).exists():
            route_id = request.GET.get("route_id")
            
            if route_id :
                customers = customers.filter(routes__pk=route_id)
                
            serialized_data = CustomerCouponStockSerializer(customers, many=True)
            
            status_code = status.HTTP_200_OK
            response_data = {
                "status": status_code,
                "StatusCode": 6000,
                "data": serialized_data.data,
            }
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            response_data = {
                "status": status_code,
                "StatusCode": 6001,
                "message": "No data",
            }
        return Response(response_data, status_code)

# class CustodyCustomItemListAPI(APIView):

#     authentication_classes = [BasicAuthentication]
#     permission_classes = [IsAuthenticated]
#     serializer_class = CustodyCustomItemsSerializer

#     def get(self, request, *args, **kwargs):
#         try:
#             user_id = request.user.id
#             customer_obj = Customers.objects.filter(sales_staff=user_id)
#             custody_items = CustodyCustomItems.objects.filter(customer__in=customer_obj)
#             serializer = self.serializer_class(custody_items, many=True)

#             grouped_data = {}

#             # Group items by customer id
#             for item in serializer.data:
#                 customer_id = item['customer']['customer_id']
#                 customer_name = item['customer']['customer_name']
#                 if customer_id not in grouped_data:
#                     grouped_data[customer_id] = {
#                         'customer_id': customer_id,
#                         'customer_name': customer_name,
#                         'products': []
#                     }
#                 grouped_data[customer_id]['products'].append({
#                     'product_name': item['product_name'],
#                     'product': item['product'],
#                     'rate': item['rate'],
#                     'count': item['count'],
#                     'serialnumber': item['serialnumber'],
#                     'deposit_type': item['deposit_type'],
#                     'deposit_form_number': item['deposit_form_number']
#                 })

class CustodyCustomItemListAPI(APIView):
    
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        customer_id = request.query_params.get('customer_id')
        
        if customer_id:
            custody_customer_ids = CustomerCustodyStock.objects.filter(customer__pk=customer_id).values_list("customer__customer_id", flat=True)
            customers = Customers.objects.filter(pk__in=custody_customer_ids)
        else:
            custody_customer_ids = CustomerCustodyStock.objects.filter(customer__sales_staff=request.user).values_list("customer__customer_id", flat=True)
            customers = Customers.objects.filter(pk__in=custody_customer_ids)
        
        if customers.exists():
            serializer = CustomerCustodyStockSerializer(customers, many=True)
            return Response({'status': True, 'data': serializer.data, 'message': 'Data fetched successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'status': True, 'data': [], 'message': 'No custody items'}, status=status.HTTP_200_OK)
    

class CustodyItemReturnAPI(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CustodyCustomReturnSerializer
    
    def get(self,request):
        stock_id = request.GET.get("stock_id")
        if stock_id:
            custody_stock_instance = CustomerCustodyStock.objects.get(pk=stock_id)
            # Split the concatenated fields into lists
            serialnumber_list = custody_stock_instance.serialnumber.split(', ')
            agreement_no_list = custody_stock_instance.agreement_no.split(', ')
            
            return Response(
                {
                    'status': True,
                    'product_id': custody_stock_instance.product.pk,
                    'product_name': custody_stock_instance.product.product_name,
                    'quantity': custody_stock_instance.quantity,
                    'amount': custody_stock_instance.amount,
                    'serialnumber': serialnumber_list,
                    'agreement_no': agreement_no_list,
                    'deposit_type': custody_stock_instance.deposit_type,
                    'can_deposite_chrge': custody_stock_instance.can_deposite_chrge,
                    'five_gallon_water_charge': custody_stock_instance.five_gallon_water_charge,
                    'amount_collected': custody_stock_instance.amount_collected,
                    'message': 'Success'
                }
            )
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            response_data = {
                "status": status_code,
                "message": "pass stock_id",
            }
            return Response(response_data, status_code)
            
    def post(self, request, *args, **kwargs):
        
        try:
            customer = Customers.objects.get(customer_id=request.data['customer_id'])
            custody_stock_id = request.data['custody_stock_id']
            agreement_no = request.data['agreement_no']
            total_amount = int(request.data['total_amount'])
            deposit_type = request.data['deposit_type']
            reference_no = request.data['reference_no']
            product =  ProdutItemMaster.objects.get(id=request.data['product_id'])
            quantity =  int(request.data['quantity'])
            serialnumber =  request.data['serialnumber']

            custody_return_instance = CustomerReturn.objects.create(
                customer=customer,
                agreement_no=agreement_no,
                deposit_type=deposit_type,
                reference_no=reference_no
            )

            # Create CustodyCustomItems instances
            # for item_data in items_data:
            item_intances = CustomerReturnItems.objects.create(
                customer_return=custody_return_instance,
                product=product,
                quantity=quantity,
                serialnumber=serialnumber,
                amount=total_amount
            )
            try:
                stock_instance = CustomerReturnStock.objects.get(customer=customer, product=product)
                stock_instance.agreement_no += ', ' + agreement_no
                stock_instance.serialnumber += ', ' + serialnumber
                stock_instance.quantity += quantity
                stock_instance.amount += total_amount
                stock_instance.save()
            except CustomerReturnStock.DoesNotExist:
                CustomerReturnStock.objects.create(
                    id=custody_stock_id,
                    agreement_no=agreement_no,
                    deposit_type=deposit_type,
                    reference_no=reference_no,
                    product=product,
                    quantity=quantity,
                    serialnumber=serialnumber,
                    amount=total_amount
                )
                
            custody_stock_instance = CustomerCustodyStock.objects.get(customer=customer, product=product)
            custody_stock_instance.amount_collected -= total_amount
            custody_stock_instance.quantity -= quantity
            custody_stock_instance.save()
            
            vanstock = VanProductStock.objects.get(created_date=datetime.today().date(),product=product,van__salesman=request.user)
            vanstock.return_count += quantity
            vanstock.save()
            
            # date_part = datetime.today().strftime('%Y%m%d')
            # try:
            #     invoice_last_no = Invoice.objects.filter(is_deleted=False).latest('created_date')
            #     last_invoice_number = invoice_last_no.invoice_no

            #     # Validate the format of the last invoice number
            #     parts = last_invoice_number.split('-')
            #     if len(parts) == 3 and parts[0] == 'WTR' and parts[1] == date_part:
            #         prefix, old_date_part, number_part = parts
            #         new_number_part = int(number_part) + 1
            #         invoice_number = f'{prefix}-{date_part}-{new_number_part:04d}'
            #     else:
            #         # If the last invoice number is not in the expected format, generate a new one
            #         random_part = str(random.randint(1000, 9999))
            #         invoice_number = f'WTR-{date_part}-{random_part}'
            # except Invoice.DoesNotExist:
            #     random_part = str(random.randint(1000, 9999))
            #     invoice_number = f'WTR-{date_part}-{random_part}'
            
            # # Create the invoice
            # invoice = Invoice.objects.create(
            #     invoice_no=invoice_number,
            #     created_date=datetime.today(),
            #     net_taxable=total_amount,
            #     vat=0,
            #     discount=0,
            #     amout_total=total_amount,
            #     amout_recieved=total_amount,
            #     customer=customer,
            #     reference_no=stock_instance.reference_no
            # )
            
            # if customer.sales_type == "CREDIT":
            #     invoice.invoice_type = "credit_invoive"
            #     invoice.save()

            # # Create invoice items
            # InvoiceItems.objects.create(
            #     category=product.category,
            #     product_items=product,
            #     qty=quantity,
            #     rate=total_amount,
            #     invoice=invoice,
            #     remarks='invoice genereted from supply items reference no : ' + invoice.reference_no
            # )
            # # print("invoice generate")
            # InvoiceDailyCollection.objects.create(
            #     invoice=invoice,
            #     created_date=datetime.today(),
            #     customer=invoice.customer,
            #     salesman=request.user,
            #     amount=invoice.amout_recieved,
            # )
                
            if item_intances.product.product_name == "5 Gallon":
                if (bottle_count:=BottleCount.objects.filter(van__salesman=request.user,created_date__date=custody_return_instance.created_date.date())).exists():
                    bottle_count = bottle_count.first()
                    bottle_count.custody_issue += item_intances.quantity
                    bottle_count.save()
                    
            return Response({'status': True,'message': 'Created Successfully'},status=status.HTTP_200_OK)
        except Exception as e:
            status_code = status.HTTP_400_BAD_REQUEST
            response_data = {
                "status": False,
                "message": str(e),
            }
            return Response(response_data, status_code)


class OutstandingAmountAPI(APIView):

    serializer_class = OutstandingAmountSerializer

    def post(self, request, *args, **kwargs):
        try:
            customer_id = request.data['customer_id']
            custody_items = CustodyCustomItems.objects.filter(customer=customer_id)
            total_amount = custody_items.aggregate(total_amount=Sum('amount'))['total_amount']
            amount_paid = request.data['amount_paid']
            amount_paid = Decimal(amount_paid)
            balance = total_amount - amount_paid
            product = custody_items.first().product
            
            outstanding_amount = OutstandingAmount.objects.create(
                customer_id=customer_id,
                product=product,
                balance_amount=balance,
                amount_paid=amount_paid
            )

            serializer = self.serializer_class(outstanding_amount)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"status": False, "data": str(e), "message": str(e) })

class OutstandingAmountListAPI(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        id = request.user.id
        print("id",id)
        customer=Customers.objects.filter(sales_staff__id = id)
        print("customer",customer)

        custody_items = CustodyCustomItems.objects.filter(custody_custom__customer__in =customer)
        print("custody_items",custody_items)

        serializer =CustodyCustomItemListSerializer(custody_items, many=True)
        return Response(serializer.data)

class VanStockAPI(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        date = request.GET.get('date')
        if date:
            date = datetime.strptime(date, '%Y-%m-%d').date()
        else:
            date = datetime.today().date()

        van_product_stock = VanProductStock.objects.filter(created_date=date,stock__gt=0)
        van_coupon_stock = VanCouponStock.objects.filter(created_date=date,stock__gt=0)

        van_pk = request.GET.get('van_pk')
        if van_pk:
            van_coupon_stock = van_coupon_stock.filter(van__pk=van_pk)
            van_product_stock = van_product_stock.filter(van__pk=van_pk)
        else:
            van_coupon_stock = van_coupon_stock.filter(van__salesman=request.user)
            van_product_stock = van_product_stock.filter(van__salesman=request.user)
            
        coupon_serialized_data = VanCouponStockSerializer(van_coupon_stock, many=True).data

        product_serialized_data = []
        for stock in van_product_stock:
            product_name = stock.product.product_name.lower()
            if product_name == "5 gallon":
                product_serialized_data.append({
                    'id': stock.pk,
                    'product_name': stock.product.product_name,
                    'stock_type': 'stock',
                    'count': stock.stock,
                    'product': stock.product.pk,
                    'van': stock.van.pk
                })
                product_serialized_data.append({
                    'id': stock.pk,
                    'product_name': f"{stock.product.product_name} (empty can)" ,
                    'stock_type': 'empty_bottle',
                    'count': stock.empty_can_count,
                    'product': stock.product.pk,
                    'van': stock.van.pk
                })
            else:
                product_serialized_data.append({
                    'id': stock.pk,
                    'product_name': stock.product.product_name,
                    'stock_type': 'stock',
                    'count': stock.stock,
                    'product': stock.product.pk,
                    'van': stock.van.pk
                })

        return Response(
            {
                "coupon_stock": coupon_serialized_data,
                "product_stock": product_serialized_data,
            })


class CouponCountList(APIView):

    def get(self, request, pk, format=None):
        try:
            customer = Customers.objects.get(customer_id=pk)
            customers = CustomerCouponStock.objects.filter(customer=customer)

            data = []
            for customer_stock in customers:
                data.append({
                    'customer_name': customer_stock.customer.customer_name,
                    'coupon_count': customer_stock.count,
                    'coupon_type':customer.coupon_type_id.coupon_type_name
                })

            return Response(data, status=status.HTTP_200_OK)
        except Customers.DoesNotExist:
            return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class NewCouponCreateAPI(APIView):
    def post(self, request, format=None):
        serializer = CustomerCouponStockSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NewCouponCountAPI(APIView):
    def post(self, request, pk):
        form = CoupenEditForm(request.data)
        if form.is_valid():
            data = form.save(commit=False)
            try:
                data.customer = Customers.objects.get(pk=pk)
                data.save()
                return Response({'message': 'New coupon count added successfully!'}, status=status.HTTP_201_CREATED)
            except Customers.DoesNotExist:
                return Response({'message': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteCouponCount(APIView):
    def delete(self, request, pk):
        customer_coupon_stock = get_object_or_404(CustomerCouponStock, pk=pk)
        customer_pk = customer_coupon_stock.customer.pk
        customer_coupon_stock.delete()
        return Response({'message': 'Coupon count deleted successfully!', 'customer_pk': str(customer_pk)}, status=status.HTTP_200_OK)

class customer_outstanding(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        date = request.GET.get('date')
        route_id = request.GET.get("route_id")
        customer_id = request.query_params.get("customer_id")
        
        if date:
            date = datetime.strptime(date, '%Y-%m-%d').date()
        else:
            date = datetime.today().date()

        if route_id:
            route_id = route_id
        else:
            van_route = Van_Routes.objects.filter(van__salesman=request.user).first().routes
            route_id = van_route.pk
            
        customers = Customers.objects.filter(routes__pk=route_id)

        if customer_id:
            customers = customers.filter(pk=customer_id)
            
        serialized_data = CustomerOutstandingSerializer(customers, many=True, context={"request": request, "date_str": date})

        # Filter out customers with zero amount, empty can, and coupons
        filtered_data = [customer for customer in serialized_data.data if customer['amount'] > 0 or customer['empty_can'] > 0 or customer['coupons'] > 0]
        
        # Initialize totals
        total_outstanding_amount = 0
        total_outstanding_bottles = 0
        total_outstanding_coupons = 0

        # Loop through each customer to calculate totals
        for customer in customers:
            outstanding_amount = OutstandingAmount.objects.filter(
                customer_outstanding__customer__pk=customer.pk, 
                customer_outstanding__created_date__date__lte=date
            ).aggregate(total_amount=Sum('amount'))['total_amount'] or 0
            
            collection_amount = CollectionPayment.objects.filter(
                customer__pk=customer.pk, 
                created_date__date__lte=date
            ).aggregate(total_amount_received=Sum('amount_received'))['total_amount_received'] or 0
            
            # outstanding_amount = max(outstanding_amount - collection_amount, 0)
            outstanding_amount = outstanding_amount - collection_amount
            
            # if outstanding_amount > collection_amount:
            #     outstanding_amount = outstanding_amount - collection_amount
            # else:
            #     outstanding_amount = collection_amount - outstanding_amount
            
            total_outstanding_amount += outstanding_amount
            
            total_bottles = OutstandingProduct.objects.filter(
                customer_outstanding__customer__pk=customer.pk, 
                customer_outstanding__created_date__date__lte=date
            ).aggregate(total_bottles=Sum('empty_bottle'))['total_bottles'] or 0
            total_outstanding_bottles += total_bottles

            total_coupons = OutstandingCoupon.objects.filter(
                customer_outstanding__customer__pk=customer.pk,
                customer_outstanding__created_date__date__lte=date
            ).aggregate(total_coupons=Sum('count'))['total_coupons'] or 0
            total_outstanding_coupons += total_coupons
        
        return Response({
            'status': True,
            'data': filtered_data,
            "total_amount": total_outstanding_amount,
            "total_coupons": total_outstanding_bottles,
            "total_emptycan": total_outstanding_bottles,
            'message': 'success'
        })


class CustomerCouponListAPI(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        customers = Customers.objects.filter(sales_type="CASH COUPON")

        route_id = request.GET.get("route_id")
        customer_id = request.query_params.get("customer_id")
        
        if route_id:
            customers = customers.filter(routes__pk=route_id)
        if customer_id:
            customers = customers.filter(pk=customer_id)
            
        serializer = CustomerDetailSerializer(customers, many=True, context={'request': request})

        return Response(serializer.data)

class ProductAndBottleAPIView(APIView):
    def get(self, request):
        date = request.query_params.get('date')
        if date:
            date = datetime.strptime(date, '%Y-%m-%d').date()
        else:
            date = datetime.today().date()
        try:
            if date:
                product_items = ProdutItemMaster.objects.filter(created_date__date=date)
                customer_supply = CustomerSupply.objects.filter(created_date__date=date)
                van_coupon_stock = VanCouponStock.objects.filter(created_date=date)
            else:
                product_items = ProdutItemMaster.objects.all()
                customer_supply = CustomerSupply.objects.all()
                van_coupon_stock = VanCouponStock.objects.all()

            product_serializer = ProdutItemMasterSerializer(product_items, many=True)
            bottle_serializer = CustomerSupplySerializer(customer_supply, many=True)
            van_coupon_stock_serializer = VanCouponStockSerializer(van_coupon_stock, many=True)

            return Response({
                'product_name': product_serializer.data,
                'collected_empty_bottle': bottle_serializer.data,
                'van_coupon_stock': van_coupon_stock_serializer.data
            })
        except ValueError:
            return Response({'error': 'Invalid date format. Please use YYYY-MM-DD.'}, status=400)

class CollectionAPI(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        if not user:
            return Response({
                'status': False,
                'message': 'User ID is required!'
            }, status=status.HTTP_400_BAD_REQUEST)
        customer_id = request.query_params.get('customer_id')
        # Filter CustomerSupply objects based on the user
        invoices_customer_pk = Invoice.objects.filter(invoice_status="non_paid",is_deleted=False).exclude(amout_total=0).values_list("customer__pk")
        collection = Customers.objects.filter(pk__in=invoices_customer_pk,sales_staff=user)
        if customer_id:
            collection = collection.filter(pk=customer_id)
        if collection.exists():
            collection_serializer = CollectionCustomerSerializer(collection, many=True)
            return Response({
                'status': True,
                'data': collection_serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': True,
                'data': []
            }, status=status.HTTP_200_OK)

# class AddCollectionPayment(APIView):
#     authentication_classes = [BasicAuthentication]
#     permission_classes = [IsAuthenticated]
#     def post(self, request):
#         # Extract data from request
#         payment_method = request.data.get("payment_method")
#         amount_received = request.data.get("amount_received")
#         invoice_ids = request.data.get("invoice_ids")
#         customer_id = request.data.get("customer_id")
        
#         # Retrieve customer object
#         try:
#             customer = Customers.objects.get(pk=customer_id)
#         except Customers.DoesNotExist:
#             return Response({"message": "Customer does not exist."}, status=status.HTTP_404_NOT_FOUND)
        
#         # Create collection payment instance
#         collection_payment = CollectionPayment.objects.create(
#             payment_method=payment_method,
#             customer=customer,
#             salesman=request.user,
#             amount_received=amount_received,
#         )
        
#         # If payment method is cheque, handle cheque details
#         if payment_method == "CHEQUE":
#             cheque_data = request.data.get("cheque_details", {})
#             cheque_serializer = CollectionChequeSerializer(data=cheque_data)
#             if cheque_serializer.is_valid():
#                 cheque = cheque_serializer.save(collection_payment=collection_payment)
#             else:
#                 return Response(cheque_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
#         remaining_amount = amount_received
        
#         # Distribute the received amount among invoices
#         for invoice_id in invoice_ids:
#             invoice = Invoice.objects.get(pk=invoice_id)
#             balance_invoice_amount = invoice.amout_total - invoice.amout_recieved
            
#             # Check if a CollectionItems instance already exists for this invoice and collection payment
#             existing_collection_item = CollectionItems.objects.filter(invoice=invoice, collection_payment=collection_payment).first()
#             if existing_collection_item:
#                 # Update existing CollectionItems instance
#                 existing_collection_item.amount_received += min(balance_invoice_amount, remaining_amount)
#                 existing_collection_item.balance = invoice.amout_recieved - existing_collection_item.amount_received
#                 existing_collection_item.save()
#             else:
#                 # Create new CollectionItems instance
#                 CollectionItems.objects.create(
#                     invoice=invoice,
#                     amount=invoice.amout_total,
#                     balance=balance_invoice_amount,
#                     amount_received=min(balance_invoice_amount, remaining_amount),
#                     collection_payment=collection_payment
#                 )
            
#             remaining_amount -= min(balance_invoice_amount, remaining_amount)
            
#             # Update invoice status if fully paid
#             if invoice.amout_recieved >= invoice.amout_total:
#                 invoice.invoice_status = 'paid'
#                 print("paid")
            
#             invoice.save()
            
#             if remaining_amount <= 0:
#                 break

        
#         return Response({"message": "Collection payment saved successfully."}, status=status.HTTP_201_CREATED)

class AddCollectionPayment(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Extract data from request
        payment_method = request.data.get("payment_method")
        amount_received = Decimal(request.data.get("amount_received"))
        invoice_ids = request.data.get("invoice_ids")
        customer_id = request.data.get("customer_id")
        date_part = timezone.now().strftime('%Y%m%d')
        
        # Retrieve customer object
        try:
            customer = Customers.objects.get(pk=customer_id)
        except Customers.DoesNotExist:
            return Response({"message": "Customer does not exist."}, status=status.HTTP_404_NOT_FOUND)
        
        # Generate a unique receipt number
        try:
            reciept_last_no = Receipt.objects.all().latest('created_date')
            last_reciept_number = reciept_last_no.receipt_number

            # Validate the format of the last invoice number
            parts = last_reciept_number.split('-')
            if len(parts) == 3 and parts[0] == 'RCT' and parts[1] == date_part:
                prefix, old_date_part, number_part = parts
                r_new_number_part = int(number_part) + 1
                receipt_number = f'{prefix}-{date_part}-{r_new_number_part:04d}'
            else:
                # If the last invoice number is not in the expected format, generate a new one
                random_part = str(random.randint(1000, 9999))
                receipt_number = f'RCT-{date_part}-{random_part}'
        except Receipt.DoesNotExist:
            random_part = str(random.randint(1000, 9999))
            receipt_number = f'RCT-{date_part}-{random_part}'
            
        # Use atomic transaction to ensure data consistency
        with transaction.atomic():
            # Create collection payment instance
            collection_payment = CollectionPayment.objects.create(
                payment_method=payment_method,
                customer=customer,
                salesman=request.user,
                amount_received=amount_received,
                receipt_number=receipt_number,
            )
           
            remaining_amount = amount_received
            
            invoice_numbers = []
            # Iterate over invoice IDs
            for invoice_id in invoice_ids:
                try:
                    invoice = Invoice.objects.get(pk=invoice_id, customer=customer)
                except Invoice.DoesNotExist:
                    continue
                invoice_numbers.append(invoice.invoice_no)
                # Calculate the amount due for this invoice
                due_amount = invoice.amout_total - invoice.amout_recieved
                
                # If remaining_amount is greater than zero and there is still due amount for the current invoice
                if remaining_amount != Decimal('0') and due_amount != Decimal('0'):
                    # Calculate the payment amount for this invoice
                    payment_amount = min(due_amount, remaining_amount)
                    
                    # Update the invoice balance and amount received
                    invoice.amout_recieved += payment_amount
                    invoice.save()
                    
                    # Create CollectionItems instance
                    CollectionItems.objects.create(
                        invoice=invoice,
                        amount=invoice.amout_total,
                        balance=invoice.amout_total - invoice.amout_recieved,
                        amount_received=payment_amount,
                        collection_payment=collection_payment
                    )
                    if CustomerOutstandingReport.objects.filter(customer=customer, product_type="amount").exists():
                        outstanding_instance = CustomerOutstandingReport.objects.get(customer=customer, product_type="amount")
                        outstanding_instance.value -= payment_amount
                        outstanding_instance.save()
                    
                    # Update the remaining amount
                    remaining_amount -= payment_amount
                    
                    # If the invoice is fully paid, update its status
                    if invoice.amout_recieved == invoice.amout_total:
                        invoice.invoice_status = 'paid'
                        invoice.save()
                else:
                    # Break the loop if there is no remaining amount or the current invoice is fully paid
                    break
            receipt = Receipt.objects.create(
                transaction_type="collection",
                instance_id=str(collection_payment.id),  # Correctly assign the ID as a string
                amount_received=amount_received,
                receipt_number=receipt_number,
                customer=customer,
                invoice_number=",".join(invoice_numbers)  # Join the invoice numbers into a comma-separated string
            )

            # If there is remaining amount after paying all invoices, adjust it with the outstanding balance
            if remaining_amount != Decimal('0'):
                negatieve_remaining_amount = -remaining_amount
                
                # Create a customer outstanding record for the refund amount
                # customer_outstanding = CustomerOutstanding.objects.create(
                #     product_type="amount",
                #     created_by=request.user.id,
                #     customer=customer,
                #     created_date=datetime.today()
                # )

                # # Create an outstanding amount record for the refund amount
                # outstanding_amount = OutstandingAmount.objects.create(
                #     amount=negatieve_remaining_amount,
                #     customer_outstanding=customer_outstanding,
                # )

                # Update the CustomerOutstandingReport or create a new one if it doesn't exist
                if CustomerOutstandingReport.objects.filter(customer=customer, product_type="amount").exists():
                    outstanding_instance = CustomerOutstandingReport.objects.get(customer=customer, product_type="amount")
                    outstanding_instance.value += negatieve_remaining_amount  # Add the remaining amount to the outstanding report
                    outstanding_instance.save()
                else:
                    CustomerOutstandingReport.objects.create(
                        customer=customer, 
                        product_type="amount",
                        value=negatieve_remaining_amount,
                    )
                
                try:
                    invoice_last_no = Invoice.objects.filter(is_deleted=False).latest('created_date')
                    last_invoice_number = invoice_last_no.invoice_no

                    # Validate the format of the last invoice number
                    parts = last_invoice_number.split('-')
                    if len(parts) == 3 and parts[0] == 'WTR' and parts[1] == date_part:
                        prefix, old_date_part, number_part = parts
                        new_number_part = int(number_part) + 1
                        invoice_number = f'{prefix}-{date_part}-{new_number_part:04d}'
                    else:
                        # If the last invoice number is not in the expected format, generate a new one
                        random_part = str(random.randint(1000, 9999))
                        invoice_number = f'WTR-{date_part}-{random_part}'
                except Invoice.DoesNotExist:
                    random_part = str(random.randint(1000, 9999))
                    invoice_number = f'WTR-{date_part}-{random_part}'
                
                # Create the invoice for the refund amount
                invoice = Invoice.objects.create(
                    invoice_no=invoice_number,
                    created_date=datetime.today(),
                    net_taxable=negatieve_remaining_amount,
                    vat=0,
                    discount=0,
                    amout_total=negatieve_remaining_amount,
                    amout_recieved=0,
                    customer=customer,
                    reference_no=f"custom_id{customer.custom_id}"
                )
                # customer_outstanding.invoice_no = invoice.invoice_no
                # customer_outstanding.save()
                
                if customer.sales_type == "CREDIT":
                    invoice.invoice_type = "credit_invoice"
                    invoice.save()

                # Create invoice items
                item = ProdutItemMaster.objects.get(product_name="5 Gallon")
                InvoiceItems.objects.create(
                    category=item.category,
                    product_items=item,
                    qty=0,
                    rate=customer.rate,
                    invoice=invoice,
                    remarks='invoice generated from collection: ' + invoice.reference_no
                )
                
        return Response({"message": "Collection payment saved successfully."}, status=status.HTTP_201_CREATED)
    
class CouponTypesAPI(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        user = request.user
        
        if not user:
            return Response({'status': False,'message': 'User ID is required!'}, status=status.HTTP_400_BAD_REQUEST)

        instances = CouponType.objects.all()

        if instances.exists():
            serialized = CouponTypeSerializer(instances, many=True)
            return Response({'status': True,'data': serialized.data}, status=status.HTTP_200_OK)
        else:
            return Response({'status': False,'message': 'No data found'}, status=400)

class EmergencyCustomersAPI(APIView):
    # authentication_classes = [BasicAuthentication]
    # permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        
        emergency_customers = DiffBottlesModel.objects.all()
        print(emergency_customers,"emergency_customers")
        if emergency_customers.exists():
            serialized = EmergencyCustomersSerializer(emergency_customers, many=True)
            return Response({'status': True,'data': serialized.data}, status=status.HTTP_200_OK)
        else:
            return Response({'status': False,'message': 'No data found'}, status=400)

#--------------------New sales Report -------------------------------
#--------------------New sales Report -------------------------------
class CustomerSalesReportAPI(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        filter_data = {}

        total_amount = 0
        total_discount = 0
        total_net_payable = 0
        total_vat = 0
        total_grand_total = 0
        total_amount_received = 0

        start_date_str = request.data.get('start_date')
        end_date_str = request.data.get('end_date')

        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        else:
            start_date = datetime.today().date()
            end_date = datetime.today().date()

        filter_data = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
        }

        sales = CustomerSupply.objects.select_related('customer', 'salesman').filter(
            created_date__date__gte=start_date,
            created_date__date__lte=end_date,
            salesman=request.user
        ).exclude(customer__sales_type__in=["CASH COUPON", "CREDIT COUPON"]).order_by("-created_date")

        coupons = CustomerCoupon.objects.select_related('customer', 'salesman').filter(
            created_date__date__gte=start_date,
            created_date__date__lte=end_date,
            salesman=request.user
        ).order_by("-created_date")

        # collections = CollectionPayment.objects.select_related('customer', 'salesman').filter(
        #     created_date__date__gte=start_date,
        #     created_date__date__lte=end_date
        # ).order_by("-created_date")

        sales_report_data = []

        # Process CustomerSupply data
        for sale in sales:
            serialized_sale = NewSalesCustomerSupplySerializer(sale).data
            serialized_sale['customer_name'] = sale.customer.customer_name
            serialized_sale['building_name'] = sale.customer.building_name
            sales_report_data.append(serialized_sale)

            total_amount += sale.grand_total
            total_discount += sale.discount
            total_net_payable += sale.net_payable
            total_vat += sale.vat
            total_grand_total += sale.grand_total
            total_amount_received += sale.amount_recieved

        # Process CustomerCoupon data
        for coupon in coupons:
            serialized_coupon = NewSalesCustomerCouponSerializer(coupon).data
            serialized_coupon['customer_name'] = coupon.customer.customer_name
            serialized_coupon['building_name'] = coupon.customer.building_name
            sales_report_data.append(serialized_coupon)

            total_amount += coupon.grand_total
            total_discount += coupon.discount
            total_net_payable += coupon.net_amount
            total_vat += Tax.objects.get(name="VAT").percentage
            total_grand_total += coupon.grand_total
            total_amount_received += coupon.amount_recieved

        # Process CollectionPayment data
        # for collection in collections:
        #     serialized_collection = NewSalesCollectionPaymentSerializer(collection).data
        #     serialized_collection['customer_name'] = collection.customer.customer_name
        #     serialized_collection['building_name'] = collection.customer.building_name
        #     sales_report_data.append(serialized_collection)

        #     total_amount += collection.total_amount()
        #     total_discount += collection.total_discounts()
        #     total_net_payable += collection.total_net_taxeble()
        #     total_vat += collection.total_vat()
        #     total_grand_total += collection.total_amount()
        #     total_amount_received += collection.collected_amount()

        response_data = {
            'customersales': sales_report_data,
            'total_amount': total_amount,
            'total_discount': total_discount,
            'total_net_payable': total_net_payable,
            'total_vat': total_vat,
            'total_grand_total': total_grand_total,
            'total_amount_received': total_amount_received,
            'filter_data': filter_data,
        }

        return Response(response_data)


class CreditNoteAPI(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        
        if start_date and end_date:
            try:
                start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
                end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                return Response({"error": "Invalid date format. Please use YYYY-MM-DD."}, status=400)
        else:
            start_datetime = datetime.today().date()
            end_datetime = datetime.today().date()
        
        credit_invoices = Invoice.objects.filter(invoice_type='credit_invoive', created_date__date__range=[start_datetime, end_datetime], customer__sales_staff=request.user)
        print('credit_invoices',credit_invoices)
        serialized = CreditNoteSerializer(credit_invoices, many=True)
        
        if serialized.data:
            return Response({'status': True, 'data': serialized.data}, status=status.HTTP_200_OK)
        else:
            return Response({'status': False, 'message': 'No data found'}, status=status.HTTP_400_BAD_REQUEST)
        

class DashboardAPI(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, route_id, trip):
        if request.GET.get("date_str"):
            date_str = request.GET.get("date_str")
        else :
            date_str = str(datetime.today().date())
            
        date = datetime.strptime(date_str, '%Y-%m-%d')
        
        today_customers = find_customers(request, date_str, route_id)
        today_customers_count = len(today_customers) if today_customers else 0

                
        supplied_customers_count = CustomerSupply.objects.filter(customer__routes__pk=route_id,created_date__date=date).count()
        
        temperary_schedule_unsupply_count = DiffBottlesModel.objects.filter(customer__routes__pk=route_id,status="pending",delivery_date__date=date).count()
        temperary_schedule_supplied_count = DiffBottlesModel.objects.filter(customer__routes__pk=route_id,status="supplied",delivery_date__date=date).count()
        
        van_route = Van_Routes.objects.get(routes__pk=route_id,van__salesman=request.user)
        coupon_sale_count = CustomerCouponItems.objects.filter(customer_coupon__customer__routes__pk=route_id,customer_coupon__created_date__date=date).count()
        try:
            van_product_stock = VanProductStock.objects.get(created_date=date, van=van_route.van, product__product_name="5 Gallon")
            empty_bottle_count = van_product_stock.empty_can_count or 0
            filled_bottle_count = van_product_stock.stock or 0
        except VanProductStock.DoesNotExist:
            empty_bottle_count = 0
            filled_bottle_count = 0
        
        used_coupon_count = CustomerSupplyCoupon.objects.filter(customer_supply__customer__routes__pk=route_id,customer_supply__created_date__date=date).aggregate(leaf_count=Count('leaf'))['leaf_count']
        # sales records start
        cash_sale_total_amount = CustomerSupply.objects.filter(customer__routes__pk=route_id,created_date__date=date,amount_recieved__gt=0).aggregate(total_amount=Sum('subtotal'))['total_amount'] or 0
        cash_sale_total_amount += CustomerCoupon.objects.filter(created_date__date=date,customer__routes__pk=route_id,amount_recieved__gt=0).aggregate(total_amount=Sum('total_payeble'))['total_amount'] or 0
        cash_sale_amount_recieved = CustomerSupply.objects.filter(customer__routes__pk=route_id,created_date__date=date,amount_recieved__gt=0).aggregate(total_amount=Sum('amount_recieved'))['total_amount'] or 0
        cash_sale_amount_recieved += CustomerCoupon.objects.filter(created_date__date=date,customer__routes__pk=route_id,amount_recieved__gt=0).aggregate(total_amount=Sum('amount_recieved'))['total_amount'] or 0
        
        credit_sale_total_amount = CustomerSupply.objects.filter(customer__routes__pk=route_id,created_date__date=date,amount_recieved__lte=0).aggregate(total_amount=Sum('subtotal'))['total_amount'] or 0
        credit_sale_total_amount += CustomerCoupon.objects.filter(customer__routes__pk=route_id,created_date__date=date,amount_recieved__lte=0).aggregate(total_amount=Sum('total_payeble'))['total_amount'] or 0
        credit_sale_amount_recieved = CustomerSupply.objects.filter(customer__routes__pk=route_id,created_date__date=date,amount_recieved__lte=0).aggregate(total_amount=Sum('amount_recieved'))['total_amount'] or 0
        credit_sale_amount_recieved += CustomerCoupon.objects.filter(customer__routes__pk=route_id,created_date__date=date,amount_recieved__lte=0).aggregate(total_amount=Sum('amount_recieved'))['total_amount'] or 0
        # sales records end
        # cash in hand start
        cash_sale_amount = CustomerSupply.objects.filter(customer__routes__pk=route_id,created_date__date=date,amount_recieved__gt=0).aggregate(total_amount=Sum('subtotal'))['total_amount'] or 0
        cash_sale_amount += CustomerCoupon.objects.filter(created_date__date=date,customer__routes__pk=route_id,amount_recieved__gt=0).aggregate(total_amount=Sum('total_payeble'))['total_amount'] or 0
        
        dialy_collections = CollectionPayment.objects.filter(salesman_id=van_route.van.salesman,amount_received__gt=0)
        
        dialy_collections = dialy_collections.filter(created_date__date=date)
        credit_sales_amount_collected = dialy_collections.aggregate(total_amount=Sum('amount_received'))['total_amount'] or 0
        total_sales_amount_collected = cash_sale_amount_recieved + credit_sales_amount_collected
        # cash in hand end
        expences = Expense.objects.filter(van__salesman__pk=van_route.van.salesman.pk,expense_date=date).aggregate(total_amount=Sum('amount'))['total_amount'] or 0
        
        balance_in_hand = total_sales_amount_collected - expences
        
        total_fivegallon_supplied = CustomerSupplyItems.objects.filter(customer_supply__customer__routes__pk=route_id,customer_supply__created_date__date=date).aggregate(total_qty=Sum('quantity'))['total_qty'] or 0
        data = {
            'date': date_str,
            'today_schedule': {
                'today_customers_count': today_customers_count,
                'supplied_customers_count': supplied_customers_count
                },
            'temporary_schedule': {
                'unsupplied_count': temperary_schedule_unsupply_count,
                'supplied_count': temperary_schedule_supplied_count,
                },
            'coupon_sale_count': coupon_sale_count,
            'empty_bottle_count': empty_bottle_count,
            'filled_bottle_count': filled_bottle_count,
            'used_coupon_count': used_coupon_count,
            'cash_in_hand': balance_in_hand,
            'cash_sale': {
                'cash_sale_total_amount': cash_sale_total_amount,
                'cash_sale_amount_recieved': cash_sale_amount_recieved,
            },
            'credit_sale': {
                'credit_sale_total_amount': credit_sale_total_amount,
                'credit_sale_amount_recieved': credit_sales_amount_collected,
            },
            'expences': expences,
            'total_fivegallon_supplied': total_fivegallon_supplied,
        }
        
        return Response({'status': True, 'data': data}, status=status.HTTP_200_OK)
    
class CollectionReportAPI(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        start_date_str = request.data.get('start_date')
        end_date_str = request.data.get('end_date')

        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        else:
            start_date = datetime.today().date()
            end_date = datetime.today().date()
        salesman=request.user
        print("salesman",salesman)    
        instances = CollectionPayment.objects.filter(created_date__date__gte=start_date,created_date__date__lte=end_date,salesman=request.user)
        serialized_data = CollectionReportSerializer(instances, many=True).data
        
        total_collected_amount = CollectionItems.objects.filter(collection_payment__pk__in=instances.values_list('pk')).aggregate(total=Sum('amount_received', output_field=DecimalField()))['total'] or 0
        return Response({
            'status': True,
            'data': serialized_data,
            'total_collected_amount': str(total_collected_amount),
            'filter_data': {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
            }
        }, status=status.HTTP_200_OK)
        
        
#----------------------Coupon Supply Report
class CouponSupplyCountAPIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):

        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        
        if not (start_date and end_date):
            start_datetime = datetime.today().date()
            end_datetime = datetime.today().date()
        else:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        coupon_counts = CustomerCoupon.objects.filter(created_date__date__range=[start_datetime,end_datetime])
        serializer = CouponSupplyCountSerializer(coupon_counts, many=True)

        return Response({'status': True, 'data': serializer.data}, status=status.HTTP_200_OK)


class Coupon_Sales_APIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):

        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        sales_type = request.data.get('sales_type')  
        
        if not (start_date and end_date):
            start_datetime = datetime.today().date()
            end_datetime = datetime.today().date()
        else:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d').date()
        
            
        coupon_sales = CustomerCouponItems.objects.filter(customer_coupon__created_date__date__range=[start_datetime,end_datetime])
        
        if sales_type:
            coupon_sales = coupon_sales.filter(customer_coupon__customer__sales_type=sales_type)
        
        # Calculate totals for rate, amount_collected, and balance
        total_rate = coupon_sales.aggregate(total=Sum('rate'))['total'] or 0
        total_amount_collected = coupon_sales.aggregate(total=Sum('customer_coupon__amount_recieved'))['total'] or 0
        total_balance = coupon_sales.aggregate(total=Sum('customer_coupon__balance'))['total'] or 0
        
        # Calculate total_per_leaf_rate
        total_per_leaf_rate = sum(
            coupon.get_per_leaf_rate() for coupon in coupon_sales if coupon.get_per_leaf_rate() is not None
        )
        serializer = Coupon_Sales_Serializer(coupon_sales, many=True)

# Return the response with totals in the footer
        return Response({
            'status': True,
            'data': serializer.data,
            'total_sum': {
                'total_rate': total_rate,
                'total_amount_collected': total_amount_collected,
                'total_per_leaf_rate':total_per_leaf_rate,
                'total_balance': total_balance
            }
        }, status=status.HTTP_200_OK)
            
class RedeemedHistoryAPI(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        customer_id = request.query_params.get('customer_id')
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            start_date = date.today()
            end_date = date.today()
        
        supply_instances = CustomerSupply.objects.filter(created_date__date__gte=start_date,created_date__date__lte=end_date,customer__sales_type="CASH COUPON")

        if customer_id:
            supply_instances = supply_instances.filter(customer__pk=customer_id)
            
        customer_coupon_counts = []
        for supply_instance in supply_instances:
            digital_count = CustomerSupplyDigitalCoupon.objects.filter(
                customer_supply=supply_instance,
                customer_supply__created_date__date__gte=start_date,
                customer_supply__created_date__date__lte=end_date
            ).aggregate(Sum('count'))['count__sum'] or 0

            manual_count = CustomerSupplyCoupon.objects.filter(
                customer_supply=supply_instance,
                customer_supply__created_date__date__gte=start_date,
                customer_supply__created_date__date__lte=end_date,
                leaf__coupon__coupon_method='manual'
            ).count()

            customer_coupon_counts.append({
                'customer_name': supply_instance.customer.customer_name,
                'building_name': supply_instance.customer.building_name,
                'door_house_no': supply_instance.customer.door_house_no,
                'digital_coupons_count': digital_count,
                'manual_coupons_count': manual_count
            })

        serializer = CustomerCouponCountsSerializer(customer_coupon_counts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# VisitReportAPI
# Coupon Consumption Report
class CouponConsumptionReport(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
            start_date = request.data.get('start_date')  
            print("start_date",start_date)
            end_date = request.data.get('end_date')  
            print("end_date",end_date)
            
            if start_date and end_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            else:
                start_date = date.today()
                end_date = date.today()

            supply_instance = CustomerSupply.objects.filter(
                created_date__date__gte=start_date,
                created_date__date__lte=end_date,
                customer__sales_type="CASH COUPON"
            )
            
            serializer = CouponConsumptionSerializer(supply_instance, many=True)
            
            # Initialize total sums
            total_no_of_bottles_supplied = 0
            total_collected_empty_bottle = 0
            total_total_digital_leaflets = 0
            total_total_manual_leaflets = 0
            total_no_of_leaflet_collected = 0
            total_pending_leaflet = 0

            # Calculate total sums from serializer data
            for supply in serializer.data:
                total_no_of_bottles_supplied += supply.get('no_of_bottles_supplied', 0)
                total_collected_empty_bottle += supply.get('collected_empty_bottle', 0)  
                total_total_digital_leaflets += supply.get('total_digital_leaflets', 0)
                total_total_manual_leaflets += supply.get('total_manual_leaflets', 0)
                total_no_of_leaflet_collected += supply.get('no_of_leaflet_collected', 0)
                total_pending_leaflet += supply.get('pending_leaflet', 0)

            return Response({
                'status': True,
                'data': serializer.data,               
                'total_no_of_bottles_supplied': total_no_of_bottles_supplied,
                'total_collected_empty_bottle': total_collected_empty_bottle,                  
                'total_total_digital_leaflets': total_total_digital_leaflets,
                'total_total_manual_leaflets': total_total_manual_leaflets,
                'total_no_of_leaflet_collected': total_no_of_leaflet_collected,
                'total_pending_leaflet': total_pending_leaflet,
            }, status=status.HTTP_200_OK)

from django.utils.timezone import make_aware
from django.db.models import Sum, Count, Case, When, IntegerField

class StockMovementReportAPI(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        salesman_id = self.kwargs.get('salesman_id')
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')

        if not (from_date and to_date):
            return Response({'status': False, 'message': 'Please provide both from_date and to_date'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from_date = make_aware(datetime.strptime(from_date, '%Y-%m-%d'))
            to_date = make_aware(datetime.strptime(to_date, '%Y-%m-%d'))
        except ValueError:
            return Response({'status': False, 'message': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)

        stock_movement = CustomerSupplyItems.objects.filter(
            customer_supply__salesman_id=salesman_id,
            customer_supply__created_date__range=(from_date, to_date)
        ).select_related('customer_supply', 'product')

        if stock_movement.exists():
            # Annotate sold and returned quantities
            stock_movement = stock_movement.annotate(
                sold_quantity=Case(
                    When(quantity__gt=0, then=F('quantity')),
                    default=0,
                    output_field=IntegerField()
                ),
                returned_quantity=Case(
                    When(quantity__lt=0, then=F('quantity')),
                    default=0,
                    output_field=IntegerField()
                )
            )

            # Aggregate by product
            aggregated_stock_movement = stock_movement.values('product__product_name', 'product__rate').annotate(
                total_quantity=Sum('quantity'),
                total_sold_quantity=Sum('sold_quantity'),
                total_returned_quantity=Sum('returned_quantity')
            )

            total_sale_amount = aggregated_stock_movement.aggregate(
                total_sale=Sum(F('amount'))
            )['total_sale']

            # Prepare product stats data
            products_stats = aggregated_stock_movement.values(
                'product__product_name', 
                'total_quantity', 
                'total_sold_quantity', 
                'total_returned_quantity', 
                'product__rate'
            )

            product_stats_data = ProductStatsSerializer(products_stats, many=True).data
            return Response({
                'status': True, 
                'products_stats': product_stats_data, 
                'total_sale_amount': total_sale_amount
            }, status=status.HTTP_200_OK)
        else:
            return Response({'status': False, 'message': 'No data found'}, status=status.HTTP_400_BAD_REQUEST)
        
        
# from django.db.models import Sum, Count, Case, When, IntegerField

# from django.utils.timezone import make_aware

# class StockMovementReportAPI(APIView):
#     authentication_classes = [BasicAuthentication]
#     permission_classes = [IsAuthenticated]
    
#     def get(self, request, salesman_id, *args, **kwargs):
#         from_date = request.GET.get('from_date')
#         to_date = request.GET.get('to_date')

#         if not (from_date and to_date):
#             return Response({'status': False, 'message': 'Please provide both from_date and to_date'}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             from_date = make_aware(datetime.strptime(from_date, '%Y-%m-%d'))
#             to_date = make_aware(datetime.strptime(to_date, '%Y-%m-%d'))
#         except ValueError:
#             return Response({'status': False, 'message': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)

#         stock_movement = CustomerSupplyItems.objects.filter(
#             customer_supply__salesman_id=salesman_id,
#             customer_supply__created_date__range=(from_date, to_date)
#         ).select_related('customer_supply__customer', 'customer_supply__salesman')


#         print("stock_movement",stock_movement)
#         if stock_movement.exists():
#             # Aggregate quantities for the same product
#             aggregated_stock_movement = stock_movement.values('product').annotate(
#                 total_quantity=Sum('quantity'),
#                 rate=F('product__rate')
#             )

#             total_sale_amount = aggregated_stock_movement.aggregate(total_sale=Sum(F('total_quantity') * F('rate')))['total_sale']

#             # Count products sold, returned, and assigned
#             products_sold = aggregated_stock_movement.aggregate(
#                 products_sold=Sum(Case(When(total_quantity__gt=0, then=F('total_quantity')), default=0, output_field=IntegerField())),
#                 products_returned=Sum(Case(When(total_quantity__lt=0, then=F('total_quantity')), default=0, output_field=IntegerField())),
#                 products_assigned=Sum(Case(When(total_quantity__gt=0, then=F('total_quantity')), default=0, output_field=IntegerField()))
#             )

#             serialized_data = StockMovementReportSerializer(aggregated_stock_movement, many=True).data
#             response_data = {
#                 'status': True,
#                 'data': serialized_data,
#                 'total_sale_amount': total_sale_amount,
#                 'products_sold': products_sold['products_sold'],
#                 'products_returned': products_sold['products_returned'],
#                 'products_assigned': products_sold['products_assigned']
#             }
#             return Response(response_data, status=status.HTTP_200_OK)
#         else:
#             return Response({'status': False, 'message': 'No data found'}, status=status.HTTP_400_BAD_REQUEST)


# class VisitReportAPI(APIView):
#     def get(self, request, *args, **kwargs):
#         salesman_id = self.kwargs.get('salesman_id')
#         date_str = str(datetime.today().date())
#         user_type = 'Salesman'

#         today_visits = Customers.objects.filter(sales_staff__user_type=user_type, sales_staff_id=salesman_id, visit_schedule=date_str)

#         print('today_visits', today_visits)
       
#         customers_list = []

#         for customer in today_visits:
#                 supplied_customer = CustomerSupply.objects.filter(customer=customer,created_date__date=datetime.today().date())

class VisitReportAPI(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        try:
            start_date_str = request.data.get('start_date')
            end_date_str = request.data.get('end_date')
            
            if not (start_date_str and end_date_str):
                start_date = datetime.today().date()
                end_date = datetime.today().date()
            else:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                
            instances = CustomerSupply.objects.filter(created_date__date__gte=start_date,created_date__date__lt=end_date,salesman=request.user)
            serialized_data = VisitedCustomerSerializers(instances,many=True).data

            return Response({'status': True, 'data': serialized_data, 'message': 'Customer visit details fetched successfully!'})

        except Exception as e:
            return Response({'status': False, 'data': str(e), 'message': 'Something went wrong!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        
class NonVisitedReportAPI(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        try:
            date = request.GET.get('date')
            
            if date:
                date = datetime.strptime(date, '%Y-%m-%d').date()
            else:
                date = datetime.today().date()
                
            van_route = Van_Routes.objects.filter(van__salesman=request.user).first()
            
            today_customers = find_customers(request, str(date), van_route.routes.pk)
            today_customer_ids = [str(customer['customer_id']) for customer in today_customers]

            today_supplied = CustomerSupply.objects.filter(created_date__date=date)
            today_supplied_ids = today_supplied.values_list('customer_id', flat=True)
            customers = Customers.objects.filter(pk__in=today_customer_ids).exclude(pk__in=today_supplied_ids)

            serializer = CustomerSupplySerializer(customers, many=True)
            return JsonResponse({'status': True, 'data': serializer.data, 'message': 'Pending Supply report passed!'})

        except Exception as e:
            return Response({'status': False, 'data': str(e), 'message': 'Something went wrong!'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    # def get(self, request, *args, **kwargs):
    #     try:
    #         user_id = request.user.id
    #         print("user_id", user_id)
            
    #         customer_objs = Customers.objects.filter(sales_staff=user_id)
            
    #         non_visited_customers = customer_objs.exclude(customersupply__salesman=user_id, customersupply__created_date__date=datetime.today().date())
            
    #         serializer = CustomerSerializer(non_visited_customers, many=True)
            
    #         return Response({'status': True, 'data': serializer.data, 'message': 'Non-visited customers listed successfully!'})
        
    #     except Exception as e:
    #         return Response({'status': False, 'data': str(e), 'message': 'Something went wrong!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CustomerStatementReport(APIView):
    def get(self, request):
        try:
            # Retrieve all customer details
            customer_details = Customers.objects.all()
            serializer = CustomersStatementSerializer(customer_details, many=True).data

            # Check if 'detail' parameter is passed
            detail_param = request.query_params.get('detail', 'false').lower() == 'true'
            print("detail_param:", detail_param)

            # If 'detail' parameter is true, fetch outstanding details for each customer
            if detail_param:
                for customer in serializer:
                    customer_id = customer['customer_id']
                    # Retrieve outstanding details for the current customer
                    outstanding_details = CustomerOutstanding.objects.filter(customer__customer_id=customer_id)
                    outstanding_serializer = CustomerOutstandingSerializer(outstanding_details, many=True).data
                    # Attach outstanding details to customer data
                    customer['outstanding_details'] = outstanding_serializer
                    # print("Customer ID:", customer_id)
                    # print("Outstanding Details:", outstanding_serializer)

            return Response(serializer)
        except Exception as e:
            print("Error:", str(e))
            return Response({"error": str(e)})


class ExpenseReportAPI(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        try:
            user_id = request.user.id
            if request.GET.get('date'):
                date_str = request.GET.get('date')
            else:
                date_str = datetime.today().date()
                
            expenses = Expense.objects.filter(van__salesman__pk=user_id,expense_date=date_str)
            
            serialized_data = SalesmanExpensesSerializer(expenses, many=True).data

            return Response({'status': True, 'data': serialized_data, 'message': 'Successful'})
        
        except Exception as e:
            return Response({'status': False, 'data': str(e), 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
class CashSaleReportAPI(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        try:
            user_id = request.user.id
            if request.GET.get('date'):
                date_str = request.GET.get('date')
            else:
                date_str = datetime.today().date()
                
            cashsale = Invoice.objects.filter(invoice_type="cash_invoice", created_date__date=date_str)
            serialized_data = CashSaleSerializer(cashsale, many=True).data
            
            return Response({'status': True, 'data': serialized_data, 'message': 'Cash Sales report passed!'})
        
        except Exception as e:
            return Response({'status': False, 'data': str(e), 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class CreditSaleReportAPI(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        try:
            user_id = request.user.id
            if request.GET.get('date'):
                date_str = request.GET.get('date')
            else:
                date_str = datetime.today().date()
                
            creditsale = Invoice.objects.filter(invoice_type="credit_invoive", created_date__date=date_str)
            serialized_data = CreditSaleSerializer(creditsale, many=True).data
            
            return Response({'status': True, 'data': serialized_data, 'message': 'Credit Sales report passed!'})
        
        except Exception as e:
            return Response({'status': False, 'data': str(e), 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
        

class VisitStatisticsAPI(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        try:
            user_id = request.user.id
            print("user_id", user_id)
            
            today_date = timezone.now().date()
            #new customers created
            salesman_customers_count = Customers.objects.filter(
                created_date__date=today_date, 
                sales_staff_id=user_id
            ).count()
            #emergency supply
            emergency_customers = DiffBottlesModel.objects.filter(created_date__date=today_date, assign_this_to_id=user_id).count()
            #actual visit
            visited_customers = CustomerSupply.objects.filter(salesman_id=user_id, created_date__date=today_date).count()
            
            visited_serializer = CustomerSupplySerializer(visited_customers, many=True)
            #non visit
            # non_visited_customers = Customers.objects.exclude(customer_supply__salesman_id=user_id, customer_supply__created_date__date=today_date)
            non_visited_customers = Customers.objects.annotate(num_visits=Count('customer_supply')).filter(num_visits=0)

            visited_serializer = CustomerSupplySerializer(CustomerSupply.objects.filter(salesman_id=user_id, created_date__date=today_date), many=True)
            non_visited_serializer = CustomersSerializer(non_visited_customers, many=True)
            
            return Response({
                'new_customers_count': salesman_customers_count,
                'emergency_supply_count': emergency_customers,
                'visited_customers_count': visited_customers,
                'visited_customers': visited_serializer.data,
                'non_visited_customers': non_visited_serializer.data,
                'status': True,
                'message': 'Visited and non-visited customers retrieved successfully!'
            })
        
        except Exception as e:
            return Response({
                'status': False,
                'data': str(e),
                'message': 'Something went wrong!'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FivegallonRelatedAPI(APIView):
    # authentication_classes = [BasicAuthentication]
    # permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        try:
            user_id = request.user.id
            print("user_id", user_id)
            
            today_date = timezone.now().date()
            
            today_customer_supplies = CustomerSupply.objects.filter(created_date__date=today_date)
            
            customers_data = []
            for supply in today_customer_supplies:
                customer_data = {
                    'customer_name': supply.customer.customer_name,
                    'building_name': supply.customer.building_name,
                    'room_no': supply.customer.door_house_no,
                    'empty_bottles_collected': supply.collected_empty_bottle,
                    'empty_bottle_pending': supply.allocate_bottle_to_pending,
                    'coupons_collected': supply.customer.customer_supplycoupon_set.filter(created_date__date=today_date).count(),
                    'pending_coupons': supply.customer.customer_supplycoupon_set.exclude(created_date__date=today_date).count()
                }
                customers_data.append(customer_data)
            
            return Response({
                'customers': customers_data,
                'status': True,
                'message': 'Customer supply data retrieved successfully!'
            })
        
        except Exception as e:
            return Response({
                'status': False,
                'data': str(e),
                'message': 'Something went wrong!'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            
class ShopInAPI(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request, customer_pk):
        try:
            user_id = request.user
            SalesmanSpendingLog.objects.create(
                customer=Customers.objects.get(pk=customer_pk),
                salesman=user_id,
                created_date=datetime.now(),
                shop_in=datetime.now(),
                )
            
            return Response({
                'status': True,
                'message': 'Shop In successfully!'
            })
        
        except Exception as e:
            return Response({
                'status': False,
                'data': str(e),
                'message': 'Something went wrong!'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
class ShopOutAPI(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request, customer_pk):
        try:
            user_id = request.user
            if (instances:=SalesmanSpendingLog.objects.filter(customer__pk=customer_pk,salesman=user_id,created_date__date=datetime.today().date())):
                instances.update(shop_out=datetime.now())
                
                return Response({
                    'status': True,
                    'message': 'Successfully!'
                })
            else:
                return Response({
                    'status': False,
                    'message': 'you are not shop in shopin first'
                })
        
        except Exception as e:
            return Response({
                'status': False,
                'data': str(e),
                'message': 'Something went wrong!'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
from django.utils import timezone

class SalesmanRequestAPI(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            serializer = SalesmanRequestSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(
                    salesman=request.user,
                    created_by=request.user,
                    created_date=timezone.now(),
                )
            
                return Response({
                    'status': True,
                    'message': 'Request Sent Successfully!'
                })
            else:
                return Response({
                    'status': False,
                    'data': serializer.errors,
                    'message': 'Validation Error!'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({
                'status': False,
                'data': str(e),
                'message': 'Something went wrong!'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
class TaxAPI(APIView):
    def get(self, request):
        try:
            instances = Tax.objects.all()
            serializer = TaxSerializer(instances,many=True)
            
            return Response({
                'status': True,
                'message': 'success!',
                'data': serializer.data
            })
        
        except Exception as e:
            return Response({
                'status': False,
                'data': str(e),
                'message': 'Something went wrong!'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CompetitorsAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CompetitorsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CompetitorsListAPIView(APIView):
    def get(self, request, format=None):
        competitors = Competitors.objects.all()
        serializer = CompetitorsSerializer(competitors, many=True)
        return Response(serializer.data)
               
# @api_view(['POST'])            
# @csrf_exempt 
# def market_share(request):
#     if request.method == 'POST':
#         customer_id = request.data.get('customer_id')
#         competitor_name = request.data.get('competitor_name')
#         price = request.data.get('price')
#         product = request.data.get('product')
        
        
#         if not customer_id or not price:
#             return Response({'error': 'customer_id and price are required'}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             market_share = MarketShare.objects.get(customer_id=customer_id)
#             market_share.price = price
#             market_share.competitor_name = competitor_name
#             market_share.product = product
#             market_share.save()
#             serializer = MarketShareSerializers(market_share)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except MarketShare.DoesNotExist:
#             return Response({'error': 'MarketShare with this customer_id does not exist'}, status=status.HTTP_404_NOT_FOUND)

class MarketShareAPI(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            serializer = MarketShareSerializers(data=request.data)
            if serializer.is_valid():
                serializer.save(
                    created_by=request.user,
                    created_date=timezone.now(),
                )
                return Response({
                    'status': True,
                    'data': serializer.data,
                    'message': 'market share added Successfully!'
                })
            else:
                return Response({
                    'status': False,
                    'data': serializer.errors,
                    'message': 'Validation Error!'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({
                'status': False,
                'data': str(e),
                'message': 'Something went wrong!' + str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CustomerLoginApi(APIView):
    def post(self, request, *args, **kwargs):
        # try:
        mobile_number = request.data.get('mobile_number')
        password = request.data.get('password')
        if (instances:=Customers.objects.filter(mobile_no=mobile_number)).exists():
            username = instances.first().user_id.username
            if username and password:
                user = authenticate(username=username, password=password)
                if user is not None:
                    # if user.is_active:
                    login(request, user)
                    user_obj = CustomUser.objects.filter(username=username).first()
                    token = generate_random_string(20)
                    
                    five_gallon = ProdutItemMaster.objects.get(product_name="5 Gallon")
                    if instances.first().rate != None and Decimal(instances.first().rate) > 0:
                        water_rate = instances.first().rate
                    else:
                        water_rate = five_gallon.rate
                        
                    data = {
                        'id': instances.first().custom_id,
                        'customer_pk': instances.first().customer_id,
                        'username': username,
                        'user_type': user_obj.user_type,
                        'sales_type': instances.first().sales_type,
                        'water_rate': water_rate,
                        'water_id': five_gallon.pk,
                        'token': token
                    }
                    # else:
                    #     return Response({'status': False, 'message': 'User Inactive!'})
                    return Response({'status': True, 'data': data, 'message': 'Authenticated User!'})
                else:
                    return Response({'status': False, 'message': 'Unauthenticated User!'})
            else:
                return Response({'status': False, 'message': 'Unauthenticated User!'})
        else:
            return Response({'status': False, 'message': 'This mobile Number not registered contact your salesman'})
        # except CustomUser.DoesNotExist:
        #     return Response({'status': False, 'message': 'User does not exist!'})
        # except Exception as e:
        #     print(f'Something went wrong: {e}')
        #     return Response({'status': False, 'message': 'Something went wrong!'})

class NextVisitDateAPI(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            customer = Customers.objects.get(user_id=request.user)
            if not customer.visit_schedule is None:
                next_visit_date = get_next_visit_date(customer.visit_schedule)
            
            return Response({
                'status': True,
                'message': 'success!',
                'data': str(next_visit_date)
            })
        
        except Exception as e:
            return Response({
                'status': False,
                'data': str(e),
                'message': 'Something went wrong!'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
class CustomerCouponBalanceAPI(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            pending_coupons = 0
            digital_coupons = 0
            manual_coupons = 0
            leaf_serializer = []
            
            if CustomerOutstandingReport.objects.filter(product_type="coupons",customer__user_id=request.user).exists() :
                pending_coupons = CustomerOutstandingReport.objects.get(product_type="coupons",customer__user_id=request.user).value
            
            if CustomerCouponStock.objects.filter(customer__user_id=request.user).exists() :
                customer_coupon_stock = CustomerCouponStock.objects.filter(customer__user_id=request.user)
            
                if (customer_coupon_stock_digital:=customer_coupon_stock.filter(coupon_method="digital")).exists() :
                    digital_coupons = customer_coupon_stock_digital.aggregate(total_count=Sum('count'))['total_count']
                if (customer_coupon_stock_manual:=customer_coupon_stock.filter(coupon_method="manual")).exists() :
                    manual_coupons = customer_coupon_stock_manual.aggregate(total_count=Sum('count'))['total_count']

                    customer_coupons_ids = CustomerCouponItems.objects.filter(customer_coupon__customer__user_id=request.user).values_list('coupon__pk')
                    coupon_leaflets = CouponLeaflet.objects.filter(coupon__pk__in=customer_coupons_ids,used=False)
                    leaf_serializer = CouponLeafSerializer(coupon_leaflets,many=True).data
                    
            bottle_conseption = CustomerSupplyItems.objects.filter(customer_supply__customer__user_id=request.user,product__product_name="5 Gallon").aggregate(total_count=Sum('quantity'))['total_count'] or 0
            
            return Response({
                'status': True,
                'message': 'success!',
                'data': {
                    'pending_coupons': pending_coupons,
                    'digital_coupons': digital_coupons,
                    'manual_coupons': manual_coupons,
                    'manual_coupon_leaflets': leaf_serializer,
                    'bottle_conseption_count': bottle_conseption
                },
            })
        
        except Exception as e:
            return Response({
                'status': False,
                'data': str(e),
                'message': 'Something went wrong!'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            
class CustomerOutstandingAPI(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            pending_coupons = 0
            pending_emptycan = 0
            pending_amount = 0
            
            if CustomerOutstandingReport.objects.filter(product_type="coupons",customer__user_id=request.user).exists() :
                pending_coupons = CustomerOutstandingReport.objects.get(product_type="coupons",customer__user_id=request.user).value
                
            if CustomerOutstandingReport.objects.filter(product_type="emptycan",customer__user_id=request.user).exists() :
                pending_emptycan = CustomerOutstandingReport.objects.get(product_type="emptycan",customer__user_id=request.user).value
                
            if CustomerOutstandingReport.objects.filter(product_type="amount",customer__user_id=request.user).exists() :
                pending_amount = CustomerOutstandingReport.objects.get(product_type="amount",customer__user_id=request.user).value
            
            return Response({
                'status': True,
                'message': 'success!',
                'data': {
                    'pending_coupons': pending_coupons,
                    'pending_emptycan': pending_emptycan,
                    'pending_amount': pending_amount,
                },
            })
        
        except Exception as e:
            return Response({
                'status': False,
                'data': str(e),
                'message': 'Something went wrong!'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            
# class OffloadCouponAPI(APIView):
#     def post(self, request):
#         product_id = request.data.get('product')
#         quantity = request.data.get('quantity')

#         try:
#             coupon = VanCouponStock.objects.get(pk=product_id)
#         except VanCouponStock.DoesNotExist:
#             return Response({"error": "Coupon does not exist"}, status=status.HTTP_404_NOT_FOUND)

#         try:
#             quantity = int(quantity) 
#         except ValueError:
#             return Response({"error": "Invalid quantity"}, status=status.HTTP_400_BAD_REQUEST)

#         if coupon.book_num is None or coupon.book_num < quantity:
#             return Response({"error": "Not enough coupons available"}, status=status.HTTP_400_BAD_REQUEST)

#         coupon.book_num -= quantity
#         coupon.save()

#         offload_data = {
#             'van': request.data.get('van'),
#             'product': product_id,
#             'quantity': quantity,
#             'stock_type': 'offload',
#             'created_by': str(request.user.id),
#             'modified_by': str(request.user.id),
#             'modified_date': datetime.now(),
#             'created_date': datetime.now()
#         }
#         serializer = OffloadVanSerializer(data=offload_data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)            


class PendingSupplyReportView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, route_id):
        try:
            date_str = request.GET.get("date_str", str(datetime.today().date()))
            date = datetime.strptime(date_str, '%Y-%m-%d')

            today_customers = find_customers(request, date_str, route_id)
            today_customer_ids = [str(customer['customer_id']) for customer in today_customers]

            today_supplied = CustomerSupply.objects.filter(created_date__date=date)
            today_supplied_ids = today_supplied.values_list('customer_id', flat=True)
            customers = Customers.objects.filter(pk__in=today_customer_ids).exclude(pk__in=today_supplied_ids)

            serializer = CustomerSupplySerializer(customers, many=True)
            return JsonResponse({'status': True, 'data': serializer.data, 'message': 'Pending Supply report passed!'})

        except Exception as e:
            return Response({'status': False, 'data': str(e), 'message': 'Something went wrong!'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
        
        
# class CustodyReportView(APIView):
#     def get(self, request):
#         user_id = request.user.id

#         # Get the date from the request, if provided
#         if request.GET.get('date'):
#             date_str = request.GET.get('date')
#         else:
#             date_str = datetime.today().date()
#         instances = CustodyCustom.objects.filter(created_date__date=date_str).order_by("-created_date")

#         serializer = CustodyCustomSerializer(instances, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

        
class BottleStockView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        try:
            user_id = request.user.id
            
            if request.GET.get("date"):
                date_str = request.GET.get("date")
            else :
                date_str = str(datetime.today().date())
                
            date = datetime.strptime(date_str, '%Y-%m-%d')
            van_stock = VanProductStock.objects.get(created_date=date,van__salesman=user_id,product__product_name="5 Gallon")
            
            total_vanstock = van_stock.opening_count + van_stock.stock - van_stock.damage_count
            fresh_bottle_count = van_stock.stock
            empty_bottle_count = van_stock.empty_can_count
            total_bottle_count = fresh_bottle_count + empty_bottle_count

            result = {
                'total_vanstock': total_vanstock,
                'fresh_bottle_count': fresh_bottle_count,
                'empty_bottle_count': empty_bottle_count,
                'total_bottle_count': total_bottle_count,
            }

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FreshcanEmptyBottleView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        try:
            user_id = request.user.id
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')

            if not (start_date and end_date):
                return Response({"error": "Both start_date and end_date are required."}, status=status.HTTP_400_BAD_REQUEST)

            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')

            customers = Customers.objects.filter(sales_staff__id=user_id)
            serialized_data = FreshCanVsEmptyBottleSerializer(customers, many=True, context={'start_date': start_datetime,'end_date':end_datetime}).data

            return Response({'status': True, 'data': serialized_data, 'message': 'Successfull'})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustodyReportView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):

        try:
            user_id = request.user.id
            print("user_id", user_id)
            start_date = request.data.get('start_date')
            end_date = request.data.get('end_date')

            if not (start_date and end_date):
                return Response({"error": "Both start_date and end_date are required."}, status=status.HTTP_400_BAD_REQUEST)

            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')

            
            customer_objs = Customers.objects.filter(sales_staff=user_id)
            serialized_data = CustomerCustodyReportSerializer(customer_objs,many=True, context={'start_date': start_datetime,'end_date':end_datetime}).data
            
            return Response({'status': True, 'data': serialized_data, 'message': 'Customer products list passed!'})
        
        except Exception as e:
            return Response({'status': False, 'data': str(e), 'message': 'Something went wrong!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FreshcanVsCouponView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user_id = request.user.id
            customer_objs = Customers.objects.filter(sales_staff=user_id)
            start_date = request.data.get('start_date')
            end_date = request.data.get('end_date')

            if not (start_date and end_date):
                return Response({"error": "Both start_date and end_date are required."}, status=status.HTTP_400_BAD_REQUEST)

            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')

            customers_serializer = FreshvsCouponCustomerSerializer(
                customer_objs, many=True, context={'request': request}
            )

            return Response(customers_serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomerCartAPIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        response_data = {}
        if CustomerCart.objects.filter(customer__user_id=request.user,order_status=False).exists():
            instance = CustomerCart.objects.get(customer__user_id=request.user,order_status=False)
            serializer = CustomerCartSerializer(instance, many=False)
        
            response_data = {
                "statusCode": status.HTTP_200_OK,
                "data" : serializer.data,
            }
        
            return Response(response_data, status=status.HTTP_200_OK)
        
        else:
            response_data = {
                "statusCode": status.HTTP_200_OK,
                "data" : [],
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        customer = Customers.objects.get(user_id=request.user)
        cart_data = request.data

        # Pass the entire request data to the CustomerCartPostSerializer
        cart_serializer = CustomerCartPostSerializer(data=cart_data)

        if cart_serializer.is_valid():
            # Check if there is an existing cart with order_status=False
            if (cart_instances := CustomerCart.objects.filter(customer__user_id=request.user, order_status=False)).exists():
                cart_instance = cart_instances.latest('-created_date')
            else:
                cart_instance = cart_serializer.save(
                    customer=customer,
                    created_by=customer.pk,
                    created_date=datetime.today()
                )
            
            # Process the single item in the request
            item_data = cart_data['items']
            product_id = item_data['product']

            # If the product is not already in the cart, proceed to add it
            cart_item_serializer = CustomerCartItemsPostSerializer(data=item_data)

            if cart_item_serializer.is_valid():
                cart_item_instance = cart_item_serializer.save(
                    customer_cart=cart_instance
                )
                
                # Calculate total amount for the item and update grand total
                cart_item_instance.total_amount = cart_item_instance.quantity * cart_item_instance.price
                cart_item_instance.save()

                cart_instance.grand_total += cart_item_instance.total_amount
                cart_instance.save()

                response_data = {
                    "statusCode": status.HTTP_201_CREATED,
                    "data": cart_serializer.data,
                    "message": "Successfully added",
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                response_data = {
                    "statusCode": status.HTTP_400_BAD_REQUEST,
                    "title": "Item Data Error",
                    "message": cart_item_serializer.errors,
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        else:
            response_data = {
                "statusCode": status.HTTP_400_BAD_REQUEST,
                "title": "Cart Data Error",
                "message": cart_serializer.errors,
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, *args, **kwargs):
        item_pk = request.data.get("item_pk")
        item_qty = request.data.get("item_qty")
        
        if item_pk :
            item = CustomerCartItems.objects.select_related('customer_cart').get(pk=item_pk)
            previous_total = item.total_amount
            
            item.quantity = item_qty
            item.total_amount = item.quantity * item.price
            item.save()

            cart = item.customer_cart
            
            cart.grand_total = cart.grand_total - previous_total + item.total_amount
            cart.save()
            
            serializer = CustomerCartSerializer(cart, many=False)
             
            response_data = {
                "statusCode": status.HTTP_200_OK,
                "title" : "Successfull",
                "data": serializer.data,
                "message" : "Item Quantity Updated",
            }
                
            return Response(response_data, status=status.HTTP_200_OK)
        
        else:
            response_data = {
                "statusCode": status.HTTP_400_BAD_REQUEST,
                "title" : "Error",
                "message" : "no item pk",
            }
            
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, *args, **kwargs):
        item_pk = request.data.get("item_pk")
        if item_pk :
            item = CustomerCartItems.objects.get(pk=item_pk)
            
            cart = CustomerCart.objects.get(pk=item.customer_cart.pk)
            cart.grand_total -= item.price
            cart.save()
            
            item.total_amount -= item.price
            item.save()
            item.delete()   
             
            response_data = {
                "statusCode": status.HTTP_200_OK,
                "title" : "Successfull",
                "message" : "Item Removed from Cart",
            }
                
            return Response(response_data, status=status.HTTP_200_OK)
        
        else:
            response_data = {
                "statusCode": status.HTTP_400_BAD_REQUEST,
                "title" : "Error",
                "message" : "no item pk",
            }
            
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

class CustomerOrdersAPIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
       
        customer = Customers.objects.get(user_id=request.user)
        orders = CustomerOrders.objects.filter(customer=customer) 
        
        serializer = CustomerOrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        cart_id = request.data.get("cart_id")
        customer = Customers.objects.get(user_id=request.user)
        
        if cart_id :
            customer_cart = CustomerCart.objects.get(pk=cart_id)
            customer_cart_items = CustomerCartItems.objects.filter(customer_cart=customer_cart)
            
            if (customer_order_instances:=CustomerOrders.objects.filter(customer__user_id=request.user,created_date__date=datetime.today().date(),order_status="pending")).exists():
                customer_order_instance = customer_order_instances.first()
            else:
                customer_order_instance = CustomerOrders.objects.create(
                    customer=customer_cart.customer,
                    delivery_date=customer_cart.delivery_date,
                    grand_total=customer_cart.grand_total,
                    order_status="pending",
                    created_by=request.user.id,
                    created_date=datetime.today(),
                )
                
            for cart_item in customer_cart_items:
                customer_order_item_instance,create = CustomerOrdersItems.objects.get_or_create(
                    customer_order=customer_order_instance,
                    product=cart_item.product,
                )
                
                customer_order_item_instance.quantity += cart_item.quantity
                customer_order_item_instance.price += cart_item.price
                customer_order_item_instance.total_amount += customer_order_item_instance.quantity * customer_order_item_instance.price
                customer_order_item_instance.save()
                
                customer_order_instance.grand_total += customer_order_item_instance.total_amount
                customer_order_instance.save()
                
            customer_cart.order_status = True
            customer_cart.save()
                
            customer_cart.order_status = True
            customer_cart.save()
                
            response_data = {
                "statusCode": status.HTTP_201_CREATED,
                "title" : "successfull",
                "message" : "order created successfull",
            }
                
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        else:
            response_data = {
                "statusCode": status.HTTP_400_BAD_REQUEST,
                "title" : "Error",
                "message" : "no cart id",
            }
            
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    
    
#-----------------Supervisor app----------Production API------------
class ProductListAPIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        products = Product.objects.all().order_by('-created_date')
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProductCreateAPIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ProductCreateSerializer(data=request.data)
        if serializer.is_valid():
            product_name = serializer.validated_data.get('product_name')
            quantity = serializer.validated_data.get('quantity')
            product_item = get_object_or_404(ProdutItemMaster, pk=product_name.id)
            
            product = Product(
                product_name=product_item,
                created_by=str(request.user.id),
                branch_id=request.user.branch_id,
                quantity=quantity
            )
            product.save()
            if request.user.branch_id:
                try:
                    branch_id = request.user.branch_id.branch_id
                    branch = BranchMaster.objects.get(branch_id=branch_id)
                    product.branch_id = branch
                    
                    stock_instance, created = ProductStock.objects.get_or_create(
                        product_name=product.product_name,
                        branch=product.branch_id,
                        defaults={'quantity': int(product.quantity)}
                    )
                    if not created:
                        stock_instance.quantity += int(product.quantity)
                        stock_instance.save()
                except BranchMaster.DoesNotExist:
                    return Response({'detail': 'Branch information not found for the current user.'}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'detail': 'Product Successfully Added.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class DispensersAndCoolersPurchasesAPIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        products = CustomerOrders.objects.filter(customer__user_id=request.user,product__product_name__in=['Hot and Cool', 'Dispenser'])
        serializer = CustomerOrderssSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class CustomerCouponPurchaseView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        coupon_category_products = ProdutItemMaster.objects.filter(category__category_name='Coupons')
        # print("coupon_category_products",coupon_category_products)
        coupon_product_ids = coupon_category_products.values_list('id', flat=True)
        # print("coupon_product_ids",coupon_product_ids)
        customer_orders = CustomerOrders.objects.filter(customer__user_id=request.user,product__in=coupon_product_ids)
        print("customer_orders",customer_orders)

        serializer = CustomerCouponPurchaseSerializer(customer_orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)    


class WaterBottlePurchaseAPIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        products = CustomerOrders.objects.filter(customer__user_id=request.user.id, product__category__category_name='Water')
        serializer = WaterCustomerOrderSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class CustodyCustomerView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        queryset = CustomerCustodyStock.objects.filter(customer__user_id=user_id)
        serializer = CustomerCustodyStocksSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



    
class StockMovementCreateAPI(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = StockMovementSerializer(data=request.data,context={"request":request})
        if serializer.is_valid():
            stock_movement = serializer.save()
            return Response({
                'status': 'success',
                'data': {
                    'id': stock_movement.id,
                    'salesman': stock_movement.salesman.id,
                    'from_van': stock_movement.from_van.van_id, 
                    'to_van': stock_movement.to_van.van_id, 
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class StockMovementDetailsAPIView(ListAPIView):
    queryset = StockMovement.objects.all()
    serializer_class = StockMovementSerializer


class NonVisitReasonAPIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        try:
            reasons = NonVisitReason.objects.all()
            serializer = NonVisitReasonSerializer(reasons, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except NonVisitReason.DoesNotExist:
            raise Http404("No reasons found")
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class CustomerComplaintCreateView(APIView):
    def get(self, request, *args, **kwargs):
        complaints = CustomerComplaint.objects.all()
        serializer = CustomerComplaintSerializer(complaints, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = CustomerComplaintSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class NonVisitReportCreateAPIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve the authenticated user (salesman)
            salesman = request.user
            customer_id = request.data.get('customer')
            reason_text = request.data.get('reason')
            supply_date = request.data.get('supply_date')

            # Retrieve customer by ID
            customer = Customers.objects.get(customer_id=customer_id)
            
            # Retrieve reason by reason_text
            reason = NonVisitReason.objects.get(reason_text=reason_text)

            # Check if the customer is a pending customer (not visited)
            if CustomerSupply.objects.filter(customer=customer, salesman=salesman, created_date__date=supply_date).exists():
                return Response({'status': False, 'message': 'Customer has already been supplied on the given date.'}, status=status.HTTP_400_BAD_REQUEST)

            # Create the non-visit report
            nonvisit_report = NonvisitReport.objects.create(
                customer=customer,
                salesman=salesman,
                reason=reason,
                supply_date=supply_date
            )

            serializer = NonvisitReportSerializer(nonvisit_report)
            return Response({'status': True, 'data': serializer.data, 'message': 'Non-visit report created successfully!'}, status=status.HTTP_201_CREATED)
        
        except Customers.DoesNotExist:
            return Response({'status': False, 'message': 'Customer not found.'}, status=status.HTTP_404_NOT_FOUND)
        except NonVisitReason.DoesNotExist:
            return Response({'status': False, 'message': 'Non-visit reason not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'status': False, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def get(self, request, *args, **kwargs):
        try:
            customer_id = request.data.get('customer')

            if not customer_id:
                return Response({'status': False, 'message': 'Customer ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

            # Retrieve customer by ID
            customer = Customers.objects.get(customer_id=customer_id)

            # Retrieve non-visit reports for the customer
            nonvisit_reports = NonvisitReport.objects.filter(customer=customer)

            serializer = NonvisitReportDetailSerializer(nonvisit_reports, many=True)
            return Response({'status': True, 'data': serializer.data, 'message': 'Non-visit reports retrieved successfully!'}, status=status.HTTP_200_OK)

        except Customers.DoesNotExist:
            return Response({'status': False, 'message': 'Customer not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'status': False, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Send_Device_API(APIView):
    def post(self,request):
        device_token = request.data['device_token']
        user_id = request.data['user_id']
      
        user_not = Send_Notification.objects.filter(user=user_id).exists()
        
        if user_not :
           
            Send_Notification.objects.filter(user=user_id).update(device_token=device_token)
        else :
           
            Send_Notification.objects.create(user=CustomUser.objects.get(id=user_id),device_token=device_token)
        return Response({"status": True, 'data':[{"user_id":user_id,"device_token":device_token}], "message": "Succesfully !"})
    
class CustomerDeviceTokenAPI(APIView):
    def post(self,request):
        device_token = request.data['device_token']
        customer_id = request.data['customer_id']
        
        customer_user_id = Customers.objects.get(pk=customer_id).user_id.pk
        user_not = Send_Notification.objects.filter(user__pk=customer_user_id).exists()
        
        if user_not :
           
            Send_Notification.objects.filter(user__pk=customer_user_id).update(device_token=device_token)
        else :
           
            Send_Notification.objects.create(user=CustomUser.objects.get(pk=customer_user_id),device_token=device_token)
        return Response({"status": True, 'data':[{"user_id":customer_user_id,"device_token":device_token}], "message": "Succesfully !"})

class MyCurrentStockView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, van_id, *args, **kwargs):
        user = request.user.id
        van = get_object_or_404(Van, van_id=van_id)
        van_coupon_stocks = VanCouponStock.objects.filter(van=van)
        total_coupons = van_coupon_stocks.aggregate(total=Sum('count'))['total'] or 0

        serializer = VanCouponsStockSerializer(van_coupon_stocks, many=True)

        data = {
            'total_coupons': total_coupons,
            'coupons': serializer.data
        }

        return Response(data)

class PotentialBuyersAPI(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        salesman = request.user
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')

        if not (start_date and end_date):
            return Response({"error": "Both start_date and end_date are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)  # Include end date
        except ValueError:
            return Response({"error": "Invalid date format. Use 'YYYY-MM-DD'."}, status=status.HTTP_400_BAD_REQUEST)

        customers = Customers.objects.filter(
            sales_staff=salesman,
            sales_type='CASH COUPON',
            created_date__gte=start_datetime,
            created_date__lt=end_datetime).annotate(
            digital_coupons_count=Count('customercoupon', filter=Q(customercoupon__coupon_method='digital')),
            manual_coupons_count=Count('customercoupon', filter=Q(customercoupon__coupon_method='manual'))
        ).filter(digital_coupons_count__lt=5, manual_coupons_count__lt=5)

        customer_count=customers.count()
        print("customer_count",customer_count)
        customer_coupon_counts = [
            {
                'customer_name': customer.customer_name,
                'building_name': customer.building_name,
                'digital_coupons_count': customer.digital_coupons_count,
                'manual_coupons_count': customer.manual_coupons_count
            }
            for customer in customers
        ]

        serializer = PotentialBuyersSerializer(customer_coupon_counts, many=True)
        return Response(serializer.data)

class CustomerWiseCouponSaleAPIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        print("user_id", user_id)
        
        customer_objs = Customers.objects.filter(sales_staff=user_id)
        print("customer_objs", customer_objs)
        
        total_coupons = CustomerCouponStock.objects.filter(customer__in=customer_objs).aggregate(total=Sum('count'))['total'] or 0
        print("total_coupons", total_coupons)
        
        response_data = []
        
        for customer in customer_objs:
            customer_total_coupons = CustomerCouponStock.objects.filter(customer=customer).aggregate(total=Sum('count'))['total'] or 0
            response_data.append({
                "customer_name": customer.customer_name,
                "total_coupons": customer_total_coupons
            })
        
        return Response(response_data, status=status.HTTP_200_OK)
    
class TotalCouponsConsumedView(APIView):
    
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        salesman = request.user

        # Fetch query parameters
        start_date_str = request.data.get('start_date')
        end_date_str = request.data.get('end_date')
        customer_id = request.data.get('customer_id', None)
        
        # Date conversion
        if not (start_date_str and end_date_str):
            start_date = datetime.today().date()
            end_date = datetime.today().date()
        else:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        
        # Filter criteria for digital and manual coupons
        total_digital_leaflets = CustomerSupplyDigitalCoupon.objects.filter(
            customer_supply__salesman=salesman,
            customer_supply__created_date__date__gte=start_date,
            customer_supply__created_date__date__lte=end_date,
        ).aggregate(total_digital_leaflets=Sum('count'))['total_digital_leaflets'] or 0
        
        # Aggregate manual coupons (normal and free)
        total_manual_leaflets_normal = CustomerSupplyCoupon.objects.filter(
            customer_supply__created_date__date__gte=start_date,
            customer_supply__created_date__date__lte=end_date,
            customer_supply__salesman=salesman,
            leaf__coupon__leaflets__used=False
        ).aggregate(total_manual_leaflets=Count('leaf'))['total_manual_leaflets'] or 0

        total_manual_leaflets_free = CustomerSupplyCoupon.objects.filter(
            customer_supply__created_date__date__gte=start_date,
            customer_supply__created_date__date__lte=end_date,
            customer_supply__salesman=salesman,
            free_leaf__coupon__leaflets__used=False
        ).aggregate(total_manual_leaflets=Count('free_leaf'))['total_manual_leaflets'] or 0

        # Total manual leaflets
        total_manual_leaflets = total_manual_leaflets_normal + total_manual_leaflets_free
        
        # Prepare customer data list
        customer_data = []
        customer_supplies = CustomerSupply.objects.filter(
            salesman=salesman,
            created_date__date__gte=start_date,
            created_date__date__lte=end_date
        )
        
        if customer_id:
            customer_supplies = customer_supplies.filter(customer__customer_id=customer_id)

        # Populate customer data
        for supply in customer_supplies:
            customer = supply.customer
            created_date = supply.created_date

            customer_data.append({
                'created_date': created_date.date(),  
                'customer_id': customer.customer_id,
                'customer_name': customer.customer_name,
                'custom_id': customer.custom_id,
                'building_name': customer.building_name,
                'address': customer.billing_address,
                'total_digital_coupons_consumed': total_digital_leaflets,
                'total_manual_coupons_consumed': total_manual_leaflets
            })
        
        # Serialize the data (do not use `many=True` with a dict)
        serializer = TotalCouponsSerializer(customer_data, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
#---------------Offload API---------------------------------- 

   
class OffloadRequestingAPIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        products_data = []
        product_items = ProdutItemMaster.objects.all()
        
        # Filtering products based on today's date and salesman
        products = VanProductStock.objects.filter(
            created_date=datetime.today().date(),
            van__salesman=request.user
        )

        # Filtering coupons based on today's date and salesman
        coupons = VanCouponStock.objects.filter(
            created_date=datetime.today().date(),
            van__salesman=request.user,
            stock__gt=0
        )
        
        for item in product_items:
            if item.category.category_name != "Coupons":
                if item.product_name == "5 Gallon":
                    if products.filter(product=item).aggregate(total_stock=Sum('stock'))['total_stock'] or 0 > 0:
                        van_stock = products.filter(product=item).aggregate(total_stock=Sum('stock'))['total_stock'] or 0
                        offload_request_stock = OffloadRequestItems.objects.filter(product=item,offload_request__van__salesman=request.user,offload_request__date=datetime.today().date(),offload_request__status=False,stock_type="stock").aggregate(total_stock=Sum('quantity'))['total_stock'] or 0
                        
                        if van_stock > offload_request_stock :
                            current_stock = van_stock - offload_request_stock
                        else:
                            current_stock = offload_request_stock - van_stock
                            
                        products_data.append({
                            "id": item.id,
                            "product_name": f"{item.product_name} (Fresh Can)",
                            "current_stock":  current_stock,
                            "stock_type": "stock",
                            
                        })
                    if products.filter(product=item).aggregate(total_stock=Sum('empty_can_count'))['total_stock'] or 0 > 0:
                        van_empty = products.filter(product=item).aggregate(total_stock=Sum('empty_can_count'))['total_stock'] or 0
                        offload_request_empty = OffloadRequestItems.objects.filter(product=item,offload_request__van__salesman=request.user,offload_request__date=datetime.today().date(),offload_request__status=False,stock_type="emptycan").aggregate(total_stock=Sum('quantity'))['total_stock'] or 0
                        
                        if van_empty > offload_request_empty :
                            current_empty = van_empty - offload_request_empty
                        else:
                            current_empty = offload_request_empty - van_empty
                            
                        products_data.append({
                            "id": item.id,
                            "product_name": f"{item.product_name} (Empty Can)",
                            "current_stock": current_empty ,
                            "stock_type": "emptycan",
                            
                        })
                    if products.filter(product=item).aggregate(total_stock=Sum('return_count'))['total_stock'] or 0 > 0:
                        van_return = products.filter(product=item).aggregate(total_stock=Sum('return_count'))['total_stock'] or 0
                        offload_request_return = OffloadRequestItems.objects.filter(product=item,offload_request__van__salesman=request.user,offload_request__date=datetime.today().date(),offload_request__status=False,stock_type="return").aggregate(total_stock=Sum('quantity'))['total_stock'] or 0
                        
                        if van_return > offload_request_return :
                            current_return = van_return - offload_request_return
                        else:
                            current_return = offload_request_return - van_return
                            
                        products_data.append({
                            "id": item.id,
                            "product_name": f"{item.product_name} (Return Can)",
                            "current_stock": current_return ,
                            "stock_type": "return",
                            
                        })
                elif item.product_name != "5 Gallon" and item.category.category_name != "Coupons":
                    if products.filter(product=item).aggregate(total_stock=Sum('stock'))['total_stock'] or 0 > 0:
                        van_non_five_gallon = products.filter(product=item).aggregate(total_stock=Sum('stock'))['total_stock'] or 0
                        offload_request_non_five_gallon = OffloadRequestItems.objects.filter(product=item,offload_request__van__salesman=request.user,offload_request__date=datetime.today().date(),offload_request__status=False,stock_type="stock").aggregate(total_stock=Sum('quantity'))['total_stock'] or 0
                        
                        if van_non_five_gallon > offload_request_non_five_gallon :
                            current_non_five_gallon = van_non_five_gallon - offload_request_non_five_gallon
                        else:
                            current_non_five_gallon = offload_request_non_five_gallon - van_non_five_gallon
                            
                        products_data.append({
                            "id": item.id,
                            "product_name": f"{item.product_name}",
                            "current_stock": current_non_five_gallon ,
                            "stock_type": "stock",
                            
                        })
            elif item.category.category_name == "Coupons":
                # Aggregate stock for coupons
                coupons_list = coupons.filter(coupon__coupon_type__coupon_type_name=item.product_name)
                van_coupon_stock = coupons_list.aggregate(total_stock=Sum('stock'))['total_stock'] or 0
                coupon_offload_request_stock = OffloadRequestCoupon.objects.filter(
                    coupon__coupon_type__coupon_type_name=item.product_name,
                    offload_request__van__salesman=request.user,
                    offload_request__date=datetime.today().date(),
                    offload_request__status=False,
                    stock_type="stock"
                    ).aggregate(total_stock=Sum('quantity'))['total_stock'] or 0
                 
                if van_coupon_stock > coupon_offload_request_stock :
                    total_stock = van_coupon_stock - coupon_offload_request_stock
                else:
                    total_stock = coupon_offload_request_stock - van_coupon_stock
                    
                serializer = OffloadRequestVanStockCouponsSerializer(coupons_list,many=True)
                if total_stock > 0:
                    products_data.append({
                        "id": item.id,
                        "product_name": f"{item.product_name}",
                        "current_stock": total_stock,
                        "stock_type": "stock",
                        
                        "coupons": serializer.data,
                        
                    })

        response_data = {
            "status": "true",
            "products": products_data,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        van = Van.objects.get(salesman=request.user)
        items = data.get('items', [])

        offload_request, created = OffloadRequest.objects.get_or_create(
            van=van,
            salesman=request.user,
            created_by=request.user.username,  # Assuming username is preferred
            created_date=datetime.today(),
            date=datetime.today().date()
        )

        for item in items:
            product_id = item.get('product')
            quantity = item.get('quantity', 1)
            stock_type = item.get('stock_type')
            
            product = ProdutItemMaster.objects.get(pk=product_id)

            offload_item, created = OffloadRequestItems.objects.get_or_create(
                offload_request=offload_request,
                product=product,
                stock_type=stock_type
            )
            offload_item.quantity += quantity
            offload_item.save()

            if stock_type == 'return':
                if item.get('other_reason', ''):
                    reason = item.get('other_reason', '')
                else:
                    reason = "Nill"
                    
                if (return_instances:=OffloadRequestReturnStocks.objects.filter(offload_request_item=offload_item)).exists():
                    offload_return = return_instances.latest('offload_request_item__created_date')
                else:
                    offload_return = OffloadRequestReturnStocks.objects.create(
                        offload_request_item=offload_item,
                        other_reason=reason,
                        )
                offload_return.scrap_count += item.get('scrap_count', 0),
                offload_return.washing_count += item.get('washing_count', 0),
                offload_return.other_quantity += item.get('other_quantity', 0),
                offload_return.save()
                    
            elif product.category.category_name == "Coupons":
                coupons = item.get('coupons', [])
                for coupon in coupons:
                    couponid = coupon.get("coupon_id")
                    coupon_instance = NewCoupon.objects.get(pk=couponid)
                    
                    OffloadCoupon.objects.create(
                        coupon=coupon_instance,
                        offload_request=offload_request,
                        quantity=1,
                        stock_type=stock_type
                    )

        return Response({'status': 'true', 'message': 'Offload request created successfully.'}, status=status.HTTP_201_CREATED)


class EditProductAPIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            products = request.data.get('products', [])
            
            with transaction.atomic():
                for product_data in products:
                    product_id = product_data.get('product_id')
                    count = int(product_data.get('count', 0))
                    stock_type = product_data.get('stock_type')
                    
                    try:
                        item = VanProductStock.objects.get(pk=product_id)
                    except VanProductStock.DoesNotExist:
                        return Response({
                            "status": "false",
                            "title": "Failed",
                            "message": f"Product with ID {product_id} not found",
                        }, status=status.HTTP_404_NOT_FOUND)

                    # Check if there is a pending offload request
                    offload_request = OffloadRequest.objects.filter(product=item.product).first()
                    if not offload_request or offload_request.quantity < count:
                        return Response({
                            "status": "false",
                            "title": "Failed",
                            "message": f"Requested quantity not met for product ID {product_id}",
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    # Deduct the requested quantity
                    offload_request.quantity -= count
                    # if offload_request.quantity <= 0:
                    #     offload_request.delete()
                    # else:
                    offload_request.save()

                    # Perform the offload operation
                    if item.product.product_name == "5 Gallon" and stock_type == "empty_can":
                        item.empty_can_count -= count
                        item.save()
                        emptycan=EmptyCanStock.objects.create(
                            product=item.product,
                            quantity=int(count)
                        )
                        emptycan.save()
                    elif item.product.product_name == "5 Gallon" and stock_type == "return_count":
                        scrap_count = int(product_data.get('scrap_count', 0))
                        washing_count = int(product_data.get('washing_count', 0))
                        other_quantity = int(product_data.get('other_quantity', 0))
                        other_reason = product_data.get('other_reason', '')
                        
                        OffloadReturnStocks.objects.create(
                            created_by=request.user.id,
                            created_date=timezone.now(),
                            salesman=item.van.salesman,
                            van=item.van,
                            product=item.product,
                            scrap_count=scrap_count,
                            washing_count=washing_count,
                            other_quantity=other_quantity,
                            other_reason=other_reason,
                        )
                        
                        if scrap_count > 0:
                            scrap_instance, created = ScrapProductStock.objects.get_or_create(
                                created_date__date=timezone.now().date(), product=item.product,
                                defaults={'created_by': request.user.id, 'created_date': timezone.now(), 'quantity': scrap_count}
                            )
                            if not created:
                                scrap_instance.quantity += scrap_count
                                scrap_instance.save()
                        
                        if washing_count > 0:
                            washing_instance, created = WashingProductStock.objects.get_or_create(
                                created_date__date=timezone.now().date(), product=item.product,
                                defaults={'created_by': request.user.id, 'created_date': timezone.now(), 'quantity': washing_count}
                            )
                            if not created:
                                washing_instance.quantity += washing_count
                                washing_instance.save()
                        
                        item.return_count -= (scrap_count + washing_count)
                        item.save()
                    elif item.product.product_name == "5 Gallon" and stock_type == "stock":
                        item.stock -= count
                        item.save()
                        
                        product_stock = ProductStock.objects.get(branch=item.van.branch_id, product_name=item.product)
                        product_stock.quantity += count
                        product_stock.save()
                    
                    Offload.objects.create(
                        created_by=request.user.id,
                        created_date=timezone.now(),
                        salesman=item.van.salesman,
                        van=item.van,
                        product=item.product,
                        quantity=count,
                        stock_type=stock_type
                    )
                
                response_data = {
                    "status": "true",
                    "title": "Successfully Offloaded",
                    "message": "Offload successfully.",
                    'reload': 'true',
                }
                
                return Response(response_data, status=status.HTTP_200_OK)
        
        except VanProductStock.DoesNotExist:
            return Response({
                "status": "false",
                "title": "Failed",
                "message": "One or more items not found",
            }, status=status.HTTP_404_NOT_FOUND)
        
        except IntegrityError as e:
            response_data = {
                "status": "false",
                "title": "Failed",
                "message": str(e),
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            response_data = {
                "status": "false",
                "title": "Failed",
                "message": str(e),
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class EditProductAPIView(APIView):
#     authentication_classes = [BasicAuthentication]
#     permission_classes = [IsAuthenticated]

    
    # def post(self, request):
    #     try:
    #         products = request.data.get('products', [])
            
    #         with transaction.atomic():
    #             for product_data in products:
    #                 product_id = product_data.get('product_id')
    #                 count = int(product_data.get('count', 0))
    #                 stock_type = product_data.get('stock_type')
                    
    #                 item = VanProductStock.objects.get(pk=product_id)

    #                 # Check if there is a pending offload request
    #                 offload_request = OffloadRequest.objects.filter(product=item.product).first()
    #                 if not offload_request or offload_request.quantity < count:
    #                     return Response({
    #                         "status": "false",
    #                         "title": "Failed",
    #                         "message": "Requested quantity not met",
    #                     }, status=status.HTTP_400_BAD_REQUEST)
                    
    #                 # Deduct the requested quantity
    #                 offload_request.quantity -= count
    #                 # if offload_request.quantity <= 0:
    #                 #     offload_request.delete()
    #                 # else:
    #                 offload_request.save()

    #                 # Perform the offload operation
    #                 if stock_type == "empty_can":
    #                     item.empty_can_count -= count
    #                     item.save()
    #                 elif stock_type == "return_count":
    #                     scrap_count = int(product_data.get('scrap_count', 0))
    #                     washing_count = int(product_data.get('washing_count', 0))
    #                     other_quantity = int(product_data.get('other_quantity', 0))
    #                     other_reason = product_data.get('other_reason', '')
                        
    #                     OffloadReturnStocks.objects.create(
    #                         created_by=request.user.id,
    #                         created_date=timezone.now(),
    #                         salesman=item.van.salesman,
    #                         van=item.van,
    #                         product=item.product,
    #                         scrap_count=scrap_count,
    #                         washing_count=washing_count,
    #                         other_quantity=other_quantity,
    #                         other_reason=other_reason,
    #                     )
                        
    #                     if scrap_count > 0:
    #                         scrap_instance, created = ScrapProductStock.objects.get_or_create(
    #                             created_date__date=timezone.now().date(), product=item.product,
    #                             defaults={'created_by': request.user.id, 'created_date': timezone.now(), 'quantity': scrap_count}
    #                         )
    #                         if not created:
    #                             scrap_instance.quantity += scrap_count
    #                             scrap_instance.save()
                        
    #                     if washing_count > 0:
    #                         washing_instance, created = WashingProductStock.objects.get_or_create(
    #                             created_date__date=timezone.now().date(), product=item.product,
    #                             defaults={'created_by': request.user.id, 'created_date': timezone.now(), 'quantity': washing_count}
    #                         )
    #                         if not created:
    #                             washing_instance.quantity += washing_count
    #                             washing_instance.save()
                        
    #                     item.return_count -= (scrap_count + washing_count)
    #                     item.save()
    #                 elif stock_type == "stock":
    #                     item.stock -= count
    #                     item.save()
                        
    #                     product_stock = ProductStock.objects.get(branch=item.van.branch_id, product_name=item.product)
    #                     product_stock.quantity += count
    #                     product_stock.save()
                    
    #                 Offload.objects.create(
    #                     created_by=request.user.id,
    #                     created_date=timezone.now(),
    #                     salesman=item.van.salesman,
    #                     van=item.van,
    #                     product=item.product,
    #                     quantity=count,
    #                     stock_type=stock_type
    #                 )
                
    #             response_data = {
    #                 "status": "true",
    #                 "title": "Successfully Offloaded",
    #                 "message": "Offload successfully.",
    #                 'reload': 'true',
    #             }
                
    #             return Response(response_data, status=status.HTTP_200_OK)
        
    #     except VanProductStock.DoesNotExist:
    #         return Response({
    #             "status": "false",
    #             "title": "Failed",
    #             "message": "One or more items not found",
    #         }, status=status.HTTP_404_NOT_FOUND)
        
    #     except IntegrityError as e:
    #         response_data = {
    #             "status": "false",
    #             "title": "Failed",
    #             "message": str(e),
    #         }
    #         return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
    #     except Exception as e:
    #         response_data = {
    #             "status": "false",
    #             "title": "Failed",
    #             "message": str(e),
    #         }
    #         return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class EditProductAPIView(APIView):
#     authentication_classes = [BasicAuthentication]
#     permission_classes = [IsAuthenticated]

    # def post(self, request):
    #     try:
    #         products = request.data.get('products', [])
            
    #         with transaction.atomic():
    #             for product_data in products:
    #                 product_id = product_data.get('product_id')
    #                 count = int(product_data.get('count', 0))
    #                 stock_type = product_data.get('stock_type')
                    
    #                 item = VanProductStock.objects.get(pk=product_id)
                    
    #                 if stock_type == "empty_can":
    #                     item.empty_can_count -= count
    #                     item.save()
    #                 elif stock_type == "return_count":
    #                     scrap_count = int(product_data.get('scrap_count', 0))
    #                     washing_count = int(product_data.get('washing_count', 0))
    #                     other_quantity = int(product_data.get('other_quantity', 0))
    #                     other_reason = product_data.get('other_reason', '')
                        
    #                     OffloadReturnStocks.objects.create(
    #                         created_by=request.user.id,
    #                         created_date=timezone.now(),
    #                         salesman=item.van.salesman,
    #                         van=item.van,
    #                         product=item.product,
    #                         scrap_count=scrap_count,
    #                         washing_count=washing_count,
    #                         other_quantity=other_quantity,
    #                         other_reason=other_reason,
    #                     )
                        
    #                     if scrap_count > 0:
    #                         scrap_instance, created = ScrapProductStock.objects.get_or_create(
    #                             created_date__date=timezone.now().date(), product=item.product,
    #                             defaults={'created_by': request.user.id, 'created_date': timezone.now(), 'quantity': scrap_count}
    #                         )
    #                         if not created:
    #                             scrap_instance.quantity += scrap_count
    #                             scrap_instance.save()
                        
    #                     if washing_count > 0:
    #                         washing_instance, created = WashingProductStock.objects.get_or_create(
    #                             created_date__date=timezone.now().date(), product=item.product,
    #                             defaults={'created_by': request.user.id, 'created_date': timezone.now(), 'quantity': washing_count}
    #                         )
    #                         if not created:
    #                             washing_instance.quantity += washing_count
    #                             washing_instance.save()
                        
    #                     item.return_count -= (scrap_count + washing_count)
    #                     item.save()
    #                 elif stock_type == "stock":
    #                     item.stock -= count
    #                     item.save()
                        
    #                     product_stock = ProductStock.objects.get(branch=item.van.branch_id, product_name=item.product)
    #                     product_stock.quantity += count
    #                     product_stock.save()
                    
    #                 Offload.objects.create(
    #                     created_by=request.user.id,
    #                     created_date=timezone.now(),
    #                     salesman=item.van.salesman,
    #                     van=item.van,
    #                     product=item.product,
    #                     quantity=count,
    #                     stock_type=stock_type
    #                 )
                
    #             response_data = {
    #                 "status": "true",
    #                 "title": "Successfully Offloaded",
    #                 "message": "Offload successfully.",
    #                 'reload': 'true',
    #             }
                
    #             return Response(response_data, status=status.HTTP_200_OK)
        
    #     except VanProductStock.DoesNotExist:
    #         return Response({
    #             "status": "false",
    #             "title": "Failed",
    #             "message": "One or more items not found",
    #         }, status=status.HTTP_404_NOT_FOUND)
        
    #     except IntegrityError as e:
    #         response_data = {
    #             "status": "false",
    #             "title": "Failed",
    #             "message": str(e),
    #         }
    #         return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
    #     except Exception as e:
    #         response_data = {
    #             "status": "false",
    #             "title": "Failed",
    #             "message": str(e),
    #         }
    #         return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
    # def post(self, request):
    #     count = request.data.get('count')
    #     stock_type = request.data.get('stock_type')
    #     product_id = request.data.get('product_id')
    #     product_category = request.data.get('product_category')
    #     try:
    #         item = VanProductStock.objects.get(product=product_id)
    #     except VanProductStock.DoesNotExist:
    #         return Response({
    #             "status": "false",
    #             "title": "Failed",
    #             "message": "Item not found",
    #         }, status=status.HTTP_404_NOT_FOUND)

    #     try:
    #         with transaction.atomic():
    #             item_stock = item.stock
    #             if stock_type == "empty_can":
    #                 item_stock = item.empty_can_count

    #             if item.product.product_name == "5 Gallon" and stock_type == "stock":
    #                 item.stock -= int(count)
    #                 item.save()

    #                 product_stock = ProductStock.objects.get(branch=item.van.branch_id, product_name=item.product)
    #                 product_stock.quantity += int(count)
    #                 product_stock.save()

    #             elif item.product.product_name == "5 Gallon" and stock_type == "empty_can":
    #                 item.empty_can_count -= int(count)
    #                 item.save()

    #             elif item.product.product_name == "5 Gallon" and stock_type == "return_count":
    #                 scrap_count = int(request.data.get('scrap_count', 0))
    #                 washing_count = int(request.data.get('washing_count', 0))
    #                 other_quantity = int(request.data.get('other_quantity', 0))
    #                 other_reason = request.data.get('other_reason')

    #                 OffloadReturnStocks.objects.create(
    #                     created_by=request.user.id,
    #                     created_date=timezone.now(),
    #                     salesman=item.van.salesman,
    #                     van=item.van,
    #                     product=item.product,
    #                     scrap_count=scrap_count,
    #                     washing_count=washing_count,
    #                     other_quantity=other_quantity,
    #                     other_reason=other_reason,
    #                 )

    #                 if scrap_count > 0:
    #                     scrap_instance, created = ScrapProductStock.objects.get_or_create(
    #                         created_date__date=timezone.now().date(), product=item.product,
    #                         defaults={'created_by': request.user.id, 'created_date': timezone.now(), 'quantity': scrap_count}
    #                     )
    #                     if not created:
    #                         scrap_instance.quantity += scrap_count
    #                         scrap_instance.save()

    #                 if washing_count > 0:
    #                     washing_instance, created = WashingProductStock.objects.get_or_create(
    #                         created_date__date=timezone.now().date(), product=item.product,
    #                         defaults={'created_by': request.user.id, 'created_date': timezone.now(), 'quantity': washing_count}
    #                     )
    #                     if not created:
    #                         washing_instance.quantity += washing_count
    #                         washing_instance.save()

    #                 count = scrap_count + washing_count
    #                 item.return_count -= int(count)
    #                 item.save()

    #             else:
    #                 item.stock -= int(count)
    #                 item.save()

    #                 product_stock = ProductStock.objects.get(branch=item.van.branch_id, product_name=item.product)
    #                 product_stock.quantity += int(count)
    #                 product_stock.save()

    #             Offload.objects.create(
    #                 created_by=request.user.id,
    #                 created_date=timezone.now(),
    #                 salesman=item.van.salesman,
    #                 van=item.van,
    #                 product=item.product,
    #                 quantity=int(count),
    #                 stock_type=stock_type
    #             )

    #             response_data = {
    #                 "status": "true",
    #                 "title": "Successfully Offloaded",
    #                 "message": "Offload successfully.",
    #                 'reload': 'true',
    #             }

    #             return Response(response_data, status=status.HTTP_200_OK)

    #     except IntegrityError as e:
    #         response_data = {
    #             "status": "false",
    #             "title": "Failed",
    #             "message": str(e),
    #         }
    #         return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    #     except Exception as e:
    #         response_data = {
    #             "status": "false",
    #             "title": "Failed",
    #             "message": str(e),
    #         }
    #         return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class GetVanCouponBookNoAPIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        coupon_type = request.GET.get("productName")
        
        instances = VanCouponStock.objects.filter(
            coupon__coupon_type__coupon_type_name=coupon_type,
            stock__gt=0
        )

        if instances.exists():
            instance = instances.values_list('coupon__pk', flat=True)
            stock_instances = CouponStock.objects.filter(couponbook__pk__in=instance)
            serialized = CouponStockSerializer(stock_instances, many=True)
            
            response_data = {
                "status": "true",
                "data": serialized.data,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        else:
            response_data = {
                "status": "false",
                "title": "Failed",
                "message": "item not found",
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        
class EditCouponAPIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, van_pk):
        book_numbers = request.data.get("coupon_book_no", [])
        
        if not book_numbers:
            return Response({
                "status": "false",
                "title": "Failed",
                "message": "No coupon book numbers provided.",
            }, status=status.HTTP_400_BAD_REQUEST)

        for book_number in book_numbers:
            try:
                coupon_instance = NewCoupon.objects.get(book_num=book_number)
                van_coupon_stock = VanCouponStock.objects.get(van__pk=van_pk, coupon=coupon_instance)
                van_coupon_stock.stock -= 1
                van_coupon_stock.save()

                product_stock = ProductStock.objects.get(
                    branch=van_coupon_stock.van.branch_id,
                    product_name__product_name=coupon_instance.coupon_type.coupon_type_name
                )
                product_stock.quantity += 1
                product_stock.save()

                coupon = CouponStock.objects.get(couponbook=coupon_instance)
                coupon.coupon_stock = "company"
                coupon.save()

                OffloadCoupon.objects.create(
                    created_by=request.user.id,
                    created_date=timezone.now(),
                    salesman=van_coupon_stock.van.salesman,
                    van=van_coupon_stock.van,
                    coupon=van_coupon_stock.coupon,
                    quantity=1,
                    stock_type="stock"
                )

            except NewCoupon.DoesNotExist:
                return Response({
                    "status": "false",
                    "title": "Failed",
                    "message": f"Coupon with book number {book_number} does not exist.",
                }, status=status.HTTP_404_NOT_FOUND)
            except VanCouponStock.DoesNotExist:
                return Response({
                    "status": "false",
                    "title": "Failed",
                    "message": f"Van coupon stock for book number {book_number} does not exist.",
                }, status=status.HTTP_404_NOT_FOUND)
            except ProductStock.DoesNotExist:
                return Response({
                    "status": "false",
                    "title": "Failed",
                    "message": f"Product stock for coupon type {coupon_instance.coupon_type.coupon_type_name} does not exist.",
                }, status=status.HTTP_404_NOT_FOUND)
            except CouponStock.DoesNotExist:
                return Response({
                    "status": "false",
                    "title": "Failed",
                    "message": f"Coupon stock for book number {book_number} does not exist.",
                }, status=status.HTTP_404_NOT_FOUND)
        
        response_data = {
            "status": "true",
            "title": "Successfully Created",
            "message": "Coupon Offload successfully.",
            'reload': 'true',
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
  
    
#-----------------------------end offload--------------------------------    


class CouponsProductsAPIView(APIView):
    def get(self, request):
        coupons_category = 'Coupons'
        products = ProdutItemMaster.objects.filter(category__category_name=coupons_category)
        serializer = CouponsProductsSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class Get_Notification_APIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
  
    def get(self, request, *args, **kwargs):
        try:
          
            user_id=request.user.id
            noti_obj=Notification.objects.filter(user=user_id)
            
            serializer=Customer_Notification_serializer(noti_obj,many=True)
         
            return Response(
                {'status': True, 'data': serializer.data, 'message': 'Successfully Passed Data!'})
        except Exception as e:
            return Response({"status": False, "data": str(e), "message": "Something went wrong!"})
        



        
        

#---------------store app Offload API---------------------------------- 

class OffloadRequestVanListAPIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            offload_requests = OffloadRequest.objects.select_related('van', 'van__salesman').filter(status=False)
            
            unique_vans = set()
            data = []
            for request in offload_requests:
                van = request.van
                
                if van and van.van_id not in unique_vans:
                    van_data = {
                        'id': van.van_id,
                        'request_id': request.id,
                        'date': datetime.today().date(),
                        'van_plate': van.plate,
                        'salesman_id': van.salesman.id if van.salesman else None,
                        'salesman_name': van.salesman.get_fullname() if van.salesman else None,
                        'route_name': self.get_van_route(van),
                    }
                    data.append(van_data)
                    unique_vans.add(van.van_id)
            
            return Response(data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_van_route(self, van):
        try:
            return van.get_van_route()
        except AttributeError:
            return None
      
class OffloadRequestListAPIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
 
    def get(self, request,van_id):
        date_str = request.GET.get("date_str", str(datetime.today().date()))
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        offload_requests = OffloadRequest.objects.filter(van__van_id=van_id,date=date,status=False)
        response_data = {
            "status": True,
            "vans": []
        }

        for offload_request in offload_requests:
            van_data = {
                "van": str(offload_request.van.pk),
                "request_id": str(offload_request.id),
                "products": []
            }

            items = OffloadRequestItems.objects.filter(offload_request=offload_request)
            for item in items:
                product = item.product
                product_name = product.product_name
                if item.stock_type == 'emptycan':
                    product_name = f"{product.product_name} (Empty Can)"
                elif item.stock_type == 'return':
                    product_name = f"{product.product_name} (Return Can)"
                    
                product_data = {
                    "product_id": str(product.id),
                    "product_name": product_name,
                    "quantity": item.quantity,
                    "stock_type": item.stock_type,
                }

                if item.stock_type == 'return':
                    return_stocks = OffloadRequestReturnStocks.objects.filter(offload_request_item=item).first()
                    if return_stocks:
                        product_data.update({
                            "scrap_count": return_stocks.scrap_count,
                            "washing_count": return_stocks.washing_count,
                            "other_reason": return_stocks.other_reason,
                            "other_quantity": return_stocks.other_quantity,
                        })
                if item.stock_type == 'stock' and product.category.category_name.lower() == "coupons":
                    coupons = OffloadRequestCoupon.objects.filter(offload_request=offload_request)
                    product_data["coupons"] = [
                        {
                            "coupon_id": str(coupon.coupon.id),
                            "book_num": coupon.coupon.book_num
                        }
                        for coupon in coupons
                    ]

                van_data["products"].append(product_data)

            response_data["vans"].append(van_data)

        return Response(response_data, status=status.HTTP_200_OK)
        
    def post(self, request):
        try:
            request_id = request.data.get('request_id')
            van_id = request.data.get('van_id')
            products = request.data.get('products', [])
            date_str=request.data.get('date_str')
            
            with transaction.atomic():
                offload_request_instance = OffloadRequest.objects.get(pk=request_id)
                if van_id:
                    van_id = offload_request_instance.van.pk
                van_instance = Van.objects.get(pk=van_id)
                
                for product_data in products:
                    product_id = product_data.get('product_id')
                    count = int(product_data.get('count', 0))
                    stock_type = product_data.get('stock_type')
                    
                    product_item_instance = ProdutItemMaster.objects.get(pk=product_id)
                    van_product_stock_instance = VanProductStock.objects.get(created_date=datetime.today().date(),product=product_item_instance,van=van_instance)
                    
                    if count > 0:
                        if product_item_instance.category.category_name != "Coupons":
                            if product_item_instance.product_name == "5 Gallon" and stock_type == "stock":
                                # print("stock")
                                van_product_stock_instance.stock -= int(count)
                                van_product_stock_instance.save()
                                
                                if (product_stock:=ProductStock.objects.filter(branch=van_instance.branch_id,product_name=product_item_instance)).exists():
                                    product_stock = ProductStock.objects.get(branch=van_instance.branch_id,product_name=product_item_instance)
                                    product_stock.quantity += int(count)
                                    product_stock.save()
                                else:
                                    product_stock = ProductStock.objects.create(
                                        branch=van_instance.branch_id,
                                        product_name=product_item_instance,
                                        quantity=int(count)
                                    )
                            elif product_item_instance.product_name == "5 Gallon" and stock_type == "emptycan":
                                # print("empty")
                                van_product_stock_instance.empty_can_count -= int(count)
                                van_product_stock_instance.save()
                                
                                emptycan=EmptyCanStock.objects.create(
                                    product=product_item_instance,
                                    quantity=int(count)
                                )
                                emptycan.save()
                                
                            elif product_item_instance.product_name == "5 Gallon" and stock_type == "return":
                                # print("return")
                                scrap_count = int(request.POST.get('scrap_count'))
                                washing_count = int(request.POST.get('washing_count'))
                                
                                # print(scrap_count)
                                # print(washing_count)
                                
                                OffloadReturnStocks.objects.create(
                                    created_by=request.user.id,
                                    created_date=datetime.today(),
                                    salesman=van_instance.salesman,
                                    van=van_instance,
                                    product=product_item_instance,
                                    scrap_count=scrap_count,
                                    washing_count=washing_count
                                )
                                
                                if scrap_count > 0 :
                                    if not ScrapProductStock.objects.filter(created_date__date=datetime.today().date(),product=product_item_instance).exists():
                                        scrap_instance=ScrapProductStock.objects.create(created_by=request.user.id,created_date=datetime.today(),product=product_item_instance)
                                    else:
                                        scrap_instance=ScrapProductStock.objects.get(created_date__date=datetime.today().date(),product=product_item_instance)
                                    scrap_instance.quantity = scrap_count
                                    scrap_instance.save()
                                
                                if washing_count > 0 :
                                    if not WashingProductStock.objects.filter(created_date__date=datetime.today().date(),product=product_item_instance).exists():
                                        washing_instance=WashingProductStock.objects.create(created_by=request.user.id,created_date=datetime.today(),product=product_item_instance)
                                    else:
                                        washing_instance=WashingProductStock.objects.get(created_date__date=datetime.today().date(),product=product_item_instance)
                                    washing_instance.quantity = washing_count
                                    washing_instance.save()
                                    
                                count = scrap_count + washing_count
                                # print(count)
                                van_product_stock_instance.return_count -= int(count)
                                van_product_stock_instance.save()
                                
                            else : 
                                # print("else")
                                van_product_stock_instance.stock -= int(count)
                                van_product_stock_instance.save()
                                
                                product_stock = ProductStock.objects.get(branch=van_instance.branch_id,product_name=product_item_instance)
                                product_stock.quantity += int(count)
                                product_stock.save()
                            
                            Offload.objects.create(
                                created_by=request.user.id,
                                created_date=datetime.today(),
                                salesman=van_instance.salesman,
                                van=van_instance,
                                product=product_item_instance,
                                quantity=int(count),
                                stock_type=stock_type,
                                offloaded_date=date_str,
                            )
                            
                            offload_items = OffloadRequestItems.objects.filter(offload_request=offload_request_instance,product=product_item_instance,stock_type=stock_type)
                            for offload_item in offload_items:
                                offload_item.offloaded_quantity = count
                                offload_item.save()
                            
                        elif product_item_instance.category.category_name == "Coupons":
                            coupons = product_data.get('coupons', [])
                            
                            for book_number in coupons:
                                coupon_instance = NewCoupon.objects.get(book_num=book_number)
                                
                                van_coupon_stock = VanCouponStock.objects.get(van=van_instance,coupon=coupon_instance)
                                van_coupon_stock.stock -= 1
                                van_coupon_stock.save()
                                
                                if (product_stock:=ProductStock.objects.filter(branch=van_instance.branch_id,product_name=product_item_instance)).exists():
                                    product_stock = ProductStock.objects.get(branch=van_instance.branch_id,product_name=product_item_instance)
                                    product_stock.quantity += 1
                                    product_stock.save()
                                else:
                                    product_stock = ProductStock.objects.create(
                                        branch=van_instance.branch_id,
                                        product_name=product_item_instance,
                                        quantity=1
                                    )
                                
                                coupon = CouponStock.objects.get(couponbook=coupon_instance)
                                coupon.coupon_stock = "company"
                                coupon.save()
                                
                                offload_item = OffloadRequestItems.objects.get(offload_request=offload_request_instance,product=product_item_instance,stock_type=stock_type)
                                offload_item.offloaded_quantity = len(coupons)
                                offload_item.save()
                                
                                OffloadCoupon.objects.create(
                                    coupon=van_coupon_stock.coupon,
                                    quantity = 1,
                                    stock_type="stock",
                                    offload_request=offload_request_instance
                                )
                                
                        offload_request_instance.status = True
                        offload_request_instance.save()
                                
                        response_data = {
                            "status": "true",
                            "title": "Successfully Offloaded",
                            "message": "Offload successfully.",
                            'reload': 'true',
                        }
                        return Response(response_data, status=status.HTTP_200_OK)
                    
        except IntegrityError as e:
            response_data = {
                "status": "false",
                "title": "Failed",
                "message": str(e),
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            response_data = {
                "status": "false",
                "title": "Failed",
                "message": str(e),
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
#------------------------------------Store Appp Orders Api-----------------------------------------------------

class StaffIssueOrdersListAPIView(APIView):
    def get(self, request):
        query = request.data.get("q")
        datefilter = request.data.get("date")
        print("datefilter", datefilter)

        instances = Staff_Orders.objects.all().order_by('-created_date')

        if query:
            instances = instances.filter(order_number__icontains=query)

        if datefilter:
            date = datetime.strptime(datefilter, "%Y-%m-%d").date()
            instances = instances.filter(order_date=date)
        else:
            instances = instances.filter(order_date=timezone.now().date())

        serializer = StaffOrdersSerializer(instances, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StaffIssueOrdersAPIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, staff_order_id):
        order = get_object_or_404(Staff_Orders, pk=staff_order_id)
        staff_orders_details = Staff_Orders_details.objects.filter(staff_order_id=order).order_by('-created_date')
        
        serialized_data = StaffOrdersDetailsSerializer(staff_orders_details, many=True).data
        response_data = {
            'staff_orders_details': serialized_data,
            'order_date': order.order_date,
            'order_number': order.order_number
        }
        
        return Response(response_data, status=status.HTTP_200_OK)

    @transaction.atomic
    def post(self, request, staff_order_id):
        def convert_to_uuid(value):
            try:
                # Attempt to convert the value to UUID
                return UUID(value)
            except (TypeError, ValueError, AttributeError):
                raise ValidationError(f'{value} is not a valid UUID.')

        order = get_object_or_404(Staff_Orders, pk=staff_order_id)
        staff_orders_details_data = request.data.get('staff_orders_details')

        if not staff_orders_details_data:
            return Response({'error': 'No data provided'}, status=status.HTTP_400_BAD_REQUEST)

        response_data = {}

        for detail_data in staff_orders_details_data:
            staff_order_details_id = detail_data.get('staff_order_details_id')
            product_id = detail_data.get('product_id')
            count = int(detail_data.get('count', 0))
            used_stock = int(detail_data.get('used_stock', 0))
            new_stock = int(detail_data.get('new_stock', 0))

            try:
                product_id = convert_to_uuid(product_id)
            except ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

            issue = get_object_or_404(Staff_Orders_details, staff_order_details_id=staff_order_details_id, product_id=product_id)
            van = get_object_or_404(Van, salesman_id__id=order.created_by)
            
            if count > 0:
                if issue.product_id.category.category_name == "Coupons":
                    book_numbers = detail_data.get('coupon_book_no')
                    for book_no in book_numbers:
                        coupon = get_object_or_404(NewCoupon, book_num=book_no, coupon_type__coupon_type_name=issue.product_id.product_name)
                        update_purchase_stock = ProductStock.objects.filter(product_name=issue.product_id)
                        
                        if update_purchase_stock.exists():
                            product_stock_quantity = update_purchase_stock.first().quantity or 0
                        else:
                            product_stock_quantity = 0

                        try:
                            with transaction.atomic():
                                issue_order = Staff_IssueOrders.objects.create(
                                    created_by=str(request.user.id),
                                    modified_by=str(request.user.id),
                                    modified_date=datetime.now(),
                                    product_id=issue.product_id,
                                    staff_Orders_details_id=issue,
                                    coupon_book=coupon,
                                    quantity_issued=1
                                )

                                update_purchase_stock = update_purchase_stock.first()
                                update_purchase_stock.quantity -= 1
                                update_purchase_stock.save()

                                if (update_van_stock := VanCouponStock.objects.filter(created_date=datetime.today().date(), van=van, coupon=coupon)).exists():
                                    van_stock = update_van_stock.first()
                                    van_stock.stock += 1
                                    van_stock.save()
                                else:
                                    vanstock = VanStock.objects.create(
                                        created_by=str(request.user.id),
                                        created_date=datetime.now(),
                                        stock_type='opening_stock',
                                        van=van
                                    )

                                    VanCouponItems.objects.create(
                                        coupon=coupon,
                                        book_no=book_no,
                                        coupon_type=coupon.coupon_type,
                                        van_stock=vanstock,
                                    )

                                    van_stock = VanCouponStock.objects.create(
                                        created_date=datetime.now().date(),
                                        coupon=coupon,
                                        stock=1,
                                        van=van
                                    )

                                    issue.issued_qty += 1
                                    issue.save()

                                    CouponStock.objects.filter(couponbook=coupon).update(coupon_stock="van")
                                    
                                    status_code = status.HTTP_200_OK
                                    response_data = {
                                        "status": "true",
                                        "title": "Successfully Created",
                                        "message": "Coupon Issued successfully.",
                                        'redirect': 'true',
                                    }

                        except IntegrityError as e:
                            status_code = status.HTTP_400_BAD_REQUEST
                            response_data = {
                                "status": "false",
                                "title": "Failed",
                                "message": str(e),
                            }

                        except Exception as e:
                            status_code = status.HTTP_400_BAD_REQUEST
                            response_data = {
                                "status": "false",
                                "title": "Failed",
                                "message": str(e),
                            }

                else:
                    quantity_issued = count

                    # Get the van's current stock of the product
                    vanstock_count = VanProductStock.objects.filter(created_date=issue.staff_order_id.order_date, van=van, product=issue.product_id).aggregate(sum=Sum('stock'))['sum'] or 0

                    # Check van limit for 5 Gallon product
                    if issue.product_id.product_name == "5 Gallon":
                        if int(quantity_issued) != 0 and van.bottle_count > int(quantity_issued) + vanstock_count:
                            van_limit = True
                        else:
                            van_limit = False
                    else:
                        van_limit = True

                    if van_limit:
                        try:
                            with transaction.atomic():
                                product_stock = get_object_or_404(ProductStock, product_name=issue.product_id,branch=van.branch_id)
                                stock_quantity = issue.count

                                if 0 < int(quantity_issued) <= int(product_stock.quantity):
                                    issue_order = Staff_IssueOrders.objects.create(
                                        created_by=str(request.user.id),
                                        modified_by=str(request.user.id),
                                        modified_date=datetime.now(),
                                        product_id=issue.product_id,
                                        staff_Orders_details_id=issue,
                                        quantity_issued=quantity_issued,
                                        van=van,
                                        stock_quantity=stock_quantity
                                    )

                                    product_stock.quantity -= int(quantity_issued)
                                    product_stock.save()

                                    vanstock = VanStock.objects.create(
                                        created_by=request.user.id,
                                        created_date=datetime.now(),
                                        modified_by=request.user.id,
                                        modified_date=datetime.now(),
                                        stock_type='opening_stock',
                                        van=van
                                    )

                                    VanProductItems.objects.create(
                                        product=issue.product_id,
                                        count=int(quantity_issued),
                                        van_stock=vanstock,
                                    )

                                    if VanProductStock.objects.filter(created_date=datetime.today().date(), product=issue.product_id, van=van).exists():
                                        van_product_stock = VanProductStock.objects.get(created_date=datetime.today().date(), product=issue.product_id, van=van)
                                    else:
                                        van_product_stock = VanProductStock.objects.create(
                                            created_date=datetime.now().date(),
                                            product=issue.product_id,
                                            van=van,
                                            stock=int(quantity_issued))

                                    if issue.product_id.product_name == "5 Gallon":
                                        if (bottle_count:=BottleCount.objects.filter(van=van_product_stock.van,created_date__date=van_product_stock.created_date)).exists():
                                            bottle_count = bottle_count.first()
                                        else:
                                            bottle_count = BottleCount.objects.create(van=van_product_stock.van,created_date=van_product_stock.created_date)
                                        bottle_count.opening_stock += van_product_stock.stock
                                        bottle_count.save()

                                    issue.issued_qty += int(quantity_issued)
                                    issue.save()
                                    
                                    status_code = status.HTTP_200_OK
                                    response_data = {
                                        "status": "true",
                                        "title": "Successfully Created",
                                        "message": "Product issued successfully.",
                                        'redirect': 'true',
                                    }
                                else:
                                    status_code = status.HTTP_400_BAD_REQUEST
                                    response_data = {
                                        "status": "false",
                                        "title": "Failed",
                                        "message": f"No stock available in {product_stock.product_name}, only {product_stock.quantity} left",
                                    }
                                if used_stock > 0:
                                    WashedUsedProduct.objects.create(
                                        product=issue.product_id,
                                        quantity=used_stock
                                    )

                                    # Deduct from ProductStock
                                    product_stock = ProductStock.objects.filter(product_name=issue.product_id).first()
                                    if product_stock and product_stock.quantity >= used_stock:
                                        product_stock.quantity -= used_stock
                                        product_stock.save()
                                    else:
                                        return Response(
                                            {
                                                "status": "false",
                                                "title": "Failed",
                                                "message": f"Insufficient stock for {product_stock.product_name}. Only {product_stock.quantity} available.",
                                            },
                                            status=status.HTTP_400_BAD_REQUEST
                                        )

                                    response_data["used_stock"] = f"{used_stock} units recorded as used stock successfully."

                                # Handle new stock
                                if new_stock > 0:
                                    product_stock = ProductStock.objects.filter(product_name=issue.product_id).first()
                                    
                                    # If ProductStock exists, increase the quantity
                                    if product_stock:
                                        product_stock.quantity += new_stock
                                        product_stock.save()
                                    else:
                                        # Create a new ProductStock record if none exists
                                        ProductStock.objects.create(
                                            product_name=issue.product_id,
                                            quantity=new_stock,
                                            branch=van.branch_id,
                                            created_by=request.user.id
                                        )

                                    response_data["new_stock"] = f"{new_stock} units added to new stock successfully."

                        

                        except Exception as e:
                            status_code = status.HTTP_400_BAD_REQUEST
                            response_data = {
                                "status": "false",
                                "title": "Failed",
                                "message": str(e),
                            }

                    else:
                        status_code = status.HTTP_400_BAD_REQUEST
                        response_data = {
                            "status": "false",
                            "title": "Failed",
                            "message": f"Over Load! currently {vanstock_count} Can Loaded, Max 5 Gallon Limit is {van.bottle_count}",
                        }

        return Response(response_data, status=status_code)

class GetCouponBookNoView(APIView):
    def get(self, request, *args, **kwargs):
        request_id = request.GET.get("request_id")
        # print("request_id",request_id)
        
        instance = get_object_or_404(Staff_Orders_details, pk=request_id)
        stock_instances = CouponStock.objects.filter(
            couponbook__coupon_type__coupon_type_name=instance.product_id.product_name,
            coupon_stock="company"
        )
        serialized = IssueCouponStockSerializer(stock_instances, many=True)
        
        response_data = {
            "status": "true",
            "data": serialized.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)
    
#------------------------------Store Appp Api Comppletes-------------------------------------------------


#------------------------------------Location Api -----------------------------------------------------

class LocationUpdateAPIView(APIView):
    def get(self, request, *args, **kwargs):
        location_updates = LocationUpdate.objects.all()
        serializer = LocationUpdateSerializer(location_updates, many=True)
        return Response({
            "message": "Location updates retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = LocationUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Location update created successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "message": "Failed to create location update.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
#------------------------------------Van Stock Api -----------------------------------------------------
        
class VanListView(APIView):

    def get(self, request):
        vans = Van.objects.all()
        serializer = VanListSerializer(vans, many=True)
        return Response(serializer.data)
    

class VanDetailView(APIView):

    def get(self, request, van_id):
        date = request.GET.get('date')
        if date:
            date = datetime.strptime(date, '%Y-%m-%d').date()
        else:
            date = datetime.today().date()

        van_product_stock = VanProductStock.objects.filter(van__pk=van_id,created_date=date,stock__gt=0)
        van_coupon_stock = VanCouponStock.objects.filter(van__pk=van_id,created_date=date,stock__gt=0)

        coupon_serialized_data = VanCouponStockSerializer(van_coupon_stock, many=True).data

        product_serialized_data = []
        for stock in van_product_stock:
            product_name = stock.product.product_name.lower()
            if product_name == "5 gallon":
                product_serialized_data.append({
                    'id': stock.pk,
                    'product_name': stock.product.product_name,
                    'stock_type': 'stock',
                    'count': stock.stock,
                    'product': stock.product.pk,
                    'van': stock.van.pk
                })
                product_serialized_data.append({
                    'id': stock.pk,
                    'product_name': f"{stock.product.product_name} (empty can)" ,
                    'stock_type': 'empty_bottle',
                    'count': stock.empty_can_count,
                    'product': stock.product.pk,
                    'van': stock.van.pk
                })
            else:
                product_serialized_data.append({
                    'id': stock.pk,
                    'product_name': stock.product.product_name,
                    'stock_type': 'stock',
                    'count': stock.stock,
                    'product': stock.product.pk,
                    'van': stock.van.pk
                })

        return Response(
            {
                "coupon_stock": coupon_serialized_data,
                "product_stock": product_serialized_data,
            })
        
        
#-----------------store app productstock---------------
class ProductStockListAPIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        branch_id = request.query_params.get('branch_id')
        if branch_id:
            product_stocks = ProductStock.objects.filter(branch__branch_id=branch_id).order_by('-created_date')
        else:
            product_stocks = ProductStock.objects.all().order_by('-created_date')
        serializer = ProductStockSerializer(product_stocks, many=True)
        return Response(serializer.data)
    # def get(self, request):
    #     # Get the authenticated user
    #     user = request.user
        
    #     # Check if the user is a supervisor
    #     if user.user_type == 'Supervisor':
    #         # Get the branch associated with the supervisor
    #         branch = user.branch_id
    #         # Filter product stocks by the supervisor's branch
    #         product_stocks = ProductStock.objects.filter(branch=branch).order_by('-created_date')
    #     else:
    #         return Response({"detail": "User is not a supervisor."}, status=403)

    #     serializer = ProductStockSerializer(product_stocks, many=True)
    #     return Response(serializer.data)
    
class CashSalesReportAPIView(APIView):
    def get(self, request):
        filter_data = {}
        data_filter = False
        salesman_id =  ""
        date_str = request.GET.get('date')
        route_name = request.GET.get('route_name')

        if date_str:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            date = datetime.today().date()
    
        if route_name:
            data_filter = True
            
            van_route = Van_Routes.objects.filter(routes__route_name=route_name).first()
            salesman = van_route.van.salesman
            salesman_id = salesman.pk
            filter_data['route_name'] = route_name
        
            cash_sales = CustomerSupply.objects.filter(created_date__date=date,salesman=salesman, amount_recieved__gt=0).exclude(customer__sales_type="CASH COUPON")
            recharge_cash_sales = CustomerCoupon.objects.filter(created_date__date=date, amount_recieved__gt=0)

            cash_total_net_taxable = cash_sales.aggregate(total_net_taxable=Sum('net_payable'))['total_net_taxable'] or 0
            cash_total_vat = cash_sales.aggregate(total_vat=Sum('vat'))['total_vat'] or 0
            cash_total_subtotal = cash_sales.aggregate(total_subtotal=Sum('subtotal'))['total_subtotal'] or 0
            cash_total_amount_recieved = cash_sales.aggregate(total_amount_recieved=Sum('amount_recieved'))['total_amount_recieved'] or 0
            cash_total_quantity = cash_sales.aggregate(total_quantity=Sum('customersupplyitems__quantity'))['total_quantity'] or 0

            cash_sales_serializer = CustomersSupplySerializer(cash_sales, many=True)
            recharge_cash_sales_serializer = CustomersCouponSerializer(recharge_cash_sales, many=True)
            cash_sale_recharge_count = recharge_cash_sales.count()
            cash_total_qty = cash_total_quantity + cash_sale_recharge_count
            data = {
                'cash_sales': cash_sales_serializer.data,
                'recharge_cash_sales': recharge_cash_sales_serializer.data,
                'cash_total_net_taxable': cash_total_net_taxable,
                'cash_total_vat': cash_total_vat,
                'cash_total_subtotal': cash_total_subtotal,
                'cash_total_amount_recieved': cash_total_amount_recieved,
                'cash_total_quantity': cash_total_qty,
            }

            return Response(data, status=status.HTTP_200_OK) 
           

class CreditSalesReportAPIView(APIView):
    def get(self, request):
        filter_data = {}
        data_filter = False
        salesman_id =  ""
        date_str = request.GET.get('date')
        if request.GET.get('route_name'):
            route_name = request.GET.get('route_name')
        else:
            route_name = request.data.get('route_name')

        if date_str:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            date = datetime.today().date()
    
        if route_name:
            data_filter = True
            
            van_route = Van_Routes.objects.filter(routes__route_name=route_name).first()
            salesman = van_route.van.salesman
            salesman_id = salesman.pk
            filter_data['route_name'] = route_name
        
            
            credit_sales = CustomerSupply.objects.filter(created_date__date=date,salesman=salesman,amount_recieved__lte=0).exclude(customer__sales_type__in=["FOC","CASH COUPON"])

            credit_total_net_taxable = credit_sales.aggregate(total_net_taxable=Sum('net_payable'))['total_net_taxable'] or 0
            credit_total_vat = credit_sales.aggregate(total_vat=Sum('vat'))['total_vat'] or 0
            credit_total_subtotal = credit_sales.aggregate(total_subtotal=Sum('subtotal'))['total_subtotal'] or 0
            credit_total_received = credit_sales.aggregate(total_amount_recieved=Sum('amount_recieved'))['total_amount_recieved'] or 0
            credit_total_quantity = credit_sales.aggregate(total_quantity=Sum('customersupplyitems__quantity'))['total_quantity'] or 0
            
            recharge_credit_sales = CustomerCoupon.objects.filter(created_date__date=date,amount_recieved__lte=0)
            credit_sale_recharge_net_payeble = recharge_credit_sales.aggregate(total_net_amount=Sum('net_amount'))['total_net_amount'] or 0
            credit_sale_recharge_vat_total = 0
            
            credit_sale_recharge_grand_total = recharge_credit_sales.aggregate(total_grand_total=Sum('grand_total'))['total_grand_total'] or 0
            credit_sale_recharge_amount_recieved = recharge_credit_sales.aggregate(total_amount_recieved=Sum('amount_recieved'))['total_amount_recieved'] or 0
            credit_total_net_taxable = credit_total_net_taxable + credit_sale_recharge_net_payeble 
            credit_total_vat = credit_total_vat + credit_sale_recharge_vat_total 
            credit_total_subtotal = credit_total_subtotal + credit_sale_recharge_grand_total
            credit_total_amount_recieved = credit_total_received + credit_sale_recharge_amount_recieved
            
            total_credit_sales_count = credit_sales.count() + recharge_credit_sales.count()
            credit_sale_recharge_count = recharge_credit_sales.count()
            credit_total_qty = credit_total_quantity + credit_sale_recharge_count
            
            # Serializing the data
            credit_sales_serializer = CustomersSupplySerializer(credit_sales, many=True)

            data = {
                'credit_sales': credit_sales_serializer.data,
                'credit_total_net_taxable': credit_total_net_taxable,
                'credit_total_vat': credit_total_vat,
                'credit_total_subtotal': credit_total_subtotal,
                'credit_total_received': credit_total_received,
                'credit_total_qty':credit_total_qty,
            }

            return Response(data, status=status.HTTP_200_OK)
        
#---------------------------Bottle Count API ------------------------------------------------   

class VanRouteBottleCountView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        filter_data = {}
        date_str = request.GET.get("filter_date")
        selected_route = request.GET.get('route_name', '')
        
        if date_str:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            date = datetime.today().date()
        
        filter_data["filter_date"] = date
        
        instances = BottleCount.objects.filter(created_date__date=date)
        
        if selected_route:
            van_ids = Van_Routes.objects.filter(routes__route_name=selected_route).values_list("van__pk")
            instances = instances.filter(van__pk__in=van_ids)
            filter_data["selected_route"] = selected_route
        
        serializer = BottleCountSerializer(instances, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = BottleCountSerializer(data=request.data)
        if serializer.is_valid():
            route_name = request.data.get('route_name')
            filter_date_str = request.data.get('filter_date')
            
            if filter_date_str:
                filter_date = datetime.strptime(filter_date_str, '%Y-%m-%d').date()
            else:
                filter_date = datetime.today().date()
            
            van_ids = Van_Routes.objects.filter(routes__route_name=route_name).values_list("van__pk")
            instances = BottleCount.objects.filter(created_date__date=filter_date, van__pk__in=van_ids)
            
            serializer = BottleCountSerializer(instances, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VansRouteBottleCountAddAPIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        instance = get_object_or_404(BottleCount, pk=pk)
        serializer = BottleCountAddSerializer(instance, data=request.data, partial=True)
        
        if serializer.is_valid():
            bottle_count = serializer.save()
            bottle_count.van = instance.van  # Ensure van is correctly assigned
            bottle_count.created_by = request.user.username  # Assuming you have user authentication
            bottle_count.save()
            return Response({"message": "Bottle count updated successfully"}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
     
class VansRouteBottleCountDeductAPIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request, pk):
        instance = get_object_or_404(BottleCount, pk=pk)
        serializer = BottleCountDeductSerializer(instance, data=request.data)
        if serializer.is_valid():
            instance.qty_deducted = serializer.validated_data['qty_deducted']
            instance.modified_by = request.user.username  # Assuming you have user authentication
            instance.save()
            return Response({"message": "Bottle count deducted successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StockTransferAPIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        product_id = request.data.get('product_id')

        if not product_id:
            return Response({"error": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            washing_stock = WashingStock.objects.get(product__pk=product_id)
            bottle_count = washing_stock.quantity
        except WashingStock.DoesNotExist:
            bottle_count = 0

        return Response({"bottle_count": bottle_count}, status=status.HTTP_200_OK)
    
    
    def post(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        used_quantity = request.data.get('used_quantity')
        damage_quantity = request.data.get('damage_quantity')

        if not product_id:
            return Response({"error": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            with transaction.atomic():
                product_item = ProdutItemMaster.objects.get(pk=product_id)
                
                if used_quantity > 0 :
                    WashedProductTransfer.objects.create(
                        product=product_item,
                        quantity=used_quantity,
                        status="used",
                        created_by=request.user.pk,
                        created_date=datetime.today(),
                    )
                    
                    used_product = WashedUsedProduct.objects.get_or_create(product = product_item)
                    used_product.quantity += used_quantity
                    used_product.save()
                    
                    washing_stock = WashingStock.objects.get(product = product_item)
                    washing_stock.quantity -= used_quantity
                    washing_stock.save()
                    
                if damage_quantity > 0 :
                    WashedProductTransfer.objects.create(
                        product=product_item,
                        quantity=damage_quantity,
                        status="scrap",
                        created_by=request.user.pk,
                        created_date=datetime.today(),
                    )
                    
                    ScrapProductStock.objects.create(
                        product=product_item,
                        quantity=damage_quantity,
                        created_by=request.user.pk,
                        created_date=datetime.today(),
                    )
                    
                    scrap_product = ScrapStock.objects.get_or_create(product = product_item)
                    scrap_product.quantity += damage_quantity
                    scrap_product.save()
                    
                    washing_stock = WashingStock.objects.get(product = product_item)
                    washing_stock.quantity -= damage_quantity
                    washing_stock.save()
                    
                    status_code = status.HTTP_200_OK
                    response_data = {
                        "status": "true",
                        "title": "Success",
                        "message": "Stock Transfer successfully Completed",
                    }
                    
        except IntegrityError as e:
            status_code = status.HTTP_400_BAD_REQUEST
            response_data = {
                "status": "false",
                "title": "Failed",
                "message": str(e),
            }

        except Exception as e:
            status_code = status.HTTP_400_BAD_REQUEST
            response_data = {
                "status": "false",
                "title": "Failed",
                "message": str(e),
            }
        return Response(response_data, status=status_code)

class ScrapStockAPIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        
        if request.data.get('product_id'):
            product_id = request.data.get('product_id')
        else:
            product_id = ProdutItemMaster.objects.get(product_name="5 Gallon").pk

        if not product_id:
            return Response({"error": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            scrap_stocks = ScrapStock.objects.filter(product__pk=product_id)
            total_quantity = scrap_stocks.aggregate(total_quantity=Sum('quantity'))['total_quantity']
        except ScrapStock.DoesNotExist:
            total_quantity = 0
        
        return Response({"total_quantity": total_quantity}, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        cleared_quantity = request.data.get('cleared_quantity')

        # if not product_id:
        #     return Response({"error": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                if product_id:
                    product_item = ProdutItemMaster.objects.get(pk=product_id)
                else:
                    product_item = ProdutItemMaster.objects.get(product_name="5 Gallon")
                
                ScrapcleanedStock.objects.create(
                        product=product_item,
                        quantity=cleared_quantity,
                        created_by=request.user.pk,
                        created_date=datetime.today(),
                    )
                
                # Create or update ScrapStock
                scrap_stock = ScrapStock.objects.get(product=product_item)
                scrap_stock.quantity -= cleared_quantity
                scrap_stock.save()
                
                status_code = status.HTTP_200_OK
                response_data = {
                    "status": "true",
                    "title": "Success",
                    "message": "Scrap Stock Transfer successfully Completed",
                }
        
        except IntegrityError as e:
            status_code = status.HTTP_400_BAD_REQUEST
            response_data = {
                "status": "false",
                "title": "Failed",
                "message": str(e),
            }
        
        except Exception as e:
            status_code = status.HTTP_400_BAD_REQUEST
            response_data = {
                "status": "false",
                "title": "Failed",
                "message": str(e),
            }
        
        return Response(response_data, status=status_code)
    
    
class addDamageBottleAPIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')
        try:
            with transaction.atomic():
                if product_id:
                    product_item = ProdutItemMaster.objects.get(pk=product_id)
                    # print(f"Product ID: {product_id} retrieved successfully.")

                else:
                    product_item = ProdutItemMaster.objects.get(product_name="5 Gallon")
                    # print("Product name '5 Gallon' retrieved successfully.")
                
                DamageBottleStock.objects.create(
                        product=product_item,
                        quantity=quantity,
                        created_by=request.user.pk,
                        created_date=datetime.today(),
                    )
                
                # Create or update ScrapStock
                scrap_stock = ScrapStock.objects.get(product=product_item)
                scrap_stock.quantity += quantity
                scrap_stock.save()
                
                # Update VanProductStock to decrement empty_can_count
                van_product_stock = VanProductStock.objects.filter(product=product_item).first()
                if van_product_stock:
                    van_product_stock.empty_can_count = max(0, van_product_stock.empty_can_count - quantity)  # Ensure count doesn't go negative
                    van_product_stock.save()
                    # print(f"VanProductStock updated: {van_product_stock} EmptyStock {van_product_stock.empty_can_count}.")
                    
                status_code = status.HTTP_200_OK
                response_data = {
                    "status": "true",
                    "title": "Success",
                    "message": "Damage Stock successfully Added",
                }
        
        except IntegrityError as e:
            status_code = status.HTTP_400_BAD_REQUEST
            response_data = {
                "status": "false",
                "title": "Failed",
                "message": str(e),
            }
        
        except Exception as e:
            status_code = status.HTTP_400_BAD_REQUEST
            response_data = {
                "status": "false",
                "title": "Failed",
                "message": str(e),
            }
        
        return Response(response_data, status=status_code)
    
    
class ExcessBottleCountAPIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')
        try:
            with transaction.atomic():
                if product_id:
                    product_item = ProdutItemMaster.objects.get(pk=product_id)
                else:
                    product_item = ProdutItemMaster.objects.get(product_name="5 Gallon")
                
                van_route = Van_Routes.objects.get(van__salesman=request.user)
                route_master = van_route.routes
                ExcessBottleCount.objects.create(
                        van=van_route.van,
                        route=route_master,
                        # product=product_item,
                        bottle_count=quantity,
                        created_by=request.user.pk,
                        created_date=datetime.today(),
                    )
                
                van_product_stock = VanProductStock.objects.get(van=van_route.van,created_date=datetime.today().date())
                van_product_stock.excess_bottle += quantity
                van_product_stock.save()
                
                status_code = status.HTTP_200_OK
                response_data = {
                    "status": "true",
                    "title": "Success",
                    "message": "Excess Bottle Stock successfully Added",
                }
        
        except IntegrityError as e:
            status_code = status.HTTP_400_BAD_REQUEST
            response_data = {
                "status": "false",
                "title": "Failed",
                "message": str(e),
            }
        
        except Exception as e:
            status_code = status.HTTP_400_BAD_REQUEST
            response_data = {
                "status": "false",
                "title": "Failed",
                "message": str(e),
            }
        
        return Response(response_data, status=status_code)
    
    
    
class ProductTransferChoicesAPI(APIView):
    def get(self, request, *args, **kwargs):
        re_instances = ProductionDamageReason.objects.all()
        data = {
            "product_transfer_from_choices": [{'value': key, 'display': value} for key, value in PRODUCT_TRANSFER_FROM_CHOICES],
            "product_transfer_to_choices": [{'value': key, 'display': value} for key, value in PRODUCT_TRANSFER_TO_CHOICES],
            "reasons" : ProductionDamageReasonSerializer(re_instances,many=True).data
        }
        
        
        response_data = {
            "status": status.HTTP_200_OK,
            "data": data,
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
class ProductionDamageAPIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        instances = ProductionDamage.objects.all()
        serializer = ProductionDamageSerializer(instances,many=True)
        
        status_code = status.HTTP_200_OK
        response_data = {
            "status": status_code,
            "data": serializer.data,
        }
        
        return Response(response_data, status=status_code)
    
    def post(self, request, *args, **kwargs):
        route_id = request.data.get('route_id')
        quantity = request.data.get('quantity')
        reason = request.data.get('reason')
        product_from = request.data.get('product_from')
        product_to = request.data.get('product_to')
        
        try:
            with transaction.atomic():
                product_instance = ProdutItemMaster.objects.get(product_name="5 Gallon")
                route_instance = RouteMaster.objects.get(pk=route_id)
                reason_instance = ProductionDamageReason.objects.get(pk=reason)
                
                ProductionDamage.objects.create(
                    product=product_instance,
                    route=route_instance,
                    branch=request.user.branch_id,
                    product_from=product_from,
                    product_to=product_to,
                    quantity=quantity,
                    reason=reason_instance,
                    created_by=request.user.id,
                    created_date=datetime.today().now(),
                )
                
                if product_from == "fresh":
                    product_stock = ProductStock.objects.get(product_name=product_instance,branch=request.user.branch_id)
                    product_stock.quantity -= quantity
                    product_stock.save()
                    
                if product_from == "used":
                    product_stock = WashedUsedProduct.objects.get(product=product_instance)
                    product_stock.quantity -= quantity
                    product_stock.save()
                    
                if product_to == "scrap":
                    product_stock = ScrapStock.objects.get(product=product_instance)
                    product_stock.quantity += quantity
                    product_stock.save()
                    
                if product_to == "service":
                    product_stock = WashingStock.objects.get(product=product_instance)
                    product_stock.quantity += quantity
                    product_stock.save()
                
                status_code = status.HTTP_201_CREATED
                response_data = {
                    "status": status_code,
                    "title": "Success",
                    "message": "Production Damage Stock successfully Added",
                }
        
        except IntegrityError as e:
            status_code = status.HTTP_400_BAD_REQUEST
            response_data = {
                "status": status_code,
                "title": "Failed",
                "message": str(e),
            }
        
        except Exception as e:
            status_code = status.HTTP_400_BAD_REQUEST
            response_data = {
                "status": status_code,
                "title": "Failed",
                "message": str(e),
            }
        
        return Response(response_data, status=status_code)
    
class VanSaleDamageAPIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        instances = VanSaleDamage.objects.all()
        serializer = VanSaleDamageSerializer(instances,many=True)
        
        status_code = status.HTTP_200_OK
        response_data = {
            "status": status_code,
            "data": serializer.data,
        }
        
        return Response(response_data, status=status_code)
    
    def post(self, request, *args, **kwargs):
        damage_from = request.data.get('from')
        reason = request.data.get('reason')
        quantity = request.data.get('quantity')
        van_instance = Van.objects.get(salesman=request.user)
        
        try:
            with transaction.atomic():
                product_instance = ProdutItemMaster.objects.get(product_name="5 Gallon")
                reason_instance = ProductionDamageReason.objects.get(pk=reason)
                
                VanSaleDamage.objects.create(
                    product=product_instance,
                    reason=reason_instance,
                    van=van_instance,
                    quantity=quantity,
                    created_by=request.user.id,
                    created_date=datetime.now(),
                )
                
                vanstock = VanProductStock.objects.get(product=product_instance,created_date=datetime.now().date(),van=van_instance)
    
                if damage_from == "fresh_stock" :
                    vanstock.stock -= quantity
                    
                if damage_from == "empty_can" :
                    vanstock.empty_can_count -= quantity
                
                vanstock.damage_count += quantity
                vanstock.save()
                
                
                status_code = status.HTTP_201_CREATED
                response_data = {
                    "status": status_code,
                    "title": "Success",
                    "message": "Van Damage Stock successfully Added",
                }
        
        except IntegrityError as e:
            status_code = status.HTTP_400_BAD_REQUEST
            response_data = {
                "status": status_code,
                "title": "Failed",
                "message": str(e),
            }
        
        except Exception as e:
            status_code = status.HTTP_400_BAD_REQUEST
            response_data = {
                "status": status_code,
                "title": "Failed",
                "message": str(e),
            }
        
        return Response(response_data, status=status_code)
    
class CustomerProductReturnAPIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        instances = CustomerProductReturn.objects.all()
        serializer = CustomerProductReturnSerializer(instances,many=True)
        
        status_code = status.HTTP_200_OK
        response_data = {
            "status": status_code,
            "data": serializer.data,
        }
        
        return Response(response_data, status=status_code)
    
    def post(self, request, *args, **kwargs):
        
        data = request.data
        serializer = CustomerProductReturnSerializer(data=data, context={'request': request})
        try:
            with transaction.atomic():
                if serializer.is_valid():
                    
                    van_instance = Van.objects.get(salesman=request.user)
                    return_instance = serializer.save(
                        created_by=request.user.id,
                        created_date=datetime.today(),
                        van=van_instance
                    )
                    
                    if return_instance.product.category.category_name != "Coupons":
                        stock_instance = VanProductStock.objects.get(van=van_instance,created_date=datetime.today().date(),product=return_instance.product)
                        stock_instance.return_count += return_instance.quantity
                        stock_instance.save()
                        
                    if return_instance.product.category.category_name == "Coupons":
                        book_numbers = request.data.get('book_numbers').split(',')
                        
                        for book_number in book_numbers :
                            coupon = NewCoupon.objects.get(book_num=book_number)
                            
                            stock_instance = VanCouponStock.objects.get(van=van_instance,created_date=datetime.today().date(),coupon=coupon)
                            stock_instance.return_count += return_instance.quantity
                            stock_instance.save()
                            
                            

                    status_code = status.HTTP_201_CREATED
                    response_data = {
                        "StatusCode": status_code,
                        "status": status_code,
                        "data": serializer.data,
                    }

                else:
                    status_code = status.HTTP_400_BAD_REQUEST
                    response_data = {
                        "StatusCode": status_code,
                        "status": status_code,
                        "message": serializer.errors,
                    }
                        
        except IntegrityError as e:
            status_code = status.HTTP_400_BAD_REQUEST
            response_data = {
                "StatusCode": 400,
                "status": status_code,
                "title": "Failed",
                "message": str(e),
            }

        except Exception as e:
            status_code = status.HTTP_400_BAD_REQUEST
            response_data = {
                "StatusCode": 400,
                "status": status_code,
                "title": "Failed",
                "message": str(e),
            }
        
        return Response(response_data, status=status_code)
    
    
class CustomerProductReplaceAPIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        instances = CustomerProductReplace.objects.all()
        serializer = CustomerProductReplaceSerializer(instances,many=True)
        
        status_code = status.HTTP_200_OK
        response_data = {
            "status": status_code,
            "data": serializer.data,
        }
        
        return Response(response_data, status=status_code)
    
    def post(self, request, *args, **kwargs):
        
        data = request.data
        serializer = CustomerProductReplaceSerializer(data=data, context={'request': request})
        try:
            with transaction.atomic():
                if serializer.is_valid():
                    
                    van_instance = Van.objects.get(salesman=request.user)
                    
                    replace_instance = serializer.save(
                        created_by=request.user.id,
                        created_date=datetime.today(),
                        van=van_instance
                    )
                    
                    if replace_instance.product.category.category_name != "Coupons":
                        stock_instance = VanProductStock.objects.get(van=van_instance,created_date=datetime.today().date())
                        stock_instance.stock -= replace_instance.quantity
                        stock_instance.save()
                        
                    if replace_instance.product.category.category_name == "Coupons":
                        book_numbers = request.data.get('book_numbers').split(',')
                        
                        for book_number in book_numbers :
                            coupon = NewCoupon.objects.get(book_num=book_number)
                            
                            stock_instance = VanCouponStock.objects.get_or_(van=van_instance,created_date=datetime.today().date(),coupon=coupon)
                            stock_instance.stock -= replace_instance.quantity
                            stock_instance.save()
                            
                            CustomerCouponItems.objects.filter(customer_coupon__customer=replace_instance.customer,coupon=coupon).delete()
                         
                        stock = CustomerCouponStock.objects.get(customer=replace_instance.customer,coupon_type_id__coupon_type_name=replace_instance.product.product_name,coupon_method="manual")
                        stock.count -= replace_instance.quantity
                        stock.save()

                    status_code = status.HTTP_201_CREATED
                    response_data = {
                        "StatusCode": status_code,
                        "status": status_code,
                        "data": serializer.data,
                    }

                else:
                    status_code = status.HTTP_400_BAD_REQUEST
                    response_data = {
                        "StatusCode": status_code,
                        "status": status_code,
                        "message": serializer.errors,
                    }
                        
        except IntegrityError as e:
            status_code = status.HTTP_400_BAD_REQUEST
            response_data = {
                "StatusCode": 400,
                "status": status_code,
                "title": "Failed",
                "message": str(e),
            }

        except Exception as e:
            status_code = status.HTTP_400_BAD_REQUEST
            response_data = {
                "StatusCode": 400,
                "status": status_code,
                "title": "Failed",
                "message": str(e),
            }
        
        return Response(response_data, status=status_code)
    


class CustomerCouponListAPIView(APIView):
    def get(self, request, customer_id):
        try:
            customer_coupon_ids = CustomerCouponItems.objects.filter(
                customer_coupon__customer__customer_id=customer_id
            ).values_list('coupon__coupon_id', flat=True)

            coupons = NewCoupon.objects.filter(
                pk__in=customer_coupon_ids
            ).annotate(
                unused_leaflets_count=Count('leaflets', filter=Q(leaflets__used=False))
            ).filter(
                unused_leaflets_count__gt=0
            )

            serializer = NewCouponSerializer(coupons, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Customers.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        
        
class CreditNoteListAPI(APIView):
    def get(self, request, *args, **kwargs):
        queryset = CreditNote.objects.filter(is_deleted=False)
        
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        sales_type = request.query_params.get('sales_type')
        query = request.query_params.get('q')
        
        if start_date_str and end_date_str:
            try:
                start_date = parse_date(start_date_str)
                end_date = parse_date(end_date_str)
                if start_date and end_date:
                    queryset = queryset.filter(created_date__range=[start_date, end_date])
            except ValueError:
                return Response({"error": "Invalid date format"}, status=status.HTTP_400_BAD_REQUEST)
        
        if sales_type:
            queryset = queryset.filter(customer__sales_type=sales_type)
        
        if query:
            queryset = queryset.filter(credit_note_no__icontains=query)

        # Aggregating the totals for the fields
        totals = queryset.aggregate(
            total_net_taxable=Sum('net_taxable'),
            total_vat=Sum('vat'),
            total_amount_total=Sum('amout_total'),
            total_amount_received=Sum('amout_recieved')
        )

        # Serialize the queryset
        serializer = CreditNoteSerializer(queryset, many=True)
        
        # Combine the serialized data and the aggregated totals in the response
        response_data = {
            'credit_notes': serializer.data,
            'totals': totals
        }

        return Response(response_data, status=status.HTTP_200_OK)
    
class ProductRouteSalesReportAPIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        product_id = request.GET.get('product_id') 

        if not start_date:
            start_date = datetime.today().date()
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()

        if not end_date:
            end_date = datetime.today().date() + timedelta(days=1)
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        instances = ProdutItemMaster.objects.exclude(category__category_name="Coupons")
        
        if product_id:
            instances = instances.filter(id=product_id)
        
        serializer = ProductSalesReportSerializer(
            instances,
            many=True,
            context={'user_id': request.user.pk, 'start_date': start_date, 'end_date': end_date}
        )

        return Response(serializer.data, status=status.HTTP_200_OK)
    

class SalesInvoicesAPIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        invoice_type = request.GET.get('invoice_types')  
        
        if not start_date:
            start_date = datetime.today().date()
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        
        if not end_date:
            end_date = datetime.today().date()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        route = Van_Routes.objects.get(van__salesman=request.user).routes
        
        instances = Invoice.objects.filter(
            created_date__date__gte=start_date,
            created_date__date__lte=end_date,
            customer__routes=route
        )
        
        if invoice_type:
            instances = instances.filter(invoice_type=invoice_type)
        
        serializer = SalesInvoiceSerializer(instances, many=True)
        
        response_data = {
            "StatusCode": status.HTTP_200_OK,
            "status": status.HTTP_200_OK,
            "data": {
                "invoices": serializer.data,
                "total_taxable": instances.aggregate(total_net_taxable=Sum('net_taxable'))['total_net_taxable'] or 0,
                "total_vat": instances.aggregate(total_vat=Sum('vat'))['total_vat'] or 0,
                "total_amount": instances.aggregate(total_amount=Sum('amout_total'))['total_amount'] or 0,
                "total_amount_collected": instances.aggregate(total_amout_recieved=Sum('amout_recieved'))['total_amout_recieved'] or 0,
                "filter_data": {
                    "invoice_types": [{'key': key, 'value': value} for key, value in INVOICE_TYPES],
                    "start_date": start_date,
                    "end_date": end_date,
                    "route_name": route.route_name,
                }
            },
        }

        return Response(response_data, status=status.HTTP_200_OK)
    
class CustomerSupplyListAPIView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        instances = CustomerSupply.objects.filter(salesman=request.user).order_by("-created_date")
        
        product_id = request.GET.get('product_id', None)
        filter_date_str = request.GET.get('filter_date', None)

        if product_id:
            instances = instances.filter(id__in=CustomerSupplyItems.objects.filter(product_id=product_id).values('customer_supply_id'))

        if filter_date_str:
            filter_date = datetime.strptime(filter_date_str, '%Y-%m-%d').date()
            instances = instances.filter(created_date__date=filter_date)

        serializer = CustomersSupplysSerializer(instances, many=True)
        data = serializer.data
        
        total_supplied = sum(item['supplied'] for item in data if 'supplied' in item)
        
        response_data = {
            'items': data,
            'total_supplied': total_supplied
        }

        return Response(response_data, status=status.HTTP_200_OK)
    
    
class CustomersOutstandingAmountsAPI(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            start_date = date.today()
            end_date = date.today()

        filter_start_date = start_date.strftime('%Y-%m-%d')
        filter_end_date = end_date.strftime('%Y-%m-%d')
        
        route = Van_Routes.objects.filter(van__salesman=request.user).first().routes
        instances = OutstandingAmount.objects.filter(customer_outstanding__created_date__date__gte=start_date,customer_outstanding__created_date__date__lte=end_date,customer_outstanding__customer__routes=route)
        serializer = CustomersOutstandingAmountsSerializer(instances, many=True, context={'user_id': request.user.pk})
        
        total_amount = instances.aggregate(total_amout_recieved=Sum('amount'))['total_amout_recieved'] or 0
        
        customer_ids = instances.values_list('customer_outstanding__customer__pk')
        dialy_collections = CollectionPayment.objects.filter(customer__pk__in=customer_ids,created_date__date__gte=start_date,created_date__date__lte=end_date).aggregate(total_amount=Sum('amount_received'))['total_amount'] or 0
        # total_amount = max(total_amount - dialy_collections, 0)
        total_amount = total_amount - dialy_collections
        
        return Response({
            'status': True,
            'message': 'Success',
            'data': 
                {
                    'filter_start_date': filter_start_date,
                    'filter_end_date': filter_end_date,
                    'data': serializer.data,
                    'total_amount': total_amount,
                    'total_collected_amount': dialy_collections,
                    'total_balance_amount': total_amount,
                },
        })
        

class CustomersOutstandingCouponsAPI(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            filter_start_date = start_date.strftime('%Y-%m-%d')
            filter_end_date = end_date.strftime('%Y-%m-%d')
        else:
            start_date = datetime.today().date()
            end_date = datetime.today().date()
            filter_start_date = date.strftime('%Y-%m-%d')
            filter_end_date = date.strftime('%Y-%m-%d')
        
        route = Van_Routes.objects.filter(van__salesman=request.user).first().routes
        instances = CustomerSupply.objects.filter(created_date__date__gte=start_date,created_date__date__lte=end_date,customer__routes=route,customer__sales_type="CASH COUPON")        
        serializer = CustomersOutstandingCouponSerializer(instances, many=True, context={'user_id': request.user.pk})
        
        supply_ids = instances.values_list('pk')
        total_suplied_count = CustomerSupplyItems.objects.filter(customer_supply__pk__in=supply_ids).aggregate(total_qty=Sum('quantity'))['total_qty'] or 0
        
        manual_coupon_count = CustomerSupplyCoupon.objects.filter(customer_supply__pk__in=supply_ids).aggregate(Count('leaf'))['leaf__count'] or 0
        digital_coupon_count = CustomerSupplyDigitalCoupon.objects.filter(customer_supply__pk__in=supply_ids).aggregate(total_count=Sum('count'))['total_count'] or 0
        total_recieved_count = manual_coupon_count + digital_coupon_count
        
        total_pending_count = total_suplied_count - total_recieved_count
        
        return Response({
            'status': True,
            'message': 'Success',
            'data': 
                {
                    'filter_start_date': filter_start_date,
                    'filter_end_date': filter_end_date,
                    'data': serializer.data,
                    'total_suplied_count': total_suplied_count,
                    'total_recieved_count': total_recieved_count,
                    'total_pending_count': total_pending_count,
                },
        })
        

class CustomersOutstandingBottlesAPI(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            start_date = datetime.today().date()
            end_date = datetime.today().date()
            
        filter_start_date = start_date.strftime('%Y-%m-%d')
        filter_end_date = end_date.strftime('%Y-%m-%d')
        
        route = Van_Routes.objects.filter(van__salesman=request.user).first().routes
        instances = CustomerSupply.objects.filter(created_date__date__gte=start_date,created_date__date__lte=end_date,customer__routes=route)        
        serializer = CustomersOutstandingBottlesSerializer(instances, many=True, context={'user_id': request.user.pk})
        
        supply_ids = instances.values_list('pk')
        total_suplied_count = CustomerSupplyItems.objects.filter(customer_supply__pk__in=supply_ids).aggregate(total_qty=Sum('quantity'))['total_qty'] or 0
        
        total_recieved_count = instances.aggregate(total_qty=Sum('collected_empty_bottle'))['total_qty'] or 0
        
        total_pending_count = total_suplied_count - total_recieved_count
        
        return Response({
            'status': True,
            'message': 'Success',
            'data': 
                {
                    'filter_start_date': filter_start_date,
                    'filter_end_date': filter_end_date,
                    'data': serializer.data,
                    'total_suplied_count': total_suplied_count,
                    'total_recieved_count': total_recieved_count,
                    'total_pending_count': total_pending_count,
                },
        })
        
class SalesmanListAPIView(APIView):
    """
    API view to list all salesmen.
    """

    def get(self, request):
        route_id = request.data.get('route_id')

        if not route_id:
            return Response({"error": "route_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Get all vans that have the given route_id
        vans_route = Van_Routes.objects.filter(routes__route_id=route_id).values_list('van', flat=True)

        # Get salesmen associated with those vans
        salesmen = CustomUser.objects.filter(user_type='Salesman', salesman_van__van_id__in=vans_route)

        # Serialize the salesmen data
        serializer = SalesmanSerializer(salesmen, many=True)

        # Return the serialized data with a 200 OK response
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class CustomerRegistrationRequestView(APIView):
    def get(self, request, *args, **kwargs):
        instances = CustomerRegistrationRequest.objects.all()
        serializer = CustomerRegistrationRequestSerializer(instances,many=True)
        
        status_code = status.HTTP_200_OK
        response_data = {
            "status": status_code,
            "data": serializer.data,
        }
        
        return Response(response_data, status=status_code)
    
    def post(self, request, *args, **kwargs):
        serializer = CustomerRegistrationRequestSerializer(data=request.data, context={'request': request})
        try:
            with transaction.atomic():
                if serializer.is_valid():
                    instance = serializer.save(
                        created_date=datetime.today(),
                    )                    
                    status_code = status.HTTP_201_CREATED
                    response_data = {
                        "StatusCode": status_code,
                        "status": status_code,
                        "data": serializer.data,
                    }
                else:
                    status_code = status.HTTP_400_BAD_REQUEST
                    response_data = {
                        "StatusCode": status_code,
                        "status": status_code,
                        "message": serializer.errors,
                    }
                        
        except IntegrityError as e:
            status_code = status.HTTP_400_BAD_REQUEST
            response_data = {
                "StatusCode": 400,
                "status": status_code,
                "title": "Failed",
                "message": str(e),
            }

        except Exception as e:
            status_code = status.HTTP_400_BAD_REQUEST
            response_data = {
                "StatusCode": 400,
                "status": status_code,
                "title": "Failed",
                "message": str(e),
            }
        
        return Response(response_data, status=status_code)
    
    
