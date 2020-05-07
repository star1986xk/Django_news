from rest_framework import serializers
from app import models


class NewsTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.NewsTable
        fields = '__all__'

class NewsTableSerializerList(serializers.ModelSerializer):
    class Meta:
        model = models.NewsTable
        fields = 'id','title','keyword','source','get_time','url'