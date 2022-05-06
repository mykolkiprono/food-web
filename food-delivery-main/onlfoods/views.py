from django.shortcuts import render, redirect, reverse
from rest_framework.response import Response
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required,user_passes_test
from django.http import HttpResponse,HttpResponseRedirect
from .models import Customer, Region, Food, monthly_plan, Feedback, Orders, Offers, Blogs
from .serializers import CustomerSerializer, RegionSerializer, FoodSerializer, FeedbackSerializer, OffersSerializer, UserSerializer, AdminPanelSerializer
from rest_framework import serializers
from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.contrib.auth.models import User
from .forms import CustomerForm, UserForm
from django.contrib import messages
from . import forms
from . import models
from django.core.mail import send_mail
from django.conf import settings

import collections



# User ==============================================================================================================
@api_view(['GET'])
def get_user(request, pk):
    serializer_context = {
            'request': request,
        }
    user = User.objects.get(id=pk)
    serializer = UserSerializer(user, many=False,context=serializer_context)

    customer = Customer.objects.get(id=pk)
    serializer2 = CustomerSerializer(customer, many=False,context=serializer_context)
    return Response(serializer2.data)

@api_view(['PUT'])
def edit_user(request, pk):
    objs = User.objects.get(id=pk)
    print(objs.name())
    serializer = UserSerializer(objs, many=False)
    return Response(serializer.data)

@api_view(['POST'])
def signup(request):
    data = request.data
    user = User.objects.create( {     
    "user": {
        "email": data["email"],
        "password": data["password"]
    },
    "profile_pic": data["profile_pic"],
    "c_email": data["c_email"],
    "c_phone_number": data["c_phone_number"],
    "address": data["address"],
    "c_region": data["c_region"]
    }
        )
    # objs = User.objects.get(id=pk)
    serializer = UserSerializer(objs, many=False)
    return Response(serializer.data)

# foods=============================================================
@api_view(['GET'])
def get_foods(request):
    serializer_context = {
            'request': request,
        }
    objs = Food.objects.all()
    serializer = FoodSerializer(objs, many=True,context=serializer_context)    
    return Response(serializer.data)

@api_view(['GET'])
def get_food(request,pk):
    serializer_context = {
            'request': request,
        }
    
    objs = Food.objects.get(id=pk)
    serializer = FoodSerializer(objs, many=False,context=serializer_context)
    return Response(serializer.data)


#admin============================================================================================
@api_view(['POST'])
def add_food(request):
    # objs = Food.objects.all(id=pk)
    data = request.data
    food = Food.objects.create(
            
        f_price = data['f_price'],
        f_name =data['f_name'],
        image_1 = data['image_1'],
        image_2 = data['image_2'],
        image_3 = data['image_3'],
        f_desc = data['f_desc']
        )
    serializer = FoodSerializer(food, many=False)
    return Response(serializer.data)

@api_view(['PUT'])
def update_food(request,pk):
    data = request.data
    food = Food.objects.get(id=pk)

    serializer = FoodSerializer(food, data=request.data)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)

@api_view(['DELETE'])
def delete_food(request,pk):
    food = Food.objects.get(id=pk)
    food.delete()
    return Response('food deleted')

@api_view(['GET'])
def adm_dashboard(request):
    food = Food.objects.all().count()
    orders = Orders.objects.all().count()
    totalsales = Orders.objects.all().filter(status = True).count()
    offers = Offers.objects.all().count()
    customers = Customer.objects.all().count()
    dash = [{
        'food':food,
        'orders':orders,
        'offers': offers,
        'customers': customers,
        'totalsales':totalsales
    }]
    return JsonResponse(dash, safe=False)

# on offer============================================================================================
@api_view(['GET'])
def offers(request):
    offer = Offers.objects.all()
    serializer = OffersSerializer(offer, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def offer(request,pk):
    offer = Offers.objects.get(id=pk)
    serializer = OffersSerializer(offer, many=False)
    return Response(serializer.data)

def signup(request):
    userForm=UserForm()
    customerForm=CustomerForm()
    mydict={'userForm':userForm,'customerForm':customerForm}
    if request.method=='POST':
        userForm=UserForm(request.POST)
        customerForm=CustomerForm(request.POST,request.FILES)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customer=customerForm.save(commit=False)
            customer.user=user
            customer.save()
            my_customer_group = Group.objects.get_or_create(name='CUSTOMER')
            my_customer_group[0].user_set.add(user)

            return HttpResponseRedirect("customerlogin")

        else:
            HttpResponse("error")
        
    return render(request,'signup.html',{'userForm':userForm,'customerForm':customerForm})


def is_customer(user):
    return user.groups.filter(name='CUSTOMER').exists()

#---------AFTER ENTERING CREDENTIALS WE CHECK WHETHER USERNAME AND PASSWORD IS OF ADMIN,CUSTOMER
def afterlogin_view(request):
    if is_customer(request.user):
        return redirect('home_view')
    else:
        return redirect('admin_dashboard_view')

@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    # for cards on dashboard
    customercount=Customer.objects.all().count()
    foodcount=Food.objects.all().count()
    ordercount=Orders.objects.all().count()

    # for recent order tables
    orders=Orders.objects.all()
    ordered_products=[]
    ordered_bys=[]
    for order in orders:
        ordered_product=Food.objects.all().filter(id=order.food.id)
        ordered_by=Customer.objects.all().filter(id = order.customer.id)
        ordered_products.append(ordered_product)
        ordered_bys.append(ordered_by)

    mydict={
    'customercount':customercount,
    'productcount':foodcount,
    'ordercount':ordercount,
    'data':zip(ordered_products,ordered_bys,orders),
    }
    return render(request,'admin-dashboard.html',context=mydict)

# website

def home_view(request):
    products=Food.objects.all()
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'index.html',{'products':products,'product_count_in_cart':product_count_in_cart})

def offers_view(request):
    products=Offers.objects.all()
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'offers.html',{'products':products,'product_count_in_cart':product_count_in_cart})


# def index(request):
#     feed = Feedback.objects.all()
#     return render("landing/index.html")

 
#for showing login button for admin(by sumit)
def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return HttpResponseRedirect('adminlogin')

#-----------for checking user iscustomer
def is_customer(user):
    return user.groups.filter(name='CUSTOMER').exists()


#---------AFTER ENTERING CREDENTIALS WE CHECK WHETHER USERNAME AND PASSWORD IS OF ADMIN,CUSTOMER
def afterlogin_view(request):
    if is_customer(request.user):
        return redirect('customer-home')
    else:
        return redirect('admin-dashboard')

#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    # for cards on dashboard
    customercount=Customer.objects.all().count()
    productcount=Food.objects.all().count()
    ordercount=Orders.objects.all().count()

    # for recent order tables
    orders=Orders.objects.all()
    ordered_products=[]
    ordered_bys=[]
    for order in orders:
        ordered_product=Food.objects.all().filter(id=order.food.id)
        ordered_by=Customer.objects.all().filter(id = order.customer.id)
        ordered_products.append(ordered_product)
        ordered_bys.append(ordered_by)

    mydict={
    'customercount':customercount,
    'productcount':productcount,
    'ordercount':ordercount,
    'data':zip(ordered_products,ordered_bys,orders),
    }
    return render(request,'admin_dashboard.html',context=mydict)


# admin view customer table
@login_required(login_url='adminlogin')
def view_customer_view(request):
    customers=models.Customer.objects.all()
    return render(request,'view_customer.html',{'customers':customers})

# admin delete customer
@login_required(login_url='adminlogin')
def delete_customer_view(request,pk):
    customer=Customer.objects.get(id=pk)
    user=User.objects.get(id=customer.user_id)
    user.delete()
    customer.delete()
    return redirect('view-customer')


@login_required(login_url='adminlogin')
def update_customer_view(request,pk):
    customer=models.Customer.objects.get(id=pk)
    user=models.User.objects.get(id=customer.user_id)
    userForm=forms.CustomerUserForm(instance=user)
    customerForm=forms.CustomerForm(request.FILES,instance=customer)
    mydict={'userForm':userForm,'customerForm':customerForm}
    if request.method=='POST':
        userForm=forms.CustomerUserForm(request.POST,instance=user)
        customerForm=forms.CustomerForm(request.POST,instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            return redirect('view-customer')
    return render(request,'admin_update_customer.html',context=mydict)

# admin view the product
@login_required(login_url='adminlogin')
def admin_products_view(request):
    products=models.Food.objects.all()
    total = products.count()
    return render(request,'admin_products.html',{'products':products,'count':total})


# admin add product by clicking on floating button
@login_required(login_url='adminlogin')
def admin_add_product_view(request):
    productForm=forms.FoodForm()
    if request.method=='POST':
        productForm=forms.FoodForm(request.POST, request.FILES)
        if productForm.is_valid():
            productForm.save()
        return HttpResponseRedirect('admin-products')
    return render(request,'admin_add_products.html',{'productForm':productForm})


@login_required(login_url='adminlogin')
def delete_product_view(request,pk):
    product=models.Food.objects.get(id=pk)
    product.delete()
    return redirect('admin-products')


@login_required(login_url='adminlogin')
def update_product_view(request,pk):
    product=models.Product.objects.get(id=pk)
    productForm=forms.ProductForm(instance=product)
    if request.method=='POST':
        productForm=forms.FoodForm(request.POST,request.FILES,instance=product)
        if productForm.is_valid():
            productForm.save()
            return redirect('admin-products')
    return render(request,'admin_update_product.html',{'productForm':productForm})


@login_required(login_url='adminlogin')
def admin_view_booking_view(request):
    orders=models.Orders.objects.all()
    ordered_products=[]
    ordered_bys=[]
    time = []
    for order in orders:
        ordered_product=Food.objects.all().filter(id=order.food.id)
        ordered_by=Customer.objects.all().filter(id = order.customer.id)
        ordered_products.append(ordered_product)
        ordered_bys.append(ordered_by)

        if order.delivered_time:
        # if order.status == 'Delivered':
            delta = order.delivered_time - order.date_ordered
            t = str(delta)
            time.append(t)

        else:
            delta ="-"  
            time.append(delta) 
        total = len(ordered_products)
    return render(request,'admin_view_booking.html',{'data':zip(ordered_products,ordered_bys,orders,time),'count':total})


@login_required(login_url='adminlogin')
def delete_order_view(request,pk):
    order=Orders.objects.get(id=pk)
    order.delete()
    return redirect('admin-view-booking')
# import datetime as dt
# from datetime import datetime, timedelta
from datetime import datetime
# for changing status of order (pending,delivered...)
@login_required(login_url='adminlogin')
def update_order_view(request,pk):
    order=models.Orders.objects.get(id=pk)
    orderForm=forms.OrderForm(instance=order)
    if request.method=='POST':
        orderForm=forms.OrderForm(request.POST,instance=order)
        if orderForm.is_valid():
            orderForm.save()
        if str(order.status)=='Delivered':
            print("delivered")
            order.delivered_time = datetime.now()
        return redirect('admin-view-booking')
    return render(request,'update_order.html',{'orderForm':orderForm})


# admin view the feedback
@login_required(login_url='adminlogin')
def view_feedback_view(request):
    feedbacks=Feedback.objects.all().order_by('-id')
    return render(request,'view_feedback.html',{'feedbacks':feedbacks})

@login_required(login_url='adminlogin')
def select_food_view(request,name):    
    food = Food.objects.all().filter(f_name=str(name))[0]
    orders=models.Orders.objects.all().filter(food=food.id)
    ordered_products=[]
    ordered_bys=[]
    time = []
    for order in orders:
        # ordered_product=Food.objects.all().filter(id=order.food.id)
        ordered_product = Food.objects.all().filter(f_name=str(name))
        ordered_by=Customer.objects.all().filter(id = order.customer.id)
        ordered_products.append(ordered_product)
        ordered_bys.append(ordered_by)

        if order.delivered_time:
            delta = order.delivered_time - order.date_ordered 
            t = str(delta)
            time.append(t)

        else:
            delta ="-"  
            time.append(delta) 
    # print(ordered_products)
    total = len(ordered_products)
    return render(request,'admin_view_booking.html',{'data':zip(ordered_products,ordered_bys,orders,time),'name':name,'count':total})

@login_required(login_url='adminlogin')
def select_status_view(request,status):    
    orders=models.Orders.objects.all().filter(status=str(status))
    ordered_products=[]
    ordered_bys=[]
    count = 0
    time = []
    for order in orders:
        ordered_product=Food.objects.all().filter(id=order.food.id)
        ordered_by=Customer.objects.all().filter(id = order.customer.id)
        ordered_products.append(ordered_product)
        ordered_bys.append(ordered_by)
        

        if order.delivered_time:
            delta = order.delivered_time - order.date_ordered 
            t = str(delta)
            time.append(t)

        else:
            delta ="-"  
            time.append(delta) 
    count = len(set(ordered_products))
    print(count)
    return render(request,'admin_view_booking.html',{'data':zip(ordered_products,ordered_bys,orders,time),'count':count})

#---------------------------------------------------------------------------------
#------------------------ PUBLIC CUSTOMER RELATED VIEWS START ---------------------
#---------------------------------------------------------------------------------
def search_view(request):
    # whatever user write in search box we get in query
    query = request.GET['query']
    products=Food.objects.all().filter(f_name__icontains=query)
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0

    # word variable will be shown in html when user click on search button
    word="Searched Result for: "
    

    if request.user.is_authenticated:
        return render(request,'customer_home.html',{'products':products,'word':word,'product_count_in_cart':product_count_in_cart})
    return render(request,'index.html',{'products':products,'query':query,'word':word,'product_count_in_cart':product_count_in_cart})


# any one can add product to cart, no need of signin
def add_to_cart_view(request,pk):
    products=Food.objects.all()

    #for cart counter, fetching products ids added by customer from cookies
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=1

    response = render(request, 'index.html',{'products':products,'product_count_in_cart':product_count_in_cart})

    #adding product id to cookies
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids=="":
            product_ids=str(pk)
        else:
            product_ids=product_ids+"|"+str(pk)
        response.set_cookie('product_ids', product_ids)
    else:
        response.set_cookie('product_ids', pk)

    product=Food.objects.get(id=pk)
    messages.info(request, product.f_name + ' added to cart successfully!')
    return response

# for checkout of cart
def cart_view(request):
    #for cart counter
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0

    # fetching product details from db whose id is present in cookie
    products=None
    total=0
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_id_in_cart=product_ids.split('|')
            products=Food.objects.all().filter(id__in = product_id_in_cart)

            #for total price shown in cart
            for p in products:
                total=total+p.f_price
    return render(request,'cart.html',{'products':products,'total':total,'product_count_in_cart':product_count_in_cart})


def remove_from_cart_view(request,pk):
    #for counter in cart
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0

    # removing product id from cookie
    total=0
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        product_id_in_cart=product_ids.split('|')
        product_id_in_cart=list(set(product_id_in_cart))
        product_id_in_cart.remove(str(pk))
        products=Food.objects.all().filter(id__in = product_id_in_cart)
        #for total price shown in cart after removing product
        for p in products:
            total=total+p.f_price

        #  for update coookie value after removing product id in cart
        value=""
        for i in range(len(product_id_in_cart)):
            if i==0:
                value=value+product_id_in_cart[0]
            else:
                value=value+"|"+product_id_in_cart[i]
        response = render(request, 'cart.html',{'products':products,'total':total,'product_count_in_cart':product_count_in_cart})
        if value=="":
            response.delete_cookie('product_ids')
        response.set_cookie('product_ids',value)
        return response

def send_feedback_view(request):
    feedbackForm=forms.FeedbackForm()
    if request.method == 'POST':
        feedbackForm = forms.FeedbackForm(request.POST)
        if feedbackForm.is_valid():
            feedbackForm.save()
            return render(request, 'feedback_sent.html')
    return render(request, 'send_feedback.html', {'feedbackForm':feedbackForm})


#---------------------------------------------------------------------------------
#------------------------ CUSTOMER RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='customerlogin')
# @user_passes_test(is_customer)
def customer_home_view(request):
    products=models.Product.objects.all()
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0
    return render(request,'customer_home.html',{'products':products,'product_count_in_cart':product_count_in_cart})



# shipment address before placing order
@login_required(login_url='customerlogin')
def customer_address_view(request):
    product_in_cart=False
    # monthly = False
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_in_cart=True
    #for counter in cart
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0
    addressForm = forms.AddressForm()
    if request.method == 'POST':
        addressForm = forms.AddressForm(request.POST)
        if addressForm.is_valid():
            email = addressForm.cleaned_data['Email']
            mobile=addressForm.cleaned_data['Mobile']
            address = addressForm.cleaned_data['Address']
            expected_time = addressForm.cleaned_data['expected_time']
            monthly = addressForm.cleaned_data['monthly']
            shift = addressForm.cleaned_data['shift']
            #for showing total price on payment page.....accessing id from cookies then fetching  price of product from db
            total=0
            if 'product_ids' in request.COOKIES:
                product_ids = request.COOKIES['product_ids']
                if product_ids != "":
                    product_id_in_cart=product_ids.split('|')
                    products=models.Food.objects.all().filter(id__in = product_id_in_cart)
                    for p in products:
                        if monthly:
                            total=int(p.f_price)*30
                        total=total+p.f_price
            response = render(request, 'payment.html',{'total':total})
            response.set_cookie('monthly',monthly)
            response.set_cookie('email',email)
            response.set_cookie('mobile',mobile)
            response.set_cookie('address',address)
            response.set_cookie('expected_time',expected_time)
            response.set_cookie('shift',shift)
            return response
    return render(request,'customer_address.html',{'addressForm':addressForm,'product_in_cart':product_in_cart,'product_count_in_cart':product_count_in_cart})




# here we are just directing to this view...actually we have to check whther payment is successful or not
#then only this view should be accessed
@login_required(login_url='customerlogin')
def payment_success_view(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    products=None
    email=None
    mobile=None
    address=None
    shift = None
    expected_time = None
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_id_in_cart=product_ids.split('|')
            products=models.Food.objects.all().filter(id__in = product_id_in_cart)
            # Here we get products list that will be ordered by one customer at a time

    # these things can be change so accessing at the time of order...
    if 'monthly' in request.COOKIES:
        monthly = request.COOKIES['monthly']
    if 'email' in request.COOKIES:
        email=request.COOKIES['email']
    if 'mobile' in request.COOKIES:
        mobile=request.COOKIES['mobile']
    if 'address' in request.COOKIES:
        address=request.COOKIES['address']
    if 'shift' in request.COOKIES:
        shift=request.COOKIES['shift']
    if 'expected_time' in request.COOKIES:
        expected_time=request.COOKIES['expected_time']

    for product in products:
        if monthly == True:
            models.monthly_plan.objects.get_or_create(customer=customer,food=product,delivery_time=expected_time)        
               
                
        else:            
            models.Orders.objects.get_or_create(customer=customer,food=product,status='Pending',address=address,shift=shift,expected_time=expected_time)

    # after order placed cookies should be deleted
    response = render(request,'payment_success.html')
    response.delete_cookie('product_ids')
    response.delete_cookie('email')
    response.delete_cookie('mobile')
    response.delete_cookie('address')
    response.delete_cookie('shift')
    response.delete_cookie('expected_time')
    return response

@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def monthly_order_view(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    orders=models.monthly_plan.objects.all().filter(customer_id = customer)

    plan = []
    for order in orders:
        food = Food.objects.all().filter(id=order.food.id)
        plan.append(food)
    return render(request,'monthly_order.html',{'data':zip(plan, orders)})

from datetime import datetime, timedelta

@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def my_order_view(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    orders=models.Orders.objects.all().filter(customer_id = customer)
    ordered_products=[]
    time = []
    for order in orders:
        if order.delivered_time:
            delta = order.delivered_time - order.date_ordered 
            time.append(str(delta))

        else:
            delta ="-"  
            time.append(delta)     
        # time = iter(time)
        ordered_product=models.Food.objects.all().filter(id=order.food.id)
        ordered_products.append(ordered_product)
        # time=iter(list(delta))
    return render(request,'my_order.html',{'data':zip(ordered_products,orders,time),'time':time})

@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def cancel_order(request,pk):
    order = Orders.objects.get(id=pk)
    message = ""
    if order.status=='Out for Delivery':
        messages = 'Dear customer once the order is out on delivery it cannot be cancelled'
    else:
        order.delete()
        messages = str(order.food) + ' order successfully cancelled'   

    return redirect('my-order')

#--------------(pdf) download and printing
import io
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return

@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def download_invoice_view(request,orderID,productID):
    order=models.Orders.objects.get(id=orderID)
    product=models.Food.objects.get(id=productID)
    customer = Customer.objects.get(user=request.user)
    mydict={
        'orderDate':order.date_ordered,
        'customerName':customer.user.username,
        'expected_time':order.expected_time,
        'customerEmail': customer.c_email,
        'shift':order.shift,
        'shipmentAddress':order.address,
        'orderStatus':order.status,
        'customerMobile': customer.c_phone_number,
        'productName':product.f_name,
        'productImage':product.image,
        'productPrice':product.f_price,
        'productDescription':product.f_desc,


    }
    return render_to_pdf('download_invoice.html',mydict)

@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def my_profile_view(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    return render(request,'my_profile.html',{'customer':customer})


@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def edit_profile_view(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    user=models.User.objects.get(id=customer.user_id)
    userForm=forms.CustomerForm(instance=user)
    customerForm=forms.CustomerForm(request.FILES,instance=customer)
    mydict={'userForm':userForm,'customerForm':customerForm}
    if request.method=='POST':
        userForm=forms.CustomerForm(request.POST,instance=user)
        customerForm=forms.CustomerForm(request.POST,instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            return HttpResponseRedirect('my-profile')
    return render(request,'edit_profile.html',context=mydict)

#---------------------------------------------------------------------------------
#------------------------ ABOUT US AND CONTACT US VIEWS START --------------------
#---------------------------------------------------------------------------------
def aboutus_view(request):
    return render(request,'landing/index.html')
from collections import Counter
def index(request):
    feed = Feedback.objects.all()
    blogs = Blogs.objects.all()
    # ords = Orders.objects.all()
    # print(ords)


    # trending = Counter(list(ord))
    # for t in ord:
    #     trending.append(t.id)
    # print(trending,"...............................................")
    feed = {
        'feed':feed,
        'blogs':blogs
    }
    return render(request,'landing/index.html',context=feed)

def contactus_view(request):
    sub = forms.ContactusForm()
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name=sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            send_mail(str(name)+' || '+str(email),message, settings.EMAIL_HOST_USER, settings.EMAIL_RECEIVING_USER, fail_silently = False)
            return render(request, 'contactussuccess.html')
    return render(request, 'contactus.html', {'form':sub})
