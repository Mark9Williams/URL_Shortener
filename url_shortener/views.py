# shortener/views.py
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q, F
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseGone


from .forms import URLForm
from .models import ShortURL




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


def redirect_code(request, code):
    obj = ShortURL.objects.filter(Q(short_code=code) | Q(custom_code=code)).first()
    if not obj:
        return render(request, 'shortener/not_found.html', status=404)
    if obj.is_expired():
        return HttpResponseGone('This link has expired.')


    # Atomic increment
    ShortURL.objects.filter(pk=obj.pk).update(click_count=F('click_count') + 1)


    return redirect(obj.original_url)




@login_required
def analytics(request):
    links = ShortURL.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shortener/analytics.html', {'links': links})




def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def link_analytics(request):
    # Get at most 20 records, ordered by creation date (latest first)
    urls = ShortURL.objects.all().order_by('-created_at')[:20]

    context = {
        'urls': urls
    }
    return render(request, 'url_shortener/analytics.html', context)