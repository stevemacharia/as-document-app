from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import InvoiceForm, InvoiceItemsForm
from accounts.forms import PaymentOptionForm
from .models import Client, Invoice, InvoiceItems
from documents.models import Client, Quotation, QuotationItems
from documents.forms import QuotationForm, QuotationItemsForm, ClientForm
from documents.models import Quotation
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
from django.contrib.auth.decorators import login_required
from accounts.models import BusinessAccount
from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.utils import timezone
import os
# Create your views here.


@login_required
def invoice(request):
    form = InvoiceItemsForm(prefix='form0')
    invoice_form = InvoiceForm()
    payment_form = PaymentOptionForm()
    business_account = request.session.get('selected_business_account')
    selected_business_account = BusinessAccount.objects.get(id=business_account) 
    draft_invoices = Invoice.objects.filter(business_account=selected_business_account, status=False)
    final_invoices = Invoice.objects.filter(business_account=selected_business_account, status=True)
    final_quotations = Quotation.objects.filter(business_account=selected_business_account, status=True)
    if request.method == 'POST':
        invoice_form = InvoiceForm(request.POST)
        payment_form_instance = PaymentOptionForm(request.POST)
        form_count = int(request.POST.get('form_count', 1))
        forms = [InvoiceItemsForm(request.POST, prefix=f'form{i}') for i in range(form_count)]
        x = str(uuid.uuid4())[:5]

        if invoice_form.is_valid() and all(f.is_valid() for f in forms) and payment_form_instance.is_valid:

            # start of payment form save
            payment_form = payment_form_instance.save(commit=False)
            payment_form.business = business_account
            payment_form.save()

            # end of payment form save



            q_form = invoice_form.save(commit=False)
            # Retrieve a business account value from the session
            q_form.business_account = selected_business_account
            client_initials = str(q_form.client)[:3]
            invoice_id_smaller = f'AS{client_initials}{x}'
            q_form.invoice_id = invoice_id_smaller.upper()
            new_invoice_id = q_form.invoice_id

            ###############QR CODE GENERATION#########
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            data = "www.document.arieshelby.com/invoice/invoice_verification/"+new_invoice_id 
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image(fill='black', back_color='white')

            # Save QR code image to a BytesIO object
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)

            # Save the image to the ImageField

            file_name = f"qr_code_{data}.png"

            ###############END OF QR CODE GENERATION##
            q_form.qr_code_image.save(file_name, File(buffer), save=False)

            q_form.save()
            
            chosen_invoice = Invoice.objects.get(invoice_id=new_invoice_id)

            sub_total_price = 0
            # Process each QuotationItemsForm
            for form in forms:
                item = form.save(commit=False)
                item.invoice = chosen_invoice
                item_price = item.price * item.quantity
                sub_total_price += item_price
                item.save()

            chosen_invoice.sub_total = sub_total_price
            chosen_invoice.save()

            #########   GENERATE PDF   #############

            template_name = get_template('invoice/invoice_doc.html')
            listed_invoice_items = InvoiceItems.objects.filter(invoice=chosen_invoice)
            selected_business_account = request.session.get('selected_business_account')
            context = {
                'selected_invoice': chosen_invoice,
                'listed_invoice_items': listed_invoice_items,
                'selected_business_account': selected_business_account,
            }
            rendered_html = template_name.render(context)
            pdf_file = HTML(string=rendered_html).write_pdf()

            ########## Update Invoice Model ##############
            chosen_invoice.invoice_doc = SimpleUploadedFile(
                f'Arieshelby Invoice-{chosen_invoice.invoice_id}.pdf', pdf_file,
                content_type='application/pdf')
            chosen_invoice.save()
            ###############################
            #########   GENERATE PDF   ##################

            messages.success(request, f'Invoice saved Successfully.')
            return redirect('invoice')
        else:
            # Gather errors for the main form and each items form
            error_messages = []
            if invoice_form.errors:
                for field, errors in invoice_form.errors.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")
            for form in forms:
                if form.errors:
                    for field, errors in form.errors.items():
                        for error in errors:
                            error_messages.append(f"{field} (item): {error}")

            # Pass error messages to the template
            return render(request, 'invoice/invoice.html', {
                'forms': forms,
                'invoice_form': invoice_form,
                'payment_form': payment_form,
                'draft_invoice': draft_invoices,
                'final_invoice': final_invoices,
                'final_quotations': final_quotations,
                'error_messages': error_messages
            })

    else:

        return render(request, 'invoice/invoice.html',{
            'forms': [form],
            'invoice_form': invoice_form,
            'payment_form': payment_form,
            'draft_invoice': draft_invoices,
            'final_invoice': final_invoices,
            'final_quotations': final_quotations
            
            })

@login_required
def invoice_details(request, id):
    chosen_invoice = Invoice.objects.get(id=id)
    listed_invoice_items = InvoiceItems.objects.filter(invoice=chosen_invoice)
    InvoiceItemFormSet = inlineformset_factory(Invoice, InvoiceItems, can_delete=True, form=InvoiceItemsForm, extra=0)
    form = InvoiceForm(instance=chosen_invoice)
    formset = InvoiceItemFormSet(instance=chosen_invoice)
    invoice_items_form = InvoiceItemsForm()

    if request.method == "POST":
        form = InvoiceForm(request.POST, instance=chosen_invoice)
        formset = InvoiceItemFormSet(request.POST, instance=chosen_invoice)
        
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
            form_replica.sub_total = sub_total_price  # Update the subtotal
            form_replica.save()
            formset.save()


            messages.success(request, f'Updated Invoice Successfully.')
            return redirect('invoice')
        else:
            return render(request, 'invoice/invoice_details.html',
                        {
                            'invoice_form': form,
                            'invoice_items_form': invoice_items_form,
                            'Invoiceformset': formset,
                            'chosen_invoice': chosen_invoice
                        })

    else:

        context = {
            'invoice_form': form,
            'invoice_items_form': invoice_items_form,
            'Invoiceformset': formset,
            'chosen_invoice': chosen_invoice
        }
    return render(request, 'invoice/invoice_details.html', context)

@login_required
def add_invoice_item(request, id):
    selected_invoice = Invoice.objects.get(id=id)
    if request.method == "POST":
        invoice_item_form = InvoiceItemsForm(request.POST)
        if invoice_item_form.is_valid():
            QI_form = invoice_item_form.save(commit=False)

            price = invoice_item_form.cleaned_data['price']
            quantity = invoice_item_form.cleaned_data['quantity']
  
            item_price = int(float(price)) * int(quantity)
            total_iten_price = item_price

            new_sub_total_price = selected_invoice.sub_total + total_iten_price

            selected_invoice.sub_total = new_sub_total_price
            selected_invoice.save()

            QI_form.invoice = selected_invoice
            QI_form.save()
            messages.success(request, f'Successfully added invoice item')
            return redirect(reverse('invoice_details', kwargs={'id': id}))
        else:
            return render(request, 'invoice/add_invoice_item.html',
                        {
                        'invoice_items_form': invoice_item_form,
                        'chosen_invoice': selected_invoice,

                        })
    else:
            messages.success(request, f'Kindly retry again')
            return redirect(reverse('invoice_details', kwargs={'id': id}))

@login_required
def invoice_delete(request, id):
    selected_invoice = Invoice.objects.get(id=id)
    selected_invoice.delete()
    messages.success(request, f'Invoice deleted successfully')
    return redirect('invoice')


@login_required
def convert_quotation_to_invoice(request, id):
    # Fetch the quotation instance
    quotation = get_object_or_404(Quotation, id=id)
    x = str(uuid.uuid4())[:5]
    client_initials = str(quotation.client)[:3]
    new_invoice_id = 'AS-' + str(client_initials) + '-' + x
    # Create a new Invoice instance with Quotation details
    invoice = Invoice.objects.create(
        invoice_id = new_invoice_id,
        client=quotation.client,
        business_account=quotation.business_account,
        status=quotation.status,
        invoice_doc=quotation.quotation_doc,
        data=quotation.data,
        qr_code_image=quotation.qr_code_image,
        note=quotation.note,
        submission_date=timezone.now(),
        taxable=quotation.taxable,
        sub_total=quotation.sub_total,
        total_price=quotation.total_price,
    )

    # Copy each QuotationItem to InvoiceItem
    quotation_items = QuotationItems.objects.filter(quotation=quotation)
    for item in quotation_items:
        InvoiceItems.objects.create(
            invoice=invoice,
            item=item.item,
            item_description=item.item_description,
            quantity=item.quantity,
            price=item.price,
        )

    # Optionally update the quotation status or other fields
    quotation.status = True  # Mark the quotation as converted
    quotation.save()

    # Redirect to the invoice detail page with the new invoice ID
    return redirect(reverse('invoice_details', args=[invoice.id]))



@login_required
def generate_pdf_invoice(request, id):
    selected_invoice = Invoice.objects.get(id=id)
    listed_invoice_items = InvoiceItems.objects.filter(invoice=selected_invoice)
    business_account = request.session.get('selected_business_account')
    selected_business_account = BusinessAccount.objects.get(id=business_account) 
    # Template context variables
    context = {
        'selected_business_account': selected_business_account,
        'selected_invoice': selected_invoice,
        'listed_invoice_items': listed_invoice_items,
    }

    # Path to your image
    qr_code_url = selected_invoice.qr_code_image.url
    # qr_code_path = os.path.join('static/images', 'qr-code.png')
    # qr_code_url = request.build_absolute_uri(qr_code_path)

    # Update context with the image URL
    context['qr_code_url'] = qr_code_url

    # Render the HTML template with context
    html_string = render_to_string('invoice/invoice_doc.html', context)

    # Create a PDF
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf(stylesheets=[CSS(string='@page { size: A4; margin: 0.5cm }')])

    ########## Update Invoice Model ##############
    selected_invoice.invoice_doc = SimpleUploadedFile(
        'Arieshelby Invoice-' + selected_invoice.invoice_id + '.pdf', pdf, content_type='application/pdf')
    selected_invoice.save()
    ################################################

    # Create a response object and specify the PDF content type
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Arieshelby Invoice-' + selected_invoice.invoice_id + '.pdf"'

    return response

def invoice_verification(request, id):
    if Invoice.objects.filter(invoice_id=id):
        context = {
            'invoice_id': id,
            'message_tag': "success",
            'message': "Verification Successful. This Invoice was generated by Arieshelby LLC",
        }
        # messages.success(request, f'Verification Successful. This invoice was generated by Arieshelby LLC')
        return render(request, 'invoice/invoice_confirmation.html', context)
    else:
        context = {
            'invoice_id': "",
            'message_tag': "warning",
            'message': "Verification not successful. This Invoice was NOT generated by Arieshelby LLC",
        }
        # messages.warning(request, f'Verification not successful. This invoice was NOT generated by Arieshelby LLC')
        return render(request, 'invoice/invoice_confirmation.html', context)




# @login_required
# def invoice_confirmation(request):
#     return render(request, 'invoice/invoice_confirmation.html')
#############start of invoice#############
#############end of invoice#############



