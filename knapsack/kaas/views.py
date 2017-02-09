from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from rest_framework.authtoken.models import Token
from .forms import LoginForm, UserRegistrationForm
from .forms import KnapsakTextArea
import json

from kaas.tasks import task_driver
from kaas.models import KnapsackTask

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
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'kaas/login.html', {'form': form})


@login_required
def dashboard(request):
    tasks = KnapsackTask.objects.filter(user=request.user)[:100]
    return render(request,
                  'kaas/dashboard.html',
                  {'section': 'dashboard',
                   'tasks': tasks})


@login_required
def solve(request):
    token = Token.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = KnapsakTextArea(request.POST)
        if form.is_valid():
            task_driver(json.loads(form.cleaned_data['knapsack_json']), request.user)
            #return HttpResponseRedirect('/dashboard/')
            data = {'token': token[0],
                    'section': 'solve',
                    'solve_form': form,
                    'solve_message': "Task has been submitted! You can chech its progress and results on the Dashboard",
                    'active2': "active",
                    'activec2': "active"}
            return render(request, 'kaas/solve.html', data)
        else:
            data = {'token': token[0],
                    'section': 'solve',
                    'solve_form': form,
                    'active2': "active",
                    'activec2': "active"}
            return render(request, 'kaas/solve.html', data)
    else:
        form = KnapsakTextArea()

    data = {'token': token[0],
            'section': 'solve',
            'solve_form': form,
            'active1': "active",
            'activec1': "active"}
    return render(request, 'kaas/solve.html', data)


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
