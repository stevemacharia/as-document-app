from django.shortcuts import render
from .forms import BusinessAccountForm, PaymentOptionForm
from documents.forms import ClientForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import BusinessAccount, PaymentOption
from deliverynote.models import DeliveryNote
from documents.models import Client


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
            u_form = BusinessAccountForm()
            return render(request, 'accounts/business_account_register.html', {'u_form': business_form})
    else:
        u_form = BusinessAccountForm()
    return render(request, 'accounts/business_account_register.html', {'u_form': u_form})

@login_required
def payment_account_register(request):
    if request.method == 'POST':
        payment_form_instance= PaymentOptionForm(request.POST)
        business_id=request.session['registered_business_instance']
        business_account= BusinessAccount.objects.get(id=business_id)
        # Capture the referrer (previous page URL)
        previous_url = request.META.get('HTTP_REFERER')

        if payment_form_instance.is_valid():
            payment_form = payment_form_instance.save(commit=False)
            payment_form.business = business_account
            payment_form.save()

            messages.success(request, f'Your payment account has been added!')
            
            # Redirect to the referrer or a fallback URL if the referrer is not available
            if previous_url:
                return redirect('client-address-creation')
            else:
                # Fallback URL in case referrer is not present
                return redirect('index')
        else:
            return render(request, 'accounts/payment_account_register.html', {'payment_form': payment_form_instance})
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
            return render(request, 'accounts/client_address_creation.html', {'client_address_form': client_address_form_instance})
    else:   
        client_address_form= ClientForm()

    return render(request, 'accounts/client_address_creation.html', {'client_address_form': client_address_form})

# start of business profile views


@login_required
def business_profile(request):
    if request.method == 'POST':
        business_account_id = request.session.get('selected_business_account')
        selected_business_account = BusinessAccount.objects.get(id=business_account_id)
        u_form = BusinessAccountForm(request.POST, request.FILES, instance=selected_business_account)
        payment_options = PaymentOption.objects.filter(business=selected_business_account)
        client_addresses= Client.objects.filter(business_account=selected_business_account)

        if u_form.is_valid():
            u_form.save()
            messages.success(request, f'Your account has been updated!' )
            return redirect('business-profile', id)
        else:
            payment_form= PaymentOptionForm()
            return render(request, 'accounts/business_profile.html', {'u_form': u_form, 'business_account':selected_business_account, 'payment_options':payment_options, 'client_addresses': client_addresses, 'payment_form':payment_form})

    else:
        business_account_id = request.session.get('selected_business_account')
        selected_business_account = BusinessAccount.objects.get(id=business_account_id)
        u_form = BusinessAccountForm(instance=selected_business_account)
        payment_options = PaymentOption.objects.filter(business=selected_business_account)
        client_addresses= Client.objects.filter(business_account=selected_business_account)
        payment_form= PaymentOptionForm()

    return render(request, 'accounts/business_profile.html', {'u_form': u_form, 'business_account':selected_business_account, 'payment_options':payment_options, 'client_addresses': client_addresses, 'payment_form':payment_form})

@login_required
def payment_account_add(request):
    # Capture the referrer (previous page URL)
    previous_url = request.META.get('HTTP_REFERER')
    business_account_id = request.session.get('selected_business_account')
    selected_business_account = BusinessAccount.objects.get(id=business_account_id)

    if request.method == 'POST':
        payment_form_instance = PaymentOptionForm(request.POST)
        if payment_form_instance.is_valid():

            payment_form= payment_form_instance.save(commit=False)

            payment_form.business=selected_business_account
            payment_form.save()

            messages.success(request, f'Your payment account has been added!')
            # Redirect to the referrer or a fallback URL if the referrer is not available
            if previous_url:
                return redirect('business-profile')
            else:
                # Fallback URL in case referrer is not present
                return redirect('index') 
        else: 
            return render(request, 'accounts/payment_add.html', {'payment_form':payment_form_instance })
    else:
        payment_form= PaymentOptionForm()
    return render(request, 'accounts/payment_add.html', {'payment_form':payment_form})




@login_required
def payment_edit(request, id):
    selected_payment_option = PaymentOption.objects.get(id=id)
    # Capture the referrer (previous page URL)
    previous_url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        payment_form_instance = PaymentOptionForm(request.POST,  instance=selected_payment_option)

        if payment_form_instance.is_valid():
            payment_form_instance.save()
            messages.success(request, f'Your payment account has been updated!')
            # Redirect to the referrer or a fallback URL if the referrer is not available
            if previous_url:
                return redirect('business-profile')
            else:
                # Fallback URL in case referrer is not present
                return redirect('index') 
        else:

            return render(request, 'accounts/payment_edit.html', {'payment_form':payment_form_instance, 'payment_option_id' : id})

    else:
        payment_option_id = id
        payment_form= PaymentOptionForm(instance=selected_payment_option)
    return render(request, 'accounts/payment_edit.html', {'payment_form':payment_form, 'payment_option_id' : payment_option_id})


@login_required
def payment_account_delete(request, id):
    selected_payment_option = PaymentOption.objects.get(id=id)
    selected_payment_option.delete()
    # Capture the referrer (previous page URL)
    previous_url = request.META.get('HTTP_REFERER')
    messages.success(request, f'Payment account deleted successfully')
        # Redirect to the referrer or a fallback URL if the referrer is not available
    if previous_url:
        return redirect(previous_url)
    else:
        # Fallback URL in case referrer is not present
        return redirect('index') 


@login_required
def client_edit(request, id):
    selected_client_profile = Client.objects.get(id=id)
    # Capture the referrer (previous page URL)
    previous_url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        client_profile_form_instance = ClientForm(request.POST,  instance=selected_client_profile)

        if client_profile_form_instance.is_valid():
            client_profile_form_instance.save()

            messages.success(request, f'Client address has been updated!')
            # Redirect to the referrer or a fallback URL if the referrer is not available
            if previous_url:
                return redirect('business-profile')
            else:
                # Fallback URL in case referrer is not present
                return redirect('index')
        else: 
            return render(request, 'accounts/client_edit.html', {'client_profile_form':client_profile_form_instance, 'client_profile_id' : id})

    else:
        client_profile_id = id
        client_profile_form= ClientForm(instance=selected_client_profile)
    return render(request, 'accounts/client_edit.html', {'client_profile_form':client_profile_form, 'client_profile_id' : client_profile_id })


@login_required
def client_profile_add(request):
    # Capture the referrer (previous page URL)
    previous_url = request.META.get('HTTP_REFERER')
    business_account_id = request.session.get('selected_business_account')
    selected_business_account = BusinessAccount.objects.get(id=business_account_id)

    if request.method == 'POST':
        client_profile_form_instance = ClientForm(request.POST)
        if client_profile_form_instance.is_valid():

            client_profile_form= client_profile_form_instance.save(commit=False)

            client_profile_form.business_account=selected_business_account
            client_profile_form.save()

            messages.success(request, f'Client account has been added!')
            # Redirect to the referrer or a fallback URL if the referrer is not available
            if previous_url:
                return redirect('business-profile')
            else:
                # Fallback URL in case referrer is not present
                return redirect('index')
        else:
            return render(request, 'accounts/client_profile_add.html', {'client_address_form':client_profile_form_instance})
    else:
        client_address_form= ClientForm()
    return render(request, 'accounts/client_profile_add.html', {'client_address_form':client_address_form})


@login_required
def client_profile_delete(request, id):
    selected_client_profile_option = Client.objects.get(id=id)
    selected_client_profile_option.delete()
    # Capture the referrer (previous page URL)
    previous_url = request.META.get('HTTP_REFERER')
    messages.success(request, f'Client profile deleted successfully')
        # Redirect to the referrer or a fallback URL if the referrer is not available
    if previous_url:
        return redirect(previous_url)
    else:
        # Fallback URL in case referrer is not present
        return redirect('index') 

# end of busines profile views


@login_required
def business_account(request):
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