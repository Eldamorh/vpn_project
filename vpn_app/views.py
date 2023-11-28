import re

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import requests
from .models import Site, Statistics
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .forms import ProfileForm
from django.db import transaction


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if form.is_valid() and profile_form.is_valid():
            with transaction.atomic():  # Ensures both user and profile are created together
                user = form.save()
                profile = profile_form.save(commit=False)
                profile.user = user
                profile.save()
                login(request, user)
                return redirect('dashboard')
    else:
        form = UserCreationForm()
        profile_form = ProfileForm()

    return render(request, 'register.html', {'form': form, 'profile_form': profile_form})


def update_user_view(request):
    user = request.user
    profile = user.profile if hasattr(user, 'profile') else None

    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, instance=profile) if profile else None

        if profile_form and profile_form.is_valid():
            profile_obj = profile_form.save(commit=False)
            profile_obj.user = user
            profile_obj.save()
            return redirect('dashboard')  # Redirect to dashboard or another page
    else:
        profile_form = ProfileForm(instance=profile) if profile else None

    return render(request, 'update_user.html', {'profile_form': profile_form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


@login_required
def dashboard_view(request):
    user = request.user
    profile = user.profile if hasattr(user, 'profile') else None
    statistics, created = Statistics.objects.get_or_create(user=user)
    sites = Site.objects.filter(user=user)

    return render(request, 'dashboard.html', {'user': user, 'statistics': statistics, 'sites': sites, 'profile': profile})


@login_required
def create_site_view(request):
    if request.method == 'POST':
        name = request.POST['name']
        url = request.POST['url']
        site = Site.objects.create(user=request.user, name=name, url=url)
        return redirect('dashboard')
    return render(request, 'create_site.html')


@login_required
def proxy_view(request, user_site_name, routes_on_original_site):
    site = Site.objects.get(user=request.user, name=user_site_name)
    url = urljoin(site.url, routes_on_original_site)

    sent_data = len(request.body) if request.body else 0
    response = requests.get(url)
    received_data = len(response.content)

    sent_megabytes = sent_data / (1024 * 1024)
    received_megabytes = received_data / (1024 * 1024)

    statistics = Statistics.objects.get(user=request.user)
    statistics.page_transitions += 1
    statistics.data_sent += sent_megabytes
    statistics.data_received += received_megabytes
    statistics.save()

    soup = BeautifulSoup(response.content, 'html.parser')
    for tag in soup.find_all(['a', 'img', 'link', 'script']):
        if tag.name == 'a' and tag.get('href') and (
                not tag.get('href').startswith('http') or tag.get('href').startswith(site.url)):
            if tag.get('href').startswith(site.url):
                tag['href'] = f'http://localhost:8000/{user_site_name}{tag["href"].replace(site.url, "")}'
            if not tag.get('href').startswith('http'):
                tag['href'] = f'http://localhost:8000/{user_site_name}{tag["href"]}'
        elif tag.name == 'img':
            if tag.get('src') and not tag.get('src').startswith('http'):
                tag['src'] = f'{site.url}{tag["src"]}'
            elif tag.get('data-src') and not tag.get('data-src').startswith('http'):
                tag['data-src'] = f'{site.url}{tag["data-src"]}'
        elif tag.name == 'link' and tag.get('href') and not tag.get('href').startswith('http'):
            tag['href'] = f'{site.url}{tag["href"]}'
        elif tag.name == 'script' and tag.get('src') and not tag.get('src').startswith('http'):
            tag['src'] = f'{site.url}{tag["src"]}'
    return HttpResponse(str(soup))
