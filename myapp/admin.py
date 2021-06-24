from django.contrib import admin
from .models import Contact,User,Blood,Wishlist,Cart,Transaction

# Register your models here.
admin.site.register(Contact)
admin.site.register(User)
admin.site.register(Blood)
admin.site.register(Wishlist)
admin.site.register(Cart)
admin.site.register(Transaction)