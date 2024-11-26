from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ReceiptForm, ReceiptItemsForm
from accounts.forms import PaymentOptionForm
from accounts.models import PaymentOption
from .models import Receipt, ReceiptItems
from invoice.models import Client, Invoice, InvoiceItems
from invoice.forms import InvoiceForm, InvoiceItemsForm
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
from num2words import num2words
import os

# Create your views here.
@login_required
def receipt(request):
    form = ReceiptItemsForm(prefix='form0')
    receipt_form = ReceiptForm()
    receipt_form.set_request(request)

    business_account = request.session.get('selected_business_account')
    selected_business_account = BusinessAccount.objects.get(id=business_account) 
    draft_receipts = Receipt.objects.filter(business_account=selected_business_account, status=False)
    final_receipts = Receipt.objects.filter(business_account=selected_business_account, status=True)
    final_invoice = Invoice.objects.filter(business_account=selected_business_account, status=True)
    final_receipts_count = Receipt.objects.filter(business_account=selected_business_account, status=True).count()
    draft_receipts_count = Receipt.objects.filter(business_account=selected_business_account, status=False).count()

    if request.method == 'POST':
        receipt_form = ReceiptForm(request.POST)
        receipt_form.set_request(request)


        form_count = int(request.POST.get('form_count', 1))
        forms = [ReceiptItemsForm(request.POST, prefix=f'form{i}') for i in range(form_count)]
        x = str(uuid.uuid4())[:5]

        if receipt_form.is_valid() and all(f.is_valid() for f in forms):

            receipt_form_instance = receipt_form.save(commit=False)
            # Retrieve a business account value from the session
            receipt_form_instance.business_account = selected_business_account
            client_initials = str(receipt_form_instance.client)[:3]
            receipt_id_smaller = f'AS{client_initials}{x}'
            receipt_form_instance.receipt_id = receipt_id_smaller.upper()
            new_receipt_id = receipt_form_instance.receipt_id

            ###############QR CODE GENERATION#########
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            data = "www.document.arieshelby.com/receipt/receipt_verification/"+new_receipt_id 
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
            receipt_form_instance.qr_code_image.save(file_name, File(buffer), save=False)

            receipt_form_instance.save()
            
            chosen_receipt = Receipt.objects.get(receipt_id=new_receipt_id)

            sub_total_price = 0
            # Process each InvoiceItemsForm
            for form in forms:
                item = form.save(commit=False)
                item.receipt = chosen_receipt
                item_price = item.price * item.quantity
                sub_total_price += item_price
                item.save()

            chosen_receipt.sub_total = sub_total_price
            chosen_receipt.save()

            #########   GENERATE PDF   #############

            template_name = get_template('receipt/receipt_doc.html')
            listed_receipt_items = ReceiptItems.objects.filter(receipt=chosen_receipt)
            selected_business_account = request.session.get('selected_business_account')
            context = {
                'selected_receipt': chosen_receipt,
                'listed_receipt_items': listed_receipt_items,
                'selected_business_account': selected_business_account,
            }
            rendered_html = template_name.render(context)
            pdf_file = HTML(string=rendered_html).write_pdf()

            ########## Update Receipt Model ##############
            chosen_receipt.receipt_doc = SimpleUploadedFile(
                f'{selected_business_account.name} Receipt-{chosen_receipt.receipt_id}.pdf', pdf_file,
                content_type='application/pdf')
            chosen_receipt.save()
            ###############################
            #########   GENERATE PDF   ##################

            messages.success(request, f'Receipt saved Successfully.')
            return redirect('receipt')
        else:
            # Gather errors for the main form and each items form
            error_messages = []
            if receipt_form.errors:
                for field, errors in receipt_form.errors.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")
            for form in forms:
                if form.errors:
                    for field, errors in form.errors.items():
                        for error in errors:
                            error_messages.append(f"{field} (item): {error}")

            # Pass error messages to the template
            return render(request, 'receipt/receipt.html', {
                'forms': forms,
                'receipt_form': receipt_form,
                'draft_receipt': draft_receipts,
                'final_receipt': final_receipts,
                'final_invoices': final_invoice,
                'final_receipts_count': final_receipts_count,
                'draft_receipts_count': draft_receipts_count,
                'error_messages': error_messages
            })

    else:

        return render(request, 'receipt/receipt.html',{
            'forms': [form],
            'receipt_form': receipt_form,
            'draft_receipts': draft_receipts,
            'final_receipts': final_receipts,
            'final_invoices': final_invoice,
            'final_receipts_count': final_receipts_count,
            'draft_receipts_count': draft_receipts_count,
            
            })
    
@login_required
def receipt_details(request, id):
    chosen_receipt = Receipt.objects.get(id=id)
    listed_receipt_items = ReceiptItems.objects.filter(receipt=chosen_receipt)
    ReceiptItemFormSet = inlineformset_factory(Receipt, ReceiptItems, can_delete=True, form=ReceiptItemsForm, extra=0)
    form = ReceiptForm(instance=chosen_receipt)
    form.set_request(request)
    formset = ReceiptItemFormSet(instance=chosen_receipt)
    receipt_items_form = ReceiptItemsForm()

    if request.method == "POST":
        form = ReceiptForm(request.POST, instance=chosen_receipt)
        form.set_request(request)
        formset = ReceiptItemFormSet(request.POST, instance=chosen_receipt)
        
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


            messages.success(request, f'Updated Receipt Successfully.')
            return redirect('receipt')
        else:
            return render(request, 'receipt/receipt_details.html',
                        {
                            'receipt_form': form,
                            'receipt_items_form': receipt_items_form,
                            'receiptformset': formset,
                            'chosen_receipt': chosen_receipt
                        })

    else:

        context = {
            'receipt_form': form,
            'receipt_items_form': receipt_items_form,
            'receipt_formset': formset,
            'chosen_receipt': chosen_receipt
        }
    return render(request, 'receipt/receipt_details.html', context)



@login_required
def add_receipt_item(request, id):
    selected_receipt = Receipt.objects.get(id=id)
    if request.method == "POST":
        receipt_item_form = ReceiptItemsForm(request.POST)
        if receipt_item_form.is_valid():
            QI_form = receipt_item_form.save(commit=False)

            price = receipt_item_form.cleaned_data['price']
            quantity = receipt_item_form.cleaned_data['quantity']
  
            item_price = int(float(price)) * int(quantity)
            total_iten_price = item_price

            new_sub_total_price = selected_receipt.sub_total + total_iten_price

            selected_receipt.sub_total = new_sub_total_price
            selected_receipt.save()

            QI_form.receipt = selected_receipt
            QI_form.save()
            messages.success(request, f'Successfully added receipt item')
            return redirect(reverse('receipt_details', kwargs={'id': id}))
        else:
            return render(request, 'receipt/add_receipt_item.html',
                        {
                        'receipt_items_form': receipt_item_form,
                        'chosen_receipt': selected_receipt,

                        })
    else:
            messages.success(request, f'Kindly retry again')
            return redirect(reverse('receipt_details', kwargs={'id': id}))
    



@login_required
def receipt_delete(request, id):
    selected_receipt = Receipt.objects.get(id=id)
    selected_receipt.delete()
    messages.success(request, f'Receipt deleted successfully')
    return redirect('receipt')


@login_required
def convert_invoice_to_receipt(request, id):
    # Fetch the receipt instance
    invoice = get_object_or_404(Invoice, id=id)
    x = str(uuid.uuid4())[:5]
    client_initials = str(invoice.client)[:3]
    new_receipt_id = 'AS-' + str(client_initials) + '-' + x
    # Create a new receipt instance with receipt details
    receipt = Receipt.objects.create(
        receipt_id = new_receipt_id,
        client=invoice.client,
        business_account=invoice.business_account,
        status=invoice.status,
        receipt_doc=invoice.invoice_doc,
        data=invoice.data,
        qr_code_image=invoice.qr_code_image,
        note=invoice.note,
        submission_date=timezone.now(),
        taxable=invoice.taxable,
        sub_total=invoice.sub_total,
        total_price=invoice.total_price,
    )

    # Copy each InvitationItem to InvoiceItem
    invoice_items = InvoiceItems.objects.filter(invoice=invoice)
    for item in invoice_items:
        ReceiptItems.objects.create(
            receipt=receipt,
            item=item.item,
            item_description=item.item_description,
            quantity=item.quantity,
            price=item.price,
        )

    # Optionally update the invitation status or other fields
    receipt.status = True  # Mark the receipt as converted
    receipt.save()

    # Redirect to the receipt detail page with the new receipt ID
    return redirect(reverse('receipt_details', args=[receipt.id]))







@login_required
def generate_pdf_receipt(request, id):
    selected_receipt = Receipt.objects.get(id=id)
    payment_option = selected_receipt.payment_account
    selected_payment_option = payment_option
    listed_receipt_items = ReceiptItems.objects.filter(receipt=selected_receipt)
    business_account = request.session.get('selected_business_account')
    selected_business_account = BusinessAccount.objects.get(id=business_account)
    receipt_total = selected_receipt.total_price
    # Convert number to words
    total_price_in_words = num2words(receipt_total)
    # Template context variables
    context = {
        'total_price_in_words': total_price_in_words,
        'selected_payment_option': selected_payment_option,
        'selected_business_account': selected_business_account,
        'selected_receipt': selected_receipt,
        'listed_receipt_items': listed_receipt_items,
    }

    # Path to your image
    qr_code_url = selected_receipt.qr_code_image.url
    # qr_code_path = os.path.join('static/images', 'qr-code.png')
    # qr_code_url = request.build_absolute_uri(qr_code_path)

    # Update context with the image URL
    context['qr_code_url'] = qr_code_url

    # Render the HTML template with context
    html_string = render_to_string('receipt/receipt_doc.html', context)

    # Create a PDF
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf(stylesheets=[CSS(string='@page { size: A5; margin: 0.5cm }')])

    ########## Update Receipt Model ##############
    selected_receipt.receipt_doc = SimpleUploadedFile(
        '{selected_business_account.name} Receipt-' + selected_receipt.receipt_id + '.pdf', pdf, content_type='application/pdf')
    selected_receipt.save()
    ################################################

    # Create a response object and specify the PDF content type
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="{selected_business_account.name} Receipt-' + selected_receipt.receipt_id + '.pdf"'

    return response

def receipt_verification(request, id):
    selected_receipt = Receipt.objects.get(receipt_id=id)
    if Receipt.objects.filter(receipt_id=id):
        context = {
            'receipt_id': id,
            'message_tag': "success",
            'message': "Verification Successful. This Receipt was generated by {selected_receipt.business_account}",
        }
        return render(request, 'receipt/receipt_confirmation.html', context)
    else:
        context = {
            'receipt_id': "",
            'message_tag': "warning",
            'message': "Verification not successful. This receipt was NOT generated by {selected_receipt.business_account}",
        }
        return render(request, 'receipt/receipt_confirmation.html', context)
