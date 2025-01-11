from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .forms import *
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from .models import *
from django.contrib.auth.decorators import login_required

# Create your views here.
def service_list(request):
    latitude = request.GET.get('latitude')
    longitude = request.GET.get('longitude')
    services = Service.objects.all()

    if latitude and longitude:
        try:
            latitude = float(latitude)
            longitude = float(longitude)
            
            # Haversine formula to calculate distance in kilometers
            services = services.annotate(
                distance=Value(6371, output_field=FloatField()) * 
                ACos(
                    Cos(Radians(latitude)) * Cos(Radians(F('latitude'))) *
                    Cos(Radians(F('longitude')) - Radians(longitude)) +
                    Sin(Radians(latitude)) * Sin(Radians(F('latitude')))
                )
            ).order_by('distance')
        except ValueError:
            pass

    return render(request, 'services.html', {'services': services})

def service_map(request):
    services = Service.objects.filter(latitude__isnull=False, longitude__isnull=False)
    return render(request, 'service_map.html', {'services': services})

def service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk)
    comments = service.comments.filter(parent=None).order_by('-created_at')  # Top-level comments
    form = ServiceCommentForm()

    if request.method == 'POST':
        form = ServiceCommentForm(request.POST)
        if form.is_valid():
            if request.user.is_authenticated:
                parent_id = request.POST.get('parent_id')
                comment = form.save(commit=False)
                comment.post = service
                comment.author = request.user
                if parent_id:  # If replying to a comment
                    parent_comment = ServiceComment.objects.get(id=parent_id)
                    comment.parent = parent_comment
                comment.save()
            return redirect('service_detail', pk=pk)

    context = {
        'service': service,
        'comments': comments,
        'form': form,
    }
    return render(request, 'service_detail.html', context)
