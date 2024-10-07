from django.shortcuts import render
from .forms import BusinessAccountForm, PaymentOptionForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import BusinessAccount, PaymentOption
from deliverynote.models import DeliveryNote


# Create your views here.
@login_required
def busines_account_register(request):
    if request.method == 'POST':
        business_form = BusinessAccountForm(request.POST, request.FILES)
        if business_form.is_valid():
            business_instance = business_form.save(commit=False)
            business_instance.user = request.user
            business_instance.save()
            request.session['registered_business_instance'] = business_instance.id
            messages.success(request, f'Your account has been updated!')
            return redirect('payment-account-register')
    else:
        u_form = BusinessAccountForm(instance=request.user)

    return render(request, 'accounts/business_account_register.html', {'u_form': u_form})

@login_required
def payment_account_register(request):
    if request.method == 'POST':
        payment_form_instance= PaymentOptionForm(request.POST, request.FILES)
        request.session['registered_business_instance']
        if payment_form_instance.is_valid():
            payment_form = payment_form_instance.save(commit=False)
            payment_form.business = request.user
            payment_form.save()

            messages.success(request, f'Your account has been updated!')
            return redirect('business-account')
    else:
        u_form = BusinessAccountForm(instance=request.user)

    return render(request, 'accounts/business_account_register.html', {'u_form': u_form})

@login_required
def business_profile(request, id):
    if request.method == 'POST':
        selected_business_account = BusinessAccount.objects.get(id=id)
        u_form = BusinessAccountForm(request.POST, request.FILES, instance=selected_business_account)
        if u_form.is_valid():
            u_form.save()
            messages.success(request, f'Your account has been updated!' )
            return redirect('business-profile', id)
    else:
        selected_business_account = BusinessAccount.objects.get(id=id)
        u_form = BusinessAccountForm(instance=selected_business_account)

    return render(request, 'accounts/business_profile.html', {'u_form': u_form, 'business_account':selected_business_account})



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