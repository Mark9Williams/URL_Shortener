# shortener/views.py
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q, F
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.http import HttpResponseGone


from .forms import URLForm
from .models import ShortURL



@login_required
def home(request):
    form = URLForm()
    if request.method == 'POST':
        form = URLForm(request.POST)
        print('Hello! This is the information in the form')
        print(form)
        if form.is_valid():
            obj = form.save(commit=False)
            if request.user.is_authenticated:
                obj.user = request.user
            obj.clean()
            obj.save()
            short_url = obj.get_absolute_short_url(request)
            return render(request, 'url_shortener/success.html', {
                'short_url': short_url,
                'obj': obj,
            })
    return render(request, 'url_shortener/home.html', {'form': form})


@login_required
def redirect_code(request, code):
    obj = ShortURL.objects.filter(Q(short_code=code) | Q(custom_code=code), user=request.user).first()
    if not obj:
        messages.warning(request, "⚠️ This short link does not exist in your current links.")
        return redirect('home')
    if obj.is_expired():
        messages.warning(request, "⏳ This link has expired.")
        return redirect('home')


    # Atomic increment
    ShortURL.objects.filter(pk=obj.pk).update(click_count=F('click_count') + 1)


    return redirect(obj.original_url)
    

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your account was created successfully!")
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def link_analytics(request):
    query = request.GET.get("q")
    if query:
        urls = ShortURL.objects.filter(short_code__iexact=query, user=request.user) | ShortURL.objects.filter(custom_code__iexact=query, user=request.user)
    else:
        urls = ShortURL.objects.filter(user=request.user).order_by('-click_count')[:20]

    return render(request, "url_shortener/analytics.html", {"urls": urls})
