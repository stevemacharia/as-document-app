from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ReceiptForm, ReceiptItemsForm
from accounts.forms import PaymentOptionForm
from accounts.models import PaymentOption
from .models import Receipt, ReceiptItems
from invoice.models import Client, Invoice, InvoiceItems
from invoice.forms import InvoiceForm, InvoiceItemsForm, ClientForm
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
    form = ReceiptItemsForm(prefix='form0')
    receipt_form = ReceiptForm()
    receipt_form.set_request(request)

    business_account = request.session.get('selected_business_account')
    selected_business_account = BusinessAccount.objects.get(id=business_account) 
    draft_receipts = Receipt.objects.filter(business_account=selected_business_account, status=False)
    final_receipts = Receipt.objects.filter(business_account=selected_business_account, status=True)
    final_invoice = Invoice.objects.filter(business_account=selected_business_account, status=True)
    if request.method == 'POST':
        receipt_form = ReceiptForm(request.POST)
        receipt_form.set_request(request)
        # form = InvoiceForm(request.POST)
        # form.set_request(request)  # Ensure this is called on InvoiceForm

        form_count = int(request.POST.get('form_count', 1))
        forms = [ReceiptItemsForm(request.POST, prefix=f'form{i}') for i in range(form_count)]
        x = str(uuid.uuid4())[:5]

        if receipt_form.is_valid() and all(f.is_valid() for f in forms):

            receipt_form_instance = receipt_form.save(commit=False)
            # Retrieve a business account value from the session
            receipt_form_instance.business_account = selected_business_account
            client_initials = str(receipt_form_instance.client)[:3]
            invoice_id_smaller = f'AS{client_initials}{x}'
            receipt_form_instance.invoice_id = invoice_id_smaller.upper()
            new_receipt_id = receipt_form_instance.receipt_id

            ###############QR CODE GENERATION#########
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            data = "www.document.arieshelby.com/invoice/invoice_verification/"+new_receipt_id 
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
            
            chosen_receipt = Receipt.objects.get(invoice_id=new_receipt_id)

            sub_total_price = 0
            # Process each QuotationItemsForm
            for form in forms:
                item = form.save(commit=False)
                item.invoice = chosen_receipt
                item_price = item.price * item.quantity
                sub_total_price += item_price
                item.save()

            chosen_receipt.sub_total = sub_total_price
            chosen_receipt.save()

            #########   GENERATE PDF   #############

            template_name = get_template('invoice/invoice_doc.html')
            listed_receipt_items = InvoiceItems.objects.filter(invoice=chosen_receipt)
            selected_business_account = request.session.get('selected_business_account')
            context = {
                'selected_invoice': chosen_receipt,
                'listed_invoice_items': listed_receipt_items,
                'selected_business_account': selected_business_account,
            }
            rendered_html = template_name.render(context)
            pdf_file = HTML(string=rendered_html).write_pdf()

            ########## Update Invoice Model ##############
            chosen_receipt.receipt_doc = SimpleUploadedFile(
                f'Arieshelby Invoice-{chosen_receipt.receipt_id}.pdf', pdf_file,
                content_type='application/pdf')
            chosen_receipt.save()
            ###############################
            #########   GENERATE PDF   ##################

            messages.success(request, f'Invoice saved Successfully.')
            return redirect('invoice')
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
                'error_messages': error_messages
            })

    else:

        return render(request, 'receipt/receipt.html',{
            'forms': [form],
            'receipt_form': receipt_form,
            'draft_receipt': draft_receipts,
            'final_receipt': final_receipts,
            'final_invoices': final_invoice,
            
            })