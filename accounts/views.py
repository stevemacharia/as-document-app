from django.shortcuts import render
from .forms import BusinessAccountForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import BusinessAccount
from deliverynote.models import DeliveryNote


# Create your views here.
@login_required
def profile(request):
    if request.method == 'POST':
        u_form = BusinessAccountForm(request.POST, instance=request.user)
        if u_form.is_valid():
            u_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')
        else:
            messages.warning(request, f'Failed to update your details, Kindly retry again. ')
            return redirect('profile')
    else:
        u_form = BusinessAccountForm(instance=request.user)
        context = {
                'u_form': u_form,
        }

    return render(request, 'accounts/profile.html', context)




def business_account(request):
    if request.method == 'POST':
        u_form = BusinessAccountForm(request.POST)
        if u_form.is_valid():
            b_form = u_form.save(commit=False)
            b_form.user = request.user
            b_form.save()
            u_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('business-account')
        else:
            messages.warning(request, f'Failed to update your details, Kindly retry again. ')
            return redirect('business-account')
    else:
        u_form = BusinessAccountForm(instance=request.user)
        business_profiles = BusinessAccount.objects.all()
        context = {
                'u_form': u_form,
                'business_profiles': business_profiles,
        }
    return render(request, 'accounts/business_accounts.html', context)
