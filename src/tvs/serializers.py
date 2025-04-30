from rest_framework import serializers
from .models import TV, TVType, TVModel

class TvTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TVType
        fields = '__all__'

class TvModelSerializer(serializers.ModelSerializer):
    type = TvTypeSerializer(read_only=True)
    
    class Meta:
        model = TVModel
        fields = '__all__'

class TvSerializer(serializers.ModelSerializer):
    type = TvTypeSerializer(read_only=True)
    model = TvModelSerializer(read_only=True)
    
    class Meta:
        model = TV
        fields = '__all__'