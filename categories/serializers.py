from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from .models import MainCategory, SubCategory
from rest_framework import serializers
from .models import ContactMessage


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = '__all__'


class MainCategorySerializer(serializers.ModelSerializer):
    subcategories = SubCategorySerializer(many=True, read_only=True)

    class Meta:
        model = MainCategory
        fields = '__all__'


class ContactMessageSerializer(serializers.ModelSerializer):
    phone = PhoneNumberField(region='DE')
    class Meta:
        model = ContactMessage
        fields = '__all__'