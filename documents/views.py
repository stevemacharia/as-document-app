from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import QuotationForm, QuotationItemsForm, ClientForm
from .models import Client, Quotation, QuotationItems
import uuid
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.core.files.uploadedfile import SimpleUploadedFile
from django_renderpdf.views import PDFView
import datetime
from django.conf import settings
from django.urls import reverse
from django.shortcuts import render
from django.template.loader import get_template
import json
from weasyprint import HTML, CSS
from django.http import FileResponse
from django.core.files.base import ContentFile
import qrcode
from io import BytesIO
from django.core.files import File
from django.core.files.storage import default_storage
from django.template.loader import render_to_string
from weasyprint import HTML
from invoice.models import Invoice, InvoiceItems
from deliverynote.models import DeliveryNote, DeliveryNoteItems
from accounts.models import BusinessAccount
import os
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from decimal import Decimal

# Create your views here.
@login_required
def index(request):
    business_account_id = request.session.get('selected_business_account')
    business_account = BusinessAccount.objects.filter(id=business_account_id)
    if business_account:
        selected_business_account = BusinessAccount.objects.get(id=business_account_id)
        # selected_business_account = BusinessAccount.objects.get(id=id, user=request.user)
        quotations = Quotation.objects.filter(business_account=selected_business_account)
        invoices = Invoice.objects.filter(business_account=selected_business_account)
        delivery_notes = DeliveryNote.objects.filter(business_account=selected_business_account)
        clients = Client.objects.filter(business_account=selected_business_account)

        quotation_count = quotations.count()
        invoice_count = invoices.count()
        d_note_count = delivery_notes.count()
        client_count = clients.count()

        context = {
            'all_quotations': quotations,
            'all_invoices': invoices,
            'delivery_notes': delivery_notes,
            'selected_business_account': selected_business_account,
            'quotation_count' : quotation_count,
            'invoice_count': invoice_count,
            'd_note_count': d_note_count,
            'client_count': client_count,
        }
        return render(request, 'documents/index.html', context)
    else:
        return redirect('business-account')

@login_required
def quotations(request):
    form = QuotationItemsForm(prefix='form0')
    quotation_form = QuotationForm()
    business_account = request.session.get('selected_business_account')
    selected_business_account = BusinessAccount.objects.get(id=business_account) 
    draft_quotations = Quotation.objects.filter(business_account=selected_business_account, status=False)
    final_quotations = Quotation.objects.filter(business_account=selected_business_account, status=True)
    final_quotations_count = Quotation.objects.filter(business_account=selected_business_account, status=True).count()
    draft_quotations_count = Quotation.objects.filter(business_account=selected_business_account, status=False).count()

    if request.method == 'POST':
        quotation_form = QuotationForm(request.POST)
        form_count = int(request.POST.get('form_count', 1))
        forms = [QuotationItemsForm(request.POST, prefix=f'form{i}') for i in range(form_count)]
        x = str(uuid.uuid4())[:5]

        if quotation_form.is_valid() and all(f.is_valid() for f in forms):
            # Process and save the main QuotationForm
            q_form = quotation_form.save(commit=False)
            q_form.business_account = selected_business_account
            client_initials = str(q_form.client)[:3]
            # client_initials = client_initials_smaller.upper()
            quotation_id_smaller = f'AS{client_initials}{x}'
            q_form.quotation_id = quotation_id_smaller.upper()
            new_quotation_id = q_form.quotation_id 
            
            # QR Code Generation
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            data = "www.document.arieshelby.com/quotation_verification/" + new_quotation_id
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image(fill='black', back_color='white')

            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            q_form.qr_code_image.save(f"qr_code_{data}.png", File(buffer), save=False)
            q_form.save()
            
            chosen_quotation = Quotation.objects.get(quotation_id=q_form.quotation_id)
            sub_total_price = 0

            # Process each QuotationItemsForm
            for form in forms:
                item = form.save(commit=False)
                item.quotation = chosen_quotation
                item_price = item.price * item.quantity
                sub_total_price += item_price
                item.save()

            chosen_quotation.sub_total = sub_total_price
            chosen_quotation.save()

            # PDF Generation
            template_name = get_template('documents/quotation_doc.html')
            listed_quotation_items = QuotationItems.objects.filter(quotation=chosen_quotation)
            context = {
                'selected_quotation': chosen_quotation,
                'listed_quotation_items': listed_quotation_items,
            }
            pdf_file = HTML(string=template_name.render(context)).write_pdf()
            chosen_quotation.quotation_doc = SimpleUploadedFile(
                f'{selected_business_account.name} Quotation-{chosen_quotation.quotation_id}.pdf', pdf_file, content_type='application/pdf'
            )
            chosen_quotation.save()

            messages.success(request, 'Quotation and items saved successfully.')
            return redirect('quotations')
        else:
            # Gather errors for the main form and each items form
            error_messages = []
            if quotation_form.errors:
                for field, errors in quotation_form.errors.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")
            for form in forms:
                if form.errors:
                    for field, errors in form.errors.items():
                        for error in errors:
                            error_messages.append(f"{field} (item): {error}")

            # Pass error messages to the template
            return render(request, 'documents/quotations.html', {
                'forms': forms,
                'quotation_form': quotation_form,
                'draft_quotations': draft_quotations,
                'final_quotations': final_quotations,
                'error_messages': error_messages,
                'final_quotations_count': final_quotations_count,
                'draft_quotations_count': draft_quotations_count
            })

    else:
        return render(request, 'documents/quotations.html', {
            'forms': [form],
            'quotation_form': quotation_form,
            'draft_quotations': draft_quotations,
            'final_quotations': final_quotations,
            'final_quotations_count': final_quotations_count,
            'draft_quotations_count': draft_quotations_count
        })

@login_required
def quotation_details(request, id):
    chosen_quotation = Quotation.objects.get(id=id)
    listed_quotation_items = QuotationItems.objects.filter(quotation=chosen_quotation)
    QuotationItemFormSet = inlineformset_factory(Quotation, QuotationItems, form=QuotationItemsForm, extra=0)
    quotation_items_form = QuotationItemsForm()
    form_instance = QuotationForm(instance=chosen_quotation)
    formset_instance = QuotationItemFormSet(instance=chosen_quotation)

    if request.method == "POST":
        form = QuotationForm(request.POST, instance=chosen_quotation)
        formset = QuotationItemFormSet(request.POST, instance=chosen_quotation)
        if form.is_valid() and formset.is_valid():
            sub_total_price = 0
            for i in formset:
                cd = i.cleaned_data
                # Only add to subtotal if the form is not marked for deletion
                if not cd.get('DELETE', False):
                    cleaned_price = cd.get('price', 0)
                    cleaned_quantity = cd.get('quantity', 0)
                    # item_price = float(cleaned_price) * int(cleaned_quantity)
                    item_price = Decimal(cleaned_price) * Decimal(cd.get('quantity', 0))
                    sub_total_price = sub_total_price + item_price

            form_replica = form.save(commit=False)
            form_replica.sub_total = sub_total_price
            form_replica.save()
            # form.save()
            formset.save()
            messages.success(request, f'Updated Quotation Successfully.')
            return redirect('quotations')
        else:
            return render(request, 'documents/quotation_details.html', 
                          {
                              'quotation_form': form, 
                              'QIformset':formset, 
                              'chosen_quotation': chosen_quotation, 
                              'quotation_items_form': quotation_items_form
                           })

    else:
        context = {
            'quotation_form': form_instance,
            'quotation_items_form': quotation_items_form,
            'QIformset': formset_instance,
            'chosen_quotation': chosen_quotation
        }
    return render(request, 'documents/quotation_details.html', context)

@login_required
def add_quotation_item(request, id):
    selected_quotation = Quotation.objects.get(id=id)
    if request.method == "POST":
        quotation_item_form = QuotationItemsForm(request.POST)
        if quotation_item_form.is_valid():
            QI_form = quotation_item_form.save(commit=False)

            price = quotation_item_form.cleaned_data['price']
            quantity = quotation_item_form.cleaned_data['quantity']
  
            item_price = int(float(price)) * int(quantity)
            total_iten_price = item_price

            new_sub_total_price = selected_quotation.sub_total + total_iten_price

            selected_quotation.sub_total = new_sub_total_price
            selected_quotation.save()


            QI_form.quotation = selected_quotation
            QI_form.save()
            messages.success(request, f'Successfully added quotation item')
            return redirect(reverse('quotation_details', kwargs={'id': id}))
        else:
            return render(request, 'documents/add_quotation_item.html',
                        {
                            'chosen_quotation': selected_quotation,
                            'quotation_items_form': quotation_item_form,

                        })
    else:
        messages.warning(request, f'Not post request')
        return redirect('quotations')

@login_required
def quotation_delete(request, id):
    selected_quotation = Quotation.objects.get(id=id)
    selected_quotation.delete()
    messages.success(request, f'Quotation deleted successfully')
    return redirect('quotations')



@login_required
def clients(request):
    if request.method == "POST":
        client_form = ClientForm(request.POST)
        if client_form.is_valid():
            business_account = request.session.get('selected_business_account')
            selected_business_account = BusinessAccount.objects.get(id=business_account) 
            c_form = client_form.save(commit=False)
            c_form.business_account = selected_business_account
            c_form.save()
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
        business_account = request.session.get('selected_business_account')
        selected_business_account = BusinessAccount.objects.get(id=business_account) 
        client_list = Client.objects.filter(business_account=selected_business_account)
        context = {
            'client_form': client_form,
            'client_list': client_list,
        }
        return render(request, 'documents/clients.html', context)

@login_required
def client_details(request, id):
    chosen_client = Client.objects.get(id=id)
    if request.method == "POST":
        client_form = ClientForm(request.POST, instance=chosen_client)
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

@login_required
def client_delete(request, id):
    selected_client = Client.objects.get(id=id)
    selected_client.delete()
    messages.success(request, f'Client details deleted successfully')
    return redirect('clients')

@login_required
def generate_pdf_quotation(request, id):
    selected_quotation = Quotation.objects.get(id=id)
    listed_quotation_items = QuotationItems.objects.filter(quotation=selected_quotation)
    business_account = request.session.get('selected_business_account')
    selected_business_account = BusinessAccount.objects.get(id=business_account) 
    # Template context variables
    context = {
        'selected_business_account': selected_business_account,
        'selected_quotation': selected_quotation,
        'listed_quotation_items': listed_quotation_items,
    }

    # Path to your image
    qr_code_url = selected_quotation.qr_code_image.url
    # qr_code_path = os.path.join('static/images', 'qr-code.png')
    # qr_code_url = request.build_absolute_uri(qr_code_path)

    # Update context with the image URL
    context['qr_code_url'] = qr_code_url

    # Render the HTML template with context
    html_string = render_to_string('documents/quotation_doc.html', context)

    # Create a PDF
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf(stylesheets=[CSS(string='@page { size: A4; margin: 0.5cm }')])

    ########## Update Quotation Model ##############
    selected_quotation.quotation_doc = SimpleUploadedFile(
        '{selected_business_account.name} Quotation-' + selected_quotation.quotation_id + '.pdf', pdf, content_type='application/pdf')
    selected_quotation.save()
    ################################################

    # Create a response object and specify the PDF content type
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="{selected_business_account.name} Quotation-' + selected_quotation.quotation_id + '.pdf"'

    return response

def quotation_verification(request, id):
    selected_quotation = Quotation.objects.get(quotation_id=id)

    if Quotation.objects.filter(quotation_id=id):
        context = {
            'document_id': id,
            'message_tag': "success",
            'message': "Verification Successful. This Quotation was generated by {selected_quotation.business_account}",
        }

        return render(request,  'documents/quotation_confirmation.html', context)
    else:
        context = {
            'document_id': "",
            'message_tag': "warning",
            'message': "Verification not successful. This Quotation was NOT generated by {selected_quotation.business_account}",
        }
        return render(request, 'documents/quotation_confirmation.html', context)




# start of search
def search(request):
    query = request.GET.get('q')
    if query:
        invoice_results = Invoice.objects.filter(
            Q(invoice_id__icontains=query) | Q(client__name__icontains=query)
        )
        quotation_results = Quotation.objects.filter(
            Q(quotation_id__icontains=query) | Q(client__name__icontains=query)
        )
        delivery_note_results = DeliveryNote.objects.filter(
            Q(dnote_id__icontains=query) | Q(client__name__icontains=query)
        )
    else:
        invoice_results = Invoice.objects.none()
        quotation_results = Quotation.objects.none()
        delivery_note_results = DeliveryNote.objects.none()

    context = {
        'query': query,
        'invoice_results': invoice_results,
        'quotation_results': quotation_results,
        'delivery_note_results': delivery_note_results,
    }
    return render(request, 'search_results.html', context)