from django.http import HttpResponse
from django.shortcuts import render, render_to_response
from django.contrib.auth import authenticate, login
from .forms import LoginForm, UserRegistrationForm
from django.contrib.auth.decorators import login_required
from rest_framework.authtoken.models import Token
import json

from kaas.tasks import task_driver

def index(request):
    template = 'kaas/index.html'
    return render(request, template)


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'],
                                password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
                    return HttpResponse('Disabled account')
                else:
                    return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'kaas/login.html', {'form': form})


@login_required
def dashboard(request):
    return render(request,
                  'kaas/dashboard.html',
                  {'section': 'dashboard'})


@login_required
def solve(request):
    from django.http import HttpResponseRedirect
    from django.shortcuts import render
    from .forms import UploadFileForm

    # Imaginary function to handle an uploaded file.
    #from somewhere import handle_uploaded_file

    token = Token.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            task_driver(json.loads(request.FILES['file'].read()), request.user)
            return HttpResponseRedirect('/dashboard/')
    else:
        form = UploadFileForm()
    return render(request, 'kaas/solve.html', {'token': token[0], 'section': 'solve', 'solve_form': form})





    #token = Token.objects.get_or_create(user=request.user)
    #return render(request,
    #              'kaas/solve.html',
    #              {'token': token[0], 'section': 'solve'})


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            # Set the chosen password
            new_user.set_password(
                    user_form.cleaned_data['password'])
            # Save the User object
            new_user.save()
            return render(request,
                          'kaas/register_done.html',
                          {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request,
                  'kaas/register.html',
                  {'user_form': user_form})
