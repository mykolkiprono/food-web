from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator


class Region(models.Model):
	r_name = models.CharField(max_length=20)
	image = models.ImageField(upload_to='regions',null=True,blank=True)
	r_desc = models.CharField(max_length=50)

	def __str__(self):
		return str(self.r_name)

class Region_manager(models.Model):
	region = models.OneToOneField(Region,on_delete=models.CASCADE)
	r_email = models.EmailField()

	def __str__(self):
		return str(self.region)
	

class Customer(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE,null=True)
	profile_pic = models.ImageField(upload_to = 'profiles',null=True,blank=True)
	c_email = models.EmailField()
	# name = models.CharField(max_length=30)
	c_phone_number = models.CharField(max_length=10)
	c_region = models.ForeignKey('Region', on_delete=models.CASCADE)
	STATUS =(
        ('active','active'),
        ('dormant','dormant'),
        
    )
	status = models.CharField(max_length=20,null=True,choices=STATUS,default="active")
	address = models.CharField(max_length=20)
	# of_offer = models.
	@property
	def get_name(self):
		return self.user.username
	@property
	def get_id(self):
  		return self.user.id
	def __str__(self):
		return self.user.username

class Food(models.Model):
	f_price = models.PositiveIntegerField()
	f_name = models.CharField(max_length=20)
	image = models.ImageField(upload_to='food',null=True,blank=True)
	f_desc = models.CharField(max_length=50)

	def __str__(self):
		return str(self.f_name)
STATUS =(
        ('Pending','Pending'),
        ('Order Confirmed','Order Confirmed'),
        ('Out for Delivery','Out for Delivery'),
        ('Delivered','Delivered'),
    )
class Orders(models.Model):
	customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
	date_ordered = models.DateTimeField(auto_now_add=True)
	expected_time = models.DateTimeField()
	# order_time = models.DateTimeField(auto_now=True)
	food = models.ForeignKey('Food',on_delete=models.CASCADE)
	status=models.CharField(max_length=50,null=True,choices=STATUS )
	address = models.CharField(max_length=500,null=True)
	shifts =(
        ('morning','morning'),
        ('lunch','lunch'),
        ('evening','evening'),
        
    )
	shift = models.CharField(max_length=20,default="lunch",choices=shifts)
	delivered_time = models.DateTimeField(null=True,blank=True)

	def __str__(self):
		return str(self.food)

class Feedback(models.Model):
	user = models.ForeignKey(Customer,on_delete=models.CASCADE, null = True, blank=True)
	date = models.DateTimeField(auto_now_add=True, null=True,blank=True)
	feed = models.CharField(max_length=100)

	def __str__(self):
		return str(self.user)


class Offers(models.Model):
	food = models.ForeignKey(Food,on_delete=models.CASCADE)
	region = models.ForeignKey('Region',on_delete=models.CASCADE)
	offer_expiry = models.DateTimeField()
	percentage = models.PositiveIntegerField(default=25)
	pieces = models.PositiveIntegerField()

	def __str__(self):
		return str(self.food) 
	

class monthly_plan(models.Model):
	food = models.ForeignKey('Food',on_delete=models.CASCADE)
	customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
	delivery_time = models.DateTimeField()
	shifts =(
        ('morning','morning'),
        ('lunch','lunch'),
        ('evening','evening'),
        
    )
	shift = models.CharField(max_length=20,default="lunch",choices=shifts)
	

	# def __str__(self):
	# 	return str(self.customer), "'s",str(self.food),"delivery at ",str(self.delivery_time) 


