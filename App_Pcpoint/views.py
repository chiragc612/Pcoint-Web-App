from django.shortcuts import render, redirect
from django.conf import settings
from django.core.mail import send_mail
import random
from .models import AddProduct, Carts, Contact, Signup, Wishlists, Transaction
from .paytm import generate_checksum, verify_checksum
from django.views.decorators.csrf import csrf_exempt

# Create your views here.


def index(request):
    return render(request, "index.html")


def contact(request):
    if(request.method == "POST"):
        Contact.objects.create(
            name=request.POST["name"],
            phonenumber=request.POST["phonenumber"],
            email=request.POST["email"],
            message=request.POST["message"],
        )
        message = "Contact Saved Successfully."
        return render(request, "contact.html", {"message": message})
    else:
        return render(request, "contact.html")


def signIn(request):
    if(request.method == 'POST'):
        try:
            user = Signup.objects.get(
                email=request.POST['email'],
                password=request.POST['password']
            )
            if user.usertype == "customer":
                request.session['usertype'] = user.usertype
                request.session['email'] = user.email
                request.session['name'] = user.name
                wishlists = Wishlists.objects.filter(user=user)
                request.session['wishlists_count'] = len(wishlists)
                carts = Carts.objects.filter(user=user, status=False)
                request.session['carts_count'] = len(carts)
                return render(request, 'index.html')
            else:
                request.session['usertype'] = user.usertype
                request.session['email'] = user.email
                request.session['name'] = user.name
                return render(request, 'index.html')
        except:
            message = "Email and Password is Incorrect."
            return render(request, "signIn.html", {"message": message})
    else:
        return render(request, "signIn.html")


def changepassword(request):
    if(request.method == "POST"):
        user = Signup.objects.get(email=request.session['email'])
        if(user.password == request.POST['oldpassword']):
            if(request.POST['newpassword'] == request.POST['cnewpassword']):
                user.password = request.POST['newpassword']
                user.save()
                return redirect('logout')
            else:
                message = "New Password and Confirm New Password Does Not Match."
                return render(request, 'changepassword.html', {'message': message})
        else:
            message = "Incorrect Old Password."
            return render(request, 'changepassword.html', {'message': message})
    else:
        return render(request, "changepassword.html")


def logout(request):
    try:
        del request.session["email"]
        del request.session["name"]
        del request.session["usertype"]
        return render(request, "signIn.html")
    except:
        return render(request, "index.html")


def signUp(request):
    if(request.method == "POST"):
        try:
            Signup.objects.get(email=request.POST["email"])
            message = "Email has already registered."
            return render(request, "signUp.html", {"message": message})
        except:
            if(request.POST["name"] != "" and request.POST["email"] != "" and request.POST["password"] != "" and request.POST["cpassword"] != "" and request.POST["password"] == request.POST["cpassword"] or request.POST["phonenumber"] != ""):
                Signup.objects.create(
                    name=request.POST["name"],
                    phonenumber=request.POST["phonenumber"],
                    email=request.POST["email"],
                    password=request.POST["password"],
                    usertype=request.POST["usertype"],
                )
                message = "User Signup Successfully."
                return render(request, "signIn.html", {"message": message})
            else:
                message = "All fields are required"
                return render(request, "signUp.html", {"message": message})
    else:
        return render(request, "signUp.html")


def forgotPassword(request):
    if(request.method == "POST"):
        try:
            user = Signup.objects.get(email=request.POST['email'])
            subject = 'OTP for Forgot Password.'
            otp = random.randint(1000, 9999)
            message = 'OTP for Forgot Password is ' + str(otp)
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user.email, ]
            send_mail(subject, message, email_from, recipient_list)
            return render(request, 'otp.html', {'otp': otp, 'email': user.email})
        except:
            message = "Email Does Not Exists."
            return render(request, "forgotPassword.html", {'message': message})
    else:
        return render(request, "forgotPassword.html")


def verifyotp(request):
    otp = request.POST['otp']
    uotp = request.POST['uotp']
    email = request.POST['email']

    if(otp == uotp):
        return render(request, 'newpassword.html', {"email": email})
    else:
        message = "Invalid OTP."
        return render(request, 'otp.html', {'otp': otp, 'email': email, 'message': message})


def newpassword(request):
    email = request.POST['email']
    newpassword = request.POST['newpassword']
    cnewpassword = request.POST['cnewpassword']

    if(newpassword == cnewpassword):
        user = Signup.objects.get(email=email)
        user.password = newpassword
        user.save()
        message = "Password Changed Successfully."
        return render(request, 'signIn.html', {'message': message})
    else:
        message = "New Password and Confirm New Password Does Not Matched."
        return render(request, 'newpassword.html', {'email': email, 'message': message})


def addproduct(request):
    if(request.method == "POST"):
        seller = Signup.objects.get(email=request.session['email'])

        AddProduct.objects.create(
            seller=seller,
            producttype=request.POST["producttype"],
            productname=request.POST["productname"],
            price=request.POST["price"],
            description=request.POST["description"],
            file=request.FILES["file"]
        )
        message = "Product Added Successfully."
        return render(request, "addproduct.html", {"message": message})
    else:
        return render(request, 'addproduct.html')


def viewproducts(request):
    seller = Signup.objects.get(email=request.session['email'])
    products = AddProduct.objects.filter(seller=seller)
    return render(request, 'viewproducts.html', {'products': products})


def editproduct(request, pk):
    product = AddProduct.objects.get(pk=pk)
    if(request.method == "POST"):
        product.producttype = request.POST['producttype']
        product.productname = request.POST['productname']
        product.price = request.POST['price']
        product.description = request.POST['description']
        try:
            product.file = request.FILES['file']
        except:
            pass
        product.save()
        message = "Product Updated Successfully."
        return render(request, "editproduct.html", {'product': product, 'message': message})
    else:
        return render(request, "editproduct.html", {'product': product})


def deleteproduct(request, pk):
    product = AddProduct.objects.get(pk=pk)
    product.delete()
    return redirect("viewproducts")


def products(request):
    products = AddProduct.objects.all()
    return render(request, 'products.html', {"products": products})


def details(request, pk):
    product = AddProduct.objects.get(pk=pk)
    return render(request, "details.html", {'product': product})


def addToWishlists(request, pk):
    product = AddProduct.objects.get(pk=pk)
    user = Signup.objects.get(email=request.session['email'])
    Wishlists.objects.create(
        user=user,
        product=product
    )
    return redirect('wishlists')


def wishlists(request):
    user = Signup.objects.get(email=request.session['email'])
    wishlists = Wishlists.objects.filter(user=user)
    request.session['wishlists_count'] = len(wishlists)
    return render(request, 'wishlists.html', {'wishlists': wishlists})


def remove(request, pk):
    product = AddProduct.objects.get(pk=pk)
    user = Signup.objects.get(email=request.session['email'])
    wishlist = Wishlists.objects.filter(user=user, product=product)
    wishlist.delete()
    return redirect('wishlists')


def removeFromCart(request, pk):
    product = AddProduct.objects.get(pk=pk)
    user = Signup.objects.get(email=request.session['email'])
    cart = Carts.objects.filter(user=user, product=product, status=False)
    cart.delete()
    return redirect('carts')


def addToCarts(request, pk):
    product = AddProduct.objects.get(pk=pk)
    user = Signup.objects.get(email=request.session['email'])
    Carts.objects.create(
        user=user,
        product=product,
        price=product.price,
        totalprice=product.price
    )
    return redirect('carts')


def carts(request):
    netPrice = 0
    user = Signup.objects.get(email=request.session['email'])
    carts = Carts.objects.filter(user=user, status=False)
    for i in carts:
        netPrice = netPrice+i.totalprice
    request.session['carts_count'] = len(carts)
    return render(request, 'carts.html', {'carts': carts, 'netPrice': netPrice})


def changeQty(request):
    cid = request.POST['cid']
    productQty = request.POST['productQty']
    cart = Carts.objects.get(pk=cid, status=False)
    cart.qty = productQty
    cart.totalprice = int(productQty)*int(cart.price)
    cart.save()
    return redirect('carts')


def initiate_payment(request):
    user = Signup.objects.get(email=request.session['email'])
    try:
        amount = int(request.POST['amount'])
    except:
        return render(request, 'carts.html', context={'error': 'Wrong Accound Details or amount'})

    transaction = Transaction.objects.create(made_by=user, amount=amount)
    transaction.save()
    merchant_key = settings.PAYTM_SECRET_KEY

    params = (
        ('MID', settings.PAYTM_MERCHANT_ID),
        ('ORDER_ID', str(transaction.order_id)),
        ('CUST_ID', str(transaction.made_by.email)),
        ('TXN_AMOUNT', str(transaction.amount)),
        ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
        ('WEBSITE', settings.PAYTM_WEBSITE),
        # ('EMAIL', request.user.email),
        # ('MOBILE_N0', '9911223388'),
        ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
        ('CALLBACK_URL', 'http://localhost:8000/callback/'),
        # ('PAYMENT_MODE_ONLY', 'NO'),
    )

    paytm_params = dict(params)
    checksum = generate_checksum(paytm_params, merchant_key)

    transaction.checksum = checksum
    transaction.save()
    carts = Carts.objects.filter(user=user)
    for i in carts:
        i.status = True
        i.save()
    carts = Carts.objects.filter(user=user, status=False)
    request.session['carts_count'] = len(carts)
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
        is_valid_checksum = verify_checksum(
            paytm_params, settings.PAYTM_SECRET_KEY, str(paytm_checksum))
        if is_valid_checksum:
            received_data['message'] = "Checksum Matched"
        else:
            received_data['message'] = "Checksum Mismatched"
            return render(request, 'callback.html', context=received_data)
        return render(request, 'callback.html', context=received_data)


def myorders(request):
    # netPrice = 0
    user = Signup.objects.get(email=request.session['email'])
    carts = Carts.objects.filter(user=user, status=True)
    # for i in carts:
        # netPrice = netPrice+i.totalprice
    #request.session['carts_count'] = len(carts)
    return render(request, 'myorders.html', {'carts': carts,})
