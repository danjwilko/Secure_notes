from django.shortcuts import render
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm

def register(request):
    """View function to handle user registration."""
    if request.method != 'POST':
        # Display a blank registration form.
        form = UserCreationForm()
    else:
        # Process the submitted form data.
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            new_user = form.save()
            # Log the user in and redirect to the home page.
            login(request, new_user)
            return render(request, 'secure_notes/index.html')
    
    # Display a blank or invalid form.
    context = {
        'form': form
    }
    
    return render(request, 'accounts/register.html', context)