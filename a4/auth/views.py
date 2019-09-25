from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from .forms import RegistrationForm, SigninForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@sensitive_post_parameters()
def register(request):
    """View for registering new users, accepts GET and POST"""
    if request.method == "POST":
        post = request.POST
        form = RegistrationForm(post)
        if not form.is_valid():
            return HttpResponse("Invalid registration request", status=400)
        if not post["password"] == post["passwordconf"]:
            return HttpResponse("Passwords do not match", status=400)
        user = User.objects.create_user(username=form.cleaned_data['username'],
                                email=form.cleaned_data['email'],
                                password=form.cleaned_data['password'],
                                first_name=form.cleaned_data['first_name'],
                                last_name=form.cleaned_data['last_name'])
        user.save()
        return HttpResponseRedirect("/auth/signin")
    elif request.method == "GET":
        form = RegistrationForm()
        return render(request, "auth/register.html", {'form': form}, status=200)
    else:
        return HttpResponse("Method not allowed on auth/register", status=405)

@csrf_exempt
@sensitive_post_parameters()
def signin(request):
    """View for signing in users, accepts GET and POST"""
    if request.method == "POST":
        form = SigninForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect("/")
            return HttpResponse("Invalid Credentials", status=401)
        else:
            return HttpResponse("Bad login form", status=400)
    elif request.method == "GET":
        form = SigninForm()
        return render(request, "auth/signin.html", {'form': form}, status=200)
    return HttpResponse("Method not allowed on auth/signin", status=405)

@csrf_exempt
def signout(request):
    """View for signing out users, accepts GET"""
    if request.method == "GET":
        if request.user.is_authenticated:
            logout(request)
            return HttpResponseRedirect("/auth/signin")
        return HttpResponse("Not logged in", status=200)
    return HttpResponse("Method not allowed on auth/signout", status=405)
