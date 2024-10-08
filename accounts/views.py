from django.shortcuts import render
from .forms import BusinessAccountForm, PaymentOptionForm
from documents.forms import ClientForm
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
            messages.success(request, f'Your business account has been created!')
            return redirect('payment-account-register')
    else:
        u_form = BusinessAccountForm(instance=request.user)

    return render(request, 'accounts/business_account_register.html', {'u_form': u_form})

@login_required
def payment_account_register(request):
    if request.method == 'POST':
        payment_form_instance= PaymentOptionForm(request.POST)
        business_id=request.session['registered_business_instance']
        business_account= BusinessAccount.objects.get(id=business_id)

        if payment_form_instance.is_valid():
            payment_form = payment_form_instance.save(commit=False)
            payment_form.business = business_account
            payment_form.save()

            messages.success(request, f'Your payment account has been added!')
            return redirect('client-address-creation')
    else:   
        payment_form= PaymentOptionForm()

    return render(request, 'accounts/payment_account_register.html', {'payment_form': payment_form})



@login_required
def client_account_creation(request):
    if request.method == 'POST':
        client_address_form_instance= ClientForm(request.POST)
        business_id=request.session['registered_business_instance']
        business_account= BusinessAccount.objects.get(id=business_id)

        if client_address_form_instance.is_valid():
            client_address_form = client_address_form_instance.save(commit=False)
            client_address_form.business_account = business_account
            client_address_form.save()

            messages.success(request, f'Your have completed your business registration process!')
            return redirect('business-account')
    else:   
        client_address_form= ClientForm()

    return render(request, 'accounts/client_address_creation.html', {'client_address_form': client_address_form})


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