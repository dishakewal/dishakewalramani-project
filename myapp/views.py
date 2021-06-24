from django.shortcuts import render,redirect
from .models import Contact,User,Blood,Wishlist,Cart,Transaction
from django.conf import settings
from django.core.mail import send_mail
from .paytm import generate_checksum, verify_checksum
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import random



def initiate_payment(request):
    
    try:
       	user=User.objects.get(email=request.session['email'])
        amount = int(request.POST['amount'])
        
    except:
        return render(request, 'pay.html', context={'error': 'Wrong Accound Details or amount'})

    transaction = Transaction.objects.create(made_by=user, amount=amount)
    transaction.save()
    merchant_key = settings.PAYTM_SECRET_KEY

    params = (
        ('MID', settings.PAYTM_MERCHANT_ID),
        ('ORDER_ID', str(transaction.order_id)),
        ('CUST_ID', str('dishakewalramani1211@gmail.com')),
        ('TXN_AMOUNT', str(transaction.amount)),
        ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
        ('WEBSITE', settings.PAYTM_WEBSITE),
        # ('EMAIL', request.user.email),
        # ('MOBILE_N0', '9911223388'),
        ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
        ('CALLBACK_URL', 'http://127.0.0.1:8000/callback/'),
        # ('PAYMENT_MODE_ONLY', 'NO'),
    )

    paytm_params = dict(params)
    checksum = generate_checksum(paytm_params, merchant_key)

    transaction.checksum = checksum
    transaction.save()

    paytm_params['CHECKSUMHASH'] = checksum
    print('SENT: ', checksum)
    return render(request, 'redirect.html', context=paytm_params)

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        received_data = dict(request.POST)
        paytm_params = {}
        paytm_checksum = received_data['CHECKSUMHASH'][0]
        for key, value in received_data.items():
            if key == 'CHECKSUMHASH':
                paytm_checksum = value[0]
            else:
                paytm_params[key] = str(value[0])
        # Verify checksum
        is_valid_checksum = verify_checksum(paytm_params, settings.PAYTM_SECRET_KEY, str(paytm_checksum))
        if is_valid_checksum:
            received_data['message'] = "Checksum Matched"
        else:
            received_data['message'] = "Checksum Mismatched"
            return render(request, 'callback.html', context=received_data)
        return render(request, 'callback.html', context=received_data)


# Create your views here.
def home(request):
	return render(request,'home.html')

def about(request):
	return render(request,'about.html')

def contact(request):
	if request.method=="POST":
		Contact.objects.create(
			name=request.POST['name'],
			email=request.POST['email'],
			mobile=request.POST['mobile'],
			remarks=request.POST['remarks']
			)
		msg="Contact Saved Successfully!!"
		return render(request,"contact.html",{msg:'msg'})
	else:
		return render(request,"contact.html")

def signup(request):
	if request.method=="POST":
		try:
			user=User.objects.get(email=request.POST['email'])
			msg="User already Registered!!"
			return render(request,"signup.html",{msg:'msg'})
		except:
			if request.POST['password']==request.POST['cpassword']:
				User.objects.create(
					firstname=request.POST['firstname'],
					lastname=request.POST['lastname'],
					email=request.POST['email'],
					mobile=request.POST['mobile'],
					gender=request.POST['gender'],
					address=request.POST['address'],
					password=request.POST['password'],
					cpassword=request.POST['cpassword'],
					image=request.FILES['image'],
					usertype=request.POST['usertype']
					)
				msg="Signup Successfully!!"
				return render(request,"home.html",{msg:'msg'})
			else:
				msg="Incorrect password!!"
				return render(request,"signup.html",{msg:'msg'})

	else:
		return render(request,"signup.html")

def login(request):
	if request.method=="POST":
		try:
			user=User.objects.get(
				email=request.POST['email'],
				password=request.POST['password']
				)
			if user.usertype=="user":
				request.session['email']=user.email
				request.session['firstname']=user.firstname
				request.session['image']=user.image.url
				return render(request,"home.html")
			elif user.usertype=="seller":
				request.session['email']=user.email
				request.session['firstname']=user.firstname
				request.session['image']=user.image.url
				return render(request,"sellerhome.html")

		except Exception as e:
			print("Exception : --------------------------------------",e)
			msg="email and password are incorrect"
			return render(request,"login.html",{'msg':msg})
	else:

		return render(request,"login.html")

def logout(request):
	try:
		del request.session['email']
		del request.session['firstname']
		del request.session['image']
		return render(request,'login.html')
	except:
		return redirect("logout")

def  Userupdateprofile(request):
		user=User.objects.get(email=request.session['email'])
		if request.method=="POST":
			user.firstname=request.POST['firstname']
			user.lastname=request.POST['lastname']
			user.email=request.POST['email']
			user.mobile=request.POST['mobile']
			user.gender=request.POST['gender']
			user.address=request.POST['address']
			user.password=request.POST['password']
			user.cpassword=request.POST['cpassword']
			try:
				user.image=request.FILES['image']
				user.save()
			except:
				pass
			user.save()
			msg="Update Successfully!!"
			return render(request,"Userupdateprofile.html",{'msg':msg})
		else:
			
			return render(request,"Userupdateprofile.html",{"user":user})	


def forgot_passwd(request):
	if request.method=='POST':
		try:
			subject = 'otp for registration!!'
			otp=random.randint(1000,9999)
			message = 'hi user, your otp is: '+str(otp)
			email_from = settings.EMAIL_HOST_USER
			recipient_list = [request.POST['email'], ]
			send_mail( subject, message, email_from, recipient_list )
			return render(request,"otp.html",{'otp':otp,'email':request.POST['email']})
		except:
			msg="email doesnt match!!"
			return render(request,"forgot_passwd.html",{"msg":msg})
	else:
		return render(request,"forgot_passwd.html")

def otp(request):
		otp1=request.POST['otp1']
		otp2=request.POST['otp2']
		email=request.POST['email']

		if otp1==otp2:
			user=User.objects.get(email=email)
			user.status="active"
			user.save()
			msg="otp verified successfully!!"
			return render(request,'new_password.html',{'msg':msg,'email':email})
		else:
			msg="invalid otp"
			return render(request,"otp.html",{'otp':otp1,'email':request.POST['email'], 'msg':msg})

def new_password(request):
	email=request.POST['email']
	npassword=request.POST['npassword']
	cnewpassword=request.POST['cnewpassword']

	user=User.objects.get(email=email)

	if npassword==cnewpassword:
		user.password=npassword
		user.cnewpassword=npassword
		user.save()
		msg="password change successfully"
		return render(request,"login.html",{"msg":msg})
	else:
		msg="password doeasnt match"
		return render(request,"new_password.html",{"msg":msg})
	return render(request,"new_password.html")

def change_password(request):
	if request.method=="POST":
		user=User.objects.get(email=request.session['email'])


		if user.password==request.POST['oldpassword']:
			if request.POST['newpassword']==request.POST['cnpassword']:
				user.password=request.POST['newpassword']
				user.cnpassword=request.POST['newpassword']
				user.save()
				return redirect('logout')
			else: 
				msg="password dosent match"
				return render (request,'change_password.html',{'msg':msg})	
		else:
			msg="old password inncorrect"
			return render (request,'change_password.html',{'msg':msg})
	else:
		return render (request,'change_password.html')


def sellerhome(request):
	return render(request,"sellerhome.html")


def sellersignup(request):
	if request.method=="POST":
		try:
			user=User.objects.get(email=request.POST['email'])
			msg="User already Registered!!"
			return render(request,"signup.html",{msg:'msg'})
		except:
			if request.POST['password']==request.POST['cpassword']:
				User.objects.create(
					firstname=request.POST['firstname'],
					lastname=request.POST['lastname'],
					email=request.POST['email'],
					mobile=request.POST['mobile'],
					gender=request.POST['gender'],
					address=request.POST['address'],
					password=request.POST['password'],
					cpassword=request.POST['cpassword'],
					image=request.FILES['image'],
					usertype=request.POST['usertype']
					)
				msg="Signup Successfully!!"
				return render(request,"login.html",{msg:'msg'})
			else:
				msg="Incorrect password!!"
				return render(request,"sellersignup.html",{msg:'msg'})

	else:
		return render(request,"sellersignup.html")


def sellerprofile(request):
	user=User.objects.get(email=request.session['email'])
	if request.method=="POST":
		user.firstname=request.POST['firstname']
		user.lastname=request.POST['lastname']
		user.email=request.POST['email']
		user.mobile=request.POST['mobile']
		user.gender=request.POST['gender']
		user.address=request.POST['address']
		user.password=request.POST['password']
		user.cpassword=request.POST['cpassword']
		try:
			user.image=request.FILES['image']
			user.save()
		except:
			pass
		user.save()
		return render(request,"sellerprofile.html")
	else:

		return render(request,"sellerprofile.html",{"user":user})

def sellerchange_password(request):
	if request.method=="POST":
		user=User.objects.get(email=request.session['email'])

		if user.password==request.POST['oldpassword']:
			if request.POST['newpassword']==request.POST['cnpassword']:
				user.password=request.POST['newpassword']
				user.cnpassword=request.POST['newpassword']
				user.save()
				return redirect('logout')

			else: 
				msg="password dosent match"
				return render (request,'sellerchange_password.html',{'msg':msg})	
		else:
			msg="old password inncorrect"
			return render (request,'sellerchange_password.html',{'msg':msg})
	else:
		return render (request,'sellerchange_password.html')

def seller_addetails(request):
	if request.method=="POST":
		seller=User.objects.get(email=request.session['email'])
		Blood.objects.create(
				seller=seller,
				blood_bank=request.POST['blood_bank'],
				blood_group=request.POST['blood_group'],
				blood_description=request.POST['blood_description'],
				blood_price=request.POST['blood_price'],
				blood_quantity=request.POST['blood_quantity'],
				blood_image=request.FILES['blood_image']
			)
		msg="Added Successfully!!"
		return render(request,"seller_addetails.html",{'msg':msg})
	else:

		return render(request,"seller_addetails.html")

def seller_viewdetails(request):
	seller=User.objects.get(email=request.session['email'])
	blood=Blood.objects.filter(seller=seller)
	return render(request,"seller_viewdetails.html",{'blood':blood})


def seller_moredetails(request,pk):
	blood=Blood.objects.get(pk=pk)
	return render(request,"seller_moredetails.html",{'blood':blood})

def seller_Editdetails(request,pk):
	blood=Blood.objects.get(pk=pk)

	if request.method=="POST":
		blood.blood_group=request.POST['blood_group']
		blood.blood_price=request.POST['blood_price']
		blood.blood_quantity=request.POST['blood_quantity']
		blood.blood_description=request.POST['blood_description']

		try:
			blood.blood_image=request.FILES['blood_image']
			blood.save()
		except:
			pass
		blood.save()		
		return redirect("seller_viewdetails")
	else:
		return render(request,"seller_Editdetails.html",{'blood':blood})


def seller_Deletedetails(request,pk):
	blood=Blood.objects.get(pk=pk)
	blood.delete()
	return redirect("seller_viewdetails")

def Blood_bank(request):
	return render(request,"Blood_bank.html")

def user_view_all_details(request,bb):
	if bb=='All':
		blood=Blood.objects.all()
		return render (request,'user_view_all_details.html',{'blood':blood})
	else:
		blood=Blood.objects.filter(blood_bank=bb)
		return render (request,'user_view_all_details.html',{'blood':blood})

def user_moredetails(request,pk):
	flag=False
	flag1=False
	blood=Blood.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])

	try:
		Wishlist.objects.get(user=user,blood=blood)
		flag=True
	except:
		pass

	try:
		Cart.objects.get(user=user,blood=blood,payment_status="pending")
		flag1=True
	except:
		pass
	return render (request,'user_moredetails.html',{'blood':blood, 'flag':flag , 'flag1':flag1})

def add_to_wishlist(request,pk):
	blood=Blood.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	Wishlist.objects.create(user=user,blood=blood)
	return redirect('mywishlist')

def mywishlist(request):
	user=User.objects.get(email=request.session['email'])
	wishlist=Wishlist.objects.filter(user=user)
	request.session['wishlist_count']=len(wishlist)
	return render(request,'mywishlist.html',{'wishlist':wishlist})

def remove_from_wishlist(request,pk):
	blood=Blood.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	wishlist=Wishlist.objects.get(user=user,blood=blood)
	wishlist.delete()
	return redirect('mywishlist')

def  add_to_cart(request,pk):
	blood=Blood.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	Cart.objects.create(user=user,blood=blood,price=blood.blood_price,total_price=blood.blood_price)
	return redirect('mycart')

def mycart(request):
	net_price=0
	user=User.objects.get(email=request.session['email'])
	cart=Cart.objects.filter(user=user,payment_status="pending")
	for i in cart:
		net_price=net_price+i.total_price
	request.session['cart_count']=len(cart)
	return render(request,'mycart.html',{'cart':cart,'net_price':net_price})

def remove_from_cart(request,pk):
	blood=Blood.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	cart=Cart.objects.get(user=user,blood=blood)
	cart.delete()
	return redirect('mycart')


def change_qty(request,pk):
	cart=Cart.objects.get(pk=pk)
	qty=int(request.POST['qty'])
	if qty<=3:
		cart.qty=qty
		cart.total_price=qty*cart.price
		cart.save()
		return redirect('mycart')
	else:
		msg="you can purchase only 3"
		return render(request,'mycart.html',{'msg':msg})
