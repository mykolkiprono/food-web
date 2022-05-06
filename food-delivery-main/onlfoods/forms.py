from .models import Customer, Orders
from django.contrib.auth.models import User
from django import forms
from . import models
from datetime import datetime
from bootstrap_datepicker_plus.widgets import DateTimePickerInput



from django.utils import timezone		
class AddressForm(forms.Form):
    Email = forms.EmailField()
    Mobile= forms.IntegerField()
    Address = forms.CharField(max_length=500)
    expected_time = forms.DateTimeField(widget=DateTimePickerInput())
    shifts =(
        ('morning','morning'),
        ('lunch','lunch'),
        ('evening','evening'),
        
    )
    shift = forms.ChoiceField(choices=shifts)
    monthly = forms.BooleanField(required=False)

    def clean(self):
        super(AddressForm, self).clean()
        expected_time = self.cleaned_data.get('expected_time')
        Mobile = self.cleaned_data.get('Mobile')

        if expected_time < timezone.now():
            self._errors['expected_time'] = self.error_class(['must be a date in the future'])

        if len(str(Mobile))<10:
            self._errors['Mobile'] = self.error_class(['must be a minimum of 10 characters'])  


class FeedbackForm(forms.ModelForm):
    class Meta:
        model=models.Feedback
        fields=['feed']

#for updating status of order
class OrderForm(forms.ModelForm):
    class Meta:
        model=models.Orders
        fields=['status']


class FoodForm(forms.ModelForm):
    class Meta:
        model=models.Food
        fields=['f_name','f_price','f_desc','image']
        

#for contact us page
class ContactusForm(forms.Form):
    Name = forms.CharField(max_length=30)
    Email = forms.EmailField()
    Message = forms.CharField(max_length=500,widget=forms.Textarea(attrs={'rows': 3, 'cols': 30}))

class CustomerForm(forms.ModelForm):

    class Meta:
        model = Customer 
        fields= ['profile_pic','c_email','c_region','c_phone_number','address']


    def clean(self):
        super(CustomerForm, self).clean()

        c_phone_number = self.cleaned_data.get('c_phone_number')
        address = self.cleaned_data.get('address')

        if len(str(c_phone_number))<10:
            self._errors['c_phone_number'] = self.error_class(['must be a minimum of 10 characters'])               

        if len(str(address))<5:
            self._errors['address'] = self.error_class(['must be a valid address'])           

        return self.cleaned_data
        

class statusForm(forms.ModelForm):
    class Meta:
        model = models.Orders
        fields = ['status']

class UserForm(forms.ModelForm):

    class Meta:
        model = User 
        fields = ['username','password']

    def clean(self):
        super(UserForm, self).clean()
        username = self.cleaned_data.get('username')
        if username.isnumeric():
            self._errors['username'] = self.error_class(['username cannot be numbers'])
        if len(username) < 5:
            self._errors['username'] = self.error_class(['username must be more than 5 characters'])