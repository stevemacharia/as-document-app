from django.shortcuts import render
from .forms import BusinessAccountForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import BusinessAccount
from deliverynote.models import DeliveryNote


# Create your views here.
@login_required
def business_profile(request, id):
    if request.method == 'POST':
        selected_business_account = BusinessAccount.objects.get(id=id)
        u_form = BusinessAccountForm(request.POST, instance=selected_business_account)
        if u_form.is_valid():
            u_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('business-profile', id)
        else:
            messages.warning(request, f'Failed to update your details, Kindly retry again. ')
            return redirect('business-profile', id)
    else:
        selected_business_account = BusinessAccount.objects.get(id=id)
        u_form = BusinessAccountForm(instance=selected_business_account)
        context = {
                'u_form': u_form,
                'business_account':selected_business_account
        }

    return render(request, 'accounts/business_profile.html', context)



@login_required
def business_account(request):
    if request.method == 'POST':
        u_form = BusinessAccountForm(request.POST, request.FILES)
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
        business_profiles = BusinessAccount.objects.filter(user=request.user)
        context = {
                'u_form': u_form,
                'business_profiles': business_profiles,
        }
    return render(request, 'accounts/business_accounts.html', context)

@login_required
def business_account_dashboard(request, id):
    selected_business_account = BusinessAccount.objects.get(id=id, user=request.user)
    # Store a value in the session
    request.session['selected_business_account'] = selected_business_account.id

    return redirect('index')


@login_required
def business_account_deletion(request, id):
    selected_business_account = BusinessAccount.objects.get(id=id)
    selected_business_account.delete()
    messages.success(request, f'Business account deleted successfully')
    return redirect('business-account')