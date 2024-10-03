from rest_framework import exceptions, serializers, status, generics


from .models import *


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class ContentBlockTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentBlockType
        fields = '__all__'

class ContentBlockSerializer(serializers.ModelSerializer):
    type = ContentBlockTypeSerializer(read_only=True)
    class Meta:
        model = ContentBlock
        fields = '__all__'

class NewsItemShortSerializer(serializers.ModelSerializer):
    tag = TagSerializer(read_only=True)
    class Meta:
        model = NewsItem
        exclude = ['html_content']


class NewsItemSerializer(serializers.ModelSerializer):
    tag = TagSerializer(read_only=True)
    content_blocks = ContentBlockSerializer(many=True, read_only=True)
    class Meta:
        model = NewsItem
        fields = '__all__'











