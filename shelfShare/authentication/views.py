from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from .forms import CustomUserCreationForm



def registration_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # Send email to the registered user
            subject = 'Welcome to Gaming World!'
            message = f"Hello {form.cleaned_data['first_name']} {form.cleaned_data['last_name']},\n\nThank you for registering with ShelfShare Portal. We are excited to have you!\nBest of luck for your readings.\n\nRegards,\nGaming World Team"
            recipient_list = [form.cleaned_data['email']]

            
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,  # from email
                recipient_list,
                fail_silently=False,
            )
            
            messages.success(request, "Registration successful! Please check your email and log in.")
        else:
            print(form.errors)
            messages.error(request, "Registration failed. Please fix the errors below.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'Register.html', {'form': form})




def Login_View(request):
    if request.method == 'POST':
        email = request.POST.get('email')  # because username = email
        password = request.POST.get('password')
        
        # authenticate() uses username field internally, so pass email as username
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome {user.first_name}! You have logged in successfully.")
        else:
            messages.error(request, "Invalid Email or Password. Please try again.")
    
    return render(request, 'login.html')





def logout_view(request):
    logout(request)  # This will log the user out and clear the session
    messages.success(request, "You have been logged out successfully.")
    return redirect('login') 



