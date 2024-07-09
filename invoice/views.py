from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import InvoiceForm, InvoiceItemsForm
from .models import Client, Invoice, InvoiceItems
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
import os
# Create your views here.


@login_required
def invoice(request):
    if request.method == 'POST':
        invoice_form = InvoiceForm(request.POST)
        x = str(uuid.uuid4())[:5]

        if invoice_form.is_valid():
            q_form = invoice_form.save(commit=False)

            client = q_form.client
            # string = "Hello world"
            # string[:3]
            client_initials = str(client)[:3]
            q_form.invoice_id = 'AS/' + str(client_initials) + '/' + x

            ###############QR CODE GENERATION#########
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            data = "www.arieshelby.com/"+x
            qr.add_data(data)
            qr.make(fit=True)
            img = qr.make_image(fill='black', back_color='white')

            # Save QR code image to a BytesIO object
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)

            # Save the image to the ImageField

            file_name = f"qr_code_{data}.png"
            # qr_code.qr_code_image.save(file_name, File(buffer), save=False)
            # qr_code.save()
            ###############END OF QR CODE GENERATION##
            q_form.qr_code_image.save(file_name, File(buffer), save=False)

            q_form.save()
            new_id = 'AS/' + str(client_initials) + '/' + x
            chosen_invoice = Invoice.objects.get(invoice_id=new_id)

            forms = []
            form_count = int(request.POST.get('form_count', 1))
            sub_total_price = 0
            for i in range(form_count):
                form = InvoiceItemsForm(request.POST, prefix='form{}'.format(i))
                form_replica = form.save(commit=False)
                item_price = form_replica.price * form_replica.quantity
                sub_total_price = sub_total_price + item_price
                if form.is_valid():
                    forms.append(form)
                else:
                    invoice_form = InvoiceForm()
                    invoice_items_form = InvoiceItemsForm()
                    context = {
                        'invoice_form': invoice_form,
                        'invoice_items_form': invoice_items_form,
                    }
                    # If any form is invalid, render the template with all forms
                    return render(request, 'invoice/invoice.html', context)
            main_sub_total_price = sub_total_price
            chosen_invoice.sub_total = main_sub_total_price
            chosen_invoice.save()
            if forms:
                # If all forms are valid, save them
                for form in forms:
                    Q_Items_form = form.save(commit=False)
                    Q_Items_form.invoice = chosen_invoice
                    Q_Items_form.save()

                #########   GENERATE PDF   #############

                template_name = get_template('invoice/invoice_doc.html')
                listed_invoice_items = InvoiceItems.objects.filter(invoice=chosen_invoice)
                context = {
                    'selected_invoice': chosen_invoice,
                    'listed_invoice_items': listed_invoice_items,
                }
                rendered_html = template_name.render(context)
                pdf_file = HTML(string=rendered_html).write_pdf()

                ########## Update Invoice Model ##############
                chosen_invoice.invoice_doc = SimpleUploadedFile(
                    'Arieshelby Invoice-' + str(chosen_invoice.invoice_id) + '.pdf', pdf_file,
                    content_type='application/pdf')
                chosen_invoice.save()
                ###############################
                #########   GENERATE PDF   ##################

                messages.success(request, f'Added Record Successfully.')
                return redirect('invoice')
        else:
            messages.warning(request, f'Failed to add record.')
            return redirect('invoice')


    else:
        form = InvoiceItemsForm(prefix='form0')
        invoice_form = InvoiceForm()
        all_invoices = Invoice.objects.all()
        return render(request, 'invoice/invoice.html',
                      {'forms': [form], 'invoice_form': invoice_form, 'all_invoice': all_invoices})

@login_required
def invoice_details(request, id):
    chosen_invoice = Invoice.objects.get(id=id)
    listed_invoice_items = InvoiceItems.objects.filter(invoice=chosen_invoice)
    InvoiceItemFormSet = inlineformset_factory(Invoice, InvoiceItems, form=InvoiceItemsForm, extra=0)

    if request.method == "POST":
        form = InvoiceForm(request.POST, instance=chosen_invoice)
        formset = InvoiceItemFormSet(request.POST, instance=chosen_invoice)
        if form.is_valid() and formset.is_valid():
            sub_total_price = 0
            for i in formset:
                cd = i.cleaned_data
                cleaned_price = cd.get('price')
                cleaned_quantity = cd.get('quantity')
                item_price = int(float(cleaned_price)) * int(cleaned_quantity)
                # item_price = cd.get('price') * cd.get('quantity')
                sub_total_price = sub_total_price + item_price

            form_replica = form.save(commit=False)
            form_replica.sub_total = sub_total_price
            form_replica.save()
            # form.save()
            formset.save()


            messages.success(request, f'Updated Invoice Successfully.')
            return redirect('invoice')
        else:
            messages.warning(request, f'Failed to update invoice details, Kindly retry again.')
            return redirect('invoice')
    else:
        form = InvoiceForm(instance=chosen_invoice)
        formset = InvoiceItemFormSet(instance=chosen_invoice)
        invoice_items_form = InvoiceItemsForm()
        context = {
            'invoice_form': form,
            'invoice_items_form': invoice_items_form,
            'QIformset': formset,
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
            QI_form.invoice = selected_invoice
            QI_form.save()
            messages.success(request, f'Successfully added invoice item')
            return redirect(reverse('invoice_details', kwargs={'id': id}))
        else:
            messages.warning(request, f'Failed to add invoice item')
            return redirect('invoice')
    else:
        messages.warning(request, f'Not post request')
        return redirect('invoice')

@login_required
def invoice_delete(request, id):
    selected_invoice = Invoice.objects.get(id=id)
    selected_invoice.delete()
    messages.success(request, f'Invoice deleted successfully')
    return redirect('invoice')



@login_required
def generate_pdf_invoice(request, id):
    selected_invoice = Invoice.objects.get(id=id)
    listed_invoice_items = InvoiceItems.objects.filter(invoice=selected_invoice)
    # Template context variables
    context = {
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
@login_required
def invoice_verification(request, id):
    if Invoice.objects.filter(id=id):
        context = {
            'invoice_id': id,
        }
        messages.success(request, f'Verification Successful. This invoice was generated by Arieshelby LLC')
        return render(request, 'invoice/clients.html', context)
    else:
        context = {
            'invoice_id': "",
        }
        messages.success(request, f'Verification Successful. This invoice was generated by Arieshelby LLC')
        return render(request, 'invoice/clients.html', context)
#############start of invoice#############
#############end of invoice#############



