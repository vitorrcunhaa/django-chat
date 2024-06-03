from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib import messages


def user_signup(request):
    if request.method == 'POST':
        email = request.POST['user_email']
        username = request.POST['user_username']
        password = request.POST['user_password']
        user_model = get_user_model()

        if not username.strip():
            messages.error(request, 'Something is wrong.')
            return render(request, 'app_users/signup.html')

        if user_model.objects.filter(email=email).exists():
            messages.error(request, 'Something is wrong.')
            return render(request, 'app_users/signup.html')

        user_obj = user_model.objects.create_user(email=email, password=password)
        user_obj.set_password(password)
        user_obj.username = username
        user_obj.save()
        user_auth = authenticate(username=email, password=password)

        if user_auth:
            login(request, user_auth)
            return redirect('home')
    return render(request, 'signup.html')


def user_login(request):
    if request.method == 'POST':
        email = request.POST['user_email']
        password = request.POST['user_password']
        try:
            user_auth = authenticate(username=email, password=password)
            login(request, user_auth)
            return redirect('home')
        except:
            messages.error(request, 'Something is wrong.')
            return render(request, 'login.html')
    else:
        return render(request, 'login.html')


def user_logout(request):
    try:
        logout(request)
    except:
        messages.error(request, 'Something is wrong.')
    return redirect('login')
