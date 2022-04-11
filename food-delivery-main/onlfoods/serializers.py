from .models import Customer, Region, Food, monthly_plan, Feedback, Orders, Offers
from rest_framework import serializers
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username','email','password')


 
class CustomerSerializer(serializers.ModelSerializer):
    img_url = serializers.SerializerMethodField()
    user = UserSerializer()
    class Meta:
        model = Customer
        fields = '__all__'
    def get_img_url(self, obj):
        return self.context['request'].build_absolute_uri()



class FoodSerializer(serializers.ModelSerializer):
    img_url = serializers.SerializerMethodField()
    class Meta:
        model = Food
        fields = '__all__'

    def get_img_url(self, obj):
        return self.context['request'].build_absolute_uri()


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = '__all__'

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'

class monthly_planSerializer(serializers.ModelSerializer):
    class Meta:
        model = monthly_plan
        fields = '__all__'


class OrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orders
        fields = '__all__'


class OffersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offers
        fields = '__all__'

class AdminPanelSerializer(serializers.ModelSerializer):
    food = Food.objects.all().count()
    orders = Orders.objects.all().count()
    totalsales = Orders.objects.all().filter(status = True).count()
    offers = Offers.objects.all().count()
    customers = Customer.objects.all().count()

    class Meta:
        fields = ['food','orders','totalsales','offers','customers']

