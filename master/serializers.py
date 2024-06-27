from rest_framework import serializers
from . models import *


class RouteMasterSerializers(serializers.ModelSerializer):
    class Meta :
        model = RouteMaster
        fields = '__all__'



class LocationMasterSerializers(serializers.ModelSerializer):
    class Meta :
        model = LocationMaster
        fields = '__all__'


class DesignationMasterSerializers(serializers.ModelSerializer):
    class Meta :
        model = DesignationMaster
        fields = '__all__'


class BranchMasterSerializers(serializers.ModelSerializer):
    class Meta :
        model = BranchMaster
        fields = '__all__'

class CategoryMasterSerializers(serializers.ModelSerializer):
    class Meta :
        model = CategoryMaster
        fields = '__all__'


class EmirateMasterSerializers(serializers.ModelSerializer):
    class Meta :
        model = EmirateMaster
        fields = '__all__'