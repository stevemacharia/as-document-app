from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django_otp.plugins.otp_email.models import EmailDevice
from django.contrib.auth.decorators import login_required
from .forms import AccountForm
from django.contrib import messages

# Create your views here.
def send_otp_via_email(user):
    device, created = EmailDevice.objects.get_or_create(user=user, confirmed=True)
    device.generate_challenge()

def password_reset_request(request):
    if request.method == "POST":
        email = request.POST["email"]
        associated_users = User.objects.filter(email=email)
        if associated_users.exists():
            for user in associated_users:
                send_otp_via_email(user)
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                reset_url = f"http://{request.get_host()}{url}"
                send_mail("Password Reset Request", f"Use the following link to reset your password: {reset_url}", "no-reply@myapp.com", [email])
                return HttpResponse("Password reset link sent.")
    return render(request, "password_reset.html")

def password_reset_confirm(request, uidb64=None, token=None):
    if request.method == 'POST':
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        if default_token_generator.check_token(user, token):
            new_password = request.POST['new_password']
            user.set_password(new_password)
            user.save()
            return HttpResponseRedirect(reverse('account_login'))
        else:
            return HttpResponse('Password reset link is invalid.')
    return render(request, 'password_reset_confirm.html')



@login_required
def profile(request):
    if request.method == 'POST':
        u_form = AccountForm(request.POST, instance=request.user)
        if u_form.is_valid():
            u_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')
        else:
            messages.warning(request, f'Failed to update your details, Kindly retry again. ')
            return redirect('profile')
    else:
        u_form = AccountForm(instance=request.user)
        context = {
                'u_form': u_form,
        }

    return render(request, 'user/profile.html', context)


def business_account(request):
    if request.method == 'POST':
        u_form = AccountForm(request.POST, instance=request.user)
        if u_form.is_valid():
            b_form = u_form.save(commit=False)
            b_form.user = request.user
            b_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('business-account')
        else:
            messages.warning(request, f'Failed to update your details, Kindly retry again. ')
            return redirect('business-account')
    else:
        u_form = AccountForm(instance=request.user)
        context = {
                'u_form': u_form,
        }
    return render(request, 'user/business_accounts.html', context)
