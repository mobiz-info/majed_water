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
        
        
class EmiratesBasedLocationsSerializers(serializers.ModelSerializer):
    locations = serializers.SerializerMethodField()
    class Meta :
        model = EmirateMaster
        fields = ['emirate_id','name','locations']
        
    def get_locations(self,obj):
        branch_id = self.context.get('branch_id')
        
        instances = LocationMaster.objects.filter(emirate=obj)
        if branch_id:
            instances = instances.filter(branch_id__pk=branch_id)
        return LocationMasterSerializers(instances, many=True).data