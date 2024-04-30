from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import QuotationForm, QuotationItemsForm, ClientForm
from .models import Client, Quotation, QuotationItems
import uuid

# Create your views here.
def index(request):
    return render(request, 'documents/index.html')


def quotations(request):
    if request.method == 'POST':
        quotation_form = QuotationForm(request.POST)
        if quotation_form.is_valid():
            x = uuid.uuid4()
            quotation_form.save(commit=False)
            quotation_form.id = x
            quotation_form.save()
            # ex = Example()
            # ex.username = form.cleaned_data['username']
            # ex.save()

            messages.success(request, f'Added Record Successfully.')
            return redirect('quotations')
        else:
            messages.warning(request, f'Failed to add record, Kindly retry again..')
            return redirect('quotations')
    else:
        quotation_form = QuotationForm()
        quotation_items_form = QuotationItemsForm()
        context = {
            'quotation_form': quotation_form,
            'quotation_items_form': quotation_items_form,
        }
        return render(request, 'documents/quotations.html', context)

def quotation_details(request, id):
    chosen_quotation = Quotation.objects.get(id=id)
    context = {
        'chosen_quotation': chosen_quotation,
    }
    return render(request, 'documents/quotation_details.html', context)

def clients(request):
    if request.method == "POST":
        client_form = ClientForm(request.POST)
        if client_form.is_valid():
            client_form.save()
            context = {
                'client_form': client_form,
            }
            messages.success(request, f'Added Record Successfully.')
            return redirect('clients')
        else:
            messages.warning(request, f'Failed to save Client details, Kindly retry again. ')
            return redirect('clients')
    else:
        client_form = ClientForm()
        client_list = Client.objects.all()
        context = {
            'client_form': client_form,
            'client_list': client_list,
        }
        return render(request, 'documents/clients.html', context)


def client_details(request, id):
    chosen_client = Client.objects.get(id=id)
    if request.method == "POST":
        client_form = ClientForm(request.POST)
        if client_form.is_valid():
            client_form.save()
            context = {
                'client_form': client_form,
            }
            messages.success(request, f'Edited Record Successfully.')
            return redirect('clients')
        else:
            messages.warning(request, f'Failed to save Client details, Kindly retry again. ')
            return redirect('clients')
    else:
        client_form = ClientForm(instance=chosen_client)
        client_list = Client.objects.all()
        context = {
            'client_form': client_form,
            'client_list': client_list,
            'chosen_client': chosen_client,
        }
        return render(request, 'documents/client_details.html', context)


def client_delete(request, id):
    selected_client = Client.objects.get(id=id)
    selected_client.delete()
    messages.success(request, f'Contract deleted successfully')
    return redirect('clients')
