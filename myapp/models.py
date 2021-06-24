from django.db import models
from django.utils import timezone
# Create your models here.
class Contact(models.Model):
	name=models.CharField(max_length=100)
	email=models.CharField(max_length=100)
	mobile=models.CharField(max_length=100)
	remarks=models.TextField()

	def __str__(self):
		return self.name

class User(models.Model):
	firstname=models.CharField(max_length=100)
	lastname=models.CharField(max_length=100)
	email=models.CharField(max_length=100)
	mobile=models.CharField(max_length=100)
	address=models.TextField()
	gender=models.CharField(max_length=100)
	password=models.CharField(max_length=100)
	cpassword=models.CharField(max_length=100)
	image=models.ImageField(upload_to="images/",default="",blank=True,null=True)
	status=models.CharField(max_length=100, default="inactive")
	usertype=models.CharField(max_length=100,default="user")

	def __str__(self):
		return self.firstname+"-"+self.lastname

class Blood(models.Model):
	CHOICES=(
		('Supratech Blood Bank,Thaltej','Supratech Blood Bank,Thaltej'),
		('Indian Blood Service , Ellisbridge','Indian Blood Service , Ellisbridge'),
	
	)

	seller=models.ForeignKey(User,on_delete=models.CASCADE)
	blood_bank=models.CharField(max_length=100,choices=CHOICES)
	blood_group=models.CharField(max_length=100)
	blood_price=models.IntegerField()
	blood_quantity=models.IntegerField()
	blood_description=models.TextField()
	blood_image=models.ImageField(upload_to="blood_images/")

	def __str__(self):
		return self.seller.firstname+" - "+self.blood_group

class Wishlist(models.Model):
	user=models.ForeignKey(User,on_delete=models.CASCADE)
	blood=models.ForeignKey(Blood,on_delete=models.CASCADE)
	date=models.DateTimeField(default=timezone.now)

	def __str__(self):
		return self.user.firstname+" - "+self.blood.blood_group	

class Cart(models.Model):
	user=models.ForeignKey(User,on_delete=models.CASCADE)
	blood=models.ForeignKey(Blood,on_delete=models.CASCADE)
	date=models.DateTimeField(default=timezone.now)
	qty=models.IntegerField(default=1)
	price=models.IntegerField()
	total_price=models.IntegerField()
	payment_status=models.CharField(max_length=100,default="pending")


class Transaction(models.Model):
    made_by = models.ForeignKey(User, related_name='transactions', 
                                on_delete=models.CASCADE)
    made_on = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField()
    order_id = models.CharField(unique=True, max_length=100, null=True, blank=True)
    checksum = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.order_id is None and self.made_on and self.id:
            self.order_id = self.made_on.strftime('PAY2ME%Y%m%dODR') + str(self.id)
        return super().save(*args, **kwargs)