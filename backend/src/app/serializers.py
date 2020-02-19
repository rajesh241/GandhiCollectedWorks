"""Serializer classes for the application"""
from rest_framework import serializers, fields
from app.models import Article





class ArticleSerializer(serializers.ModelSerializer):
    """Serializer for Article Model"""
    class Meta:
        """Meta Class"""
        model = Article
        fields = '__all__'
