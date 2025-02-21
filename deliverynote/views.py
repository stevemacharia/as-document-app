from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import DeliveryNoteForm, DeliveryNoteItemsForm
from .models import Client, DeliveryNote, DeliveryNoteItems
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
import os
from django.contrib.auth.decorators import login_required
from accounts.models import BusinessAccount
from invoice.models import Invoice, InvoiceItems
from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.utils import timezone
# Create your views here.


@login_required
def delivery_note(request):
    form = DeliveryNoteItemsForm(prefix='form0')
    delivery_note_form = DeliveryNoteForm()
    delivery_note_form.set_request(request)
    
    business_account = request.session.get('selected_business_account')
    selected_business_account = BusinessAccount.objects.get(id=business_account) 
    draft_delivery_notes = DeliveryNote.objects.filter(business_account=selected_business_account, status=False)
    final_delivery_notes = DeliveryNote.objects.filter(business_account=selected_business_account, status=True)
    final_invoices = Invoice.objects.filter(business_account=selected_business_account, status=True)
    final_delivery_notes_count = DeliveryNote.objects.filter(business_account=selected_business_account, status=True).count()
    draft_delivery_notes_count = DeliveryNote.objects.filter(business_account=selected_business_account, status=False).count()

    if request.method == 'POST':
        delivery_note_form = DeliveryNoteForm(request.POST)
        delivery_note_form.set_request(request)
        # form = InvoiceForm(request.POST)
        # form.set_request(request)  # Ensure this is called on InvoiceForm

        form_count = int(request.POST.get('form_count', 1))
        forms = [DeliveryNoteItemsForm(request.POST, request.FILES, prefix=f'form{i}') for i in range(form_count)]
        x = str(uuid.uuid4())[:5]

        if delivery_note_form.is_valid() and all(f.is_valid() for f in forms):

            dn_form = delivery_note_form.save(commit=False)
            # Retrieve a business account value from the session
            dn_form.business_account = selected_business_account
            client_initials = str(dn_form.client)[:3]
            delivery_note_id_smaller = f'AS{client_initials}{x}'
            dn_form.dnote_id = delivery_note_id_smaller.upper()
            new_delivery_note_id = dn_form.dnote_id

            ###############QR CODE GENERATION#########
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            data = "www.document.arieshelby.com/deliverynote/delivery_note_verification/"+new_delivery_note_id
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
            dn_form.qr_code_image.save(file_name, File(buffer), save=False)

            dn_form.save()
            
            chosen_delivery_note = DeliveryNote.objects.get(dnote_id=new_delivery_note_id)

            sub_total_price = 0
            # Process each DeliveryNoteItemsForm
            for form in forms:
                item = form.save(commit=False)
                item.dnote = chosen_delivery_note

                item.save()

            chosen_delivery_note.sub_total = sub_total_price
            chosen_delivery_note.save()

            #########   GENERATE PDF   #############

            template_name = get_template('deliverynote/delivery_note_doc.html')
            listed_delivery_note_items = DeliveryNoteItems.objects.filter(dnote=chosen_delivery_note)
            selected_business_account = request.session.get('selected_business_account')
            context = {
                'selected_delivery_note': chosen_delivery_note,
                'listed_delivery_note_items': listed_delivery_note_items,
                'selected_business_account': selected_business_account,
            }
            rendered_html = template_name.render(context)
            pdf_file = HTML(string=rendered_html).write_pdf()

            ########## Update Delivery Note Model ##############
            chosen_delivery_note.dnote_doc = SimpleUploadedFile(
                f'{selected_business_account} Delivery Note-{chosen_delivery_note.dnote_id}.pdf', pdf_file,
                content_type='application/pdf')
            chosen_delivery_note.save()
            ###############################
            #########   GENERATE PDF   ##################

            messages.success(request, f'Delivery note saved Successfully.')
            return redirect('delivery_note')
        else:
            # Gather errors for the main form and each items form
            error_messages = []
            if delivery_note_form.errors:
                for field, errors in delivery_note_form.errors.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")
            for form in forms:
                if form.errors:
                    for field, errors in form.errors.items():
                        for error in errors:
                            error_messages.append(f"{field} (item): {error}")

            # Pass error messages to the template
            return render(request, 'deliverynote/delivery_note.html', {
                'forms': forms,
                'delivery_note_form': delivery_note_form,
                'final_delivery_notes_count': final_delivery_notes_count,
                'draft_delivery_notes_count': draft_delivery_notes_count,
                'draft_delivery_notes': draft_delivery_notes,
                'final_delivery_notes': final_delivery_notes,
                'final_invoices': final_invoices,
                'error_messages': error_messages
            })

    else:

        return render(request, 'deliverynote/delivery_note.html',{
            'forms': [form],
            'delivery_note_form': delivery_note_form,
            'final_delivery_notes_count': final_delivery_notes_count,
            'draft_delivery_notes_count': draft_delivery_notes_count,
            'draft_delivery_notes': draft_delivery_notes,
            'final_delivery_notes': final_delivery_notes,
            'final_invoices': final_invoices,
            
            })


@login_required
def delivery_note_details(request, id):
    chosen_delivery_note = DeliveryNote.objects.get(id=id)
    listed_delivery_note_items = DeliveryNoteItems.objects.filter(dnote=chosen_delivery_note)

    DeliveryNoteItemFormSet = inlineformset_factory(DeliveryNote, DeliveryNoteItems, can_delete=True,  form=DeliveryNoteItemsForm, extra=0)

    form = DeliveryNoteForm(instance=chosen_delivery_note)
    
    form.set_request(request)
    formset = DeliveryNoteItemFormSet(instance=chosen_delivery_note)
    delivery_note_items_form = DeliveryNoteItemsForm()

    if request.method == "POST":
        form = DeliveryNoteForm(request.POST, instance=chosen_delivery_note)
        form.set_request(request)
        formset = DeliveryNoteItemFormSet(request.POST, request.FILES, instance=chosen_delivery_note)
        if form.is_valid() and formset.is_valid():

            form.save()
            formset.save()
            messages.success(request, f'Updated Delivery note Successfully.')
            return redirect('delivery_note')
        else:
            return render(request, 'deliverynote/delivery_note_details.html',
                    {
                        'delivery_note_form': form,
                        'delivery_note_items_form': delivery_note_items_form,
                        'DeliveryNoteformset': formset,
                        'chosen_delivery_note': chosen_delivery_note
                    })
    else:

        context = {
                    'delivery_note_form': form,
                    'delivery_note_items_form': delivery_note_items_form,
                    'DeliveryNoteformset': formset,
                    'chosen_delivery_note': chosen_delivery_note
                }
    return render(request, 'deliverynote/delivery_note_details.html', context)

@login_required
def add_delivery_note_item(request, id):
    selected_delivery_note = DeliveryNote.objects.get(id=id)
    if request.method == "POST":
        delivery_note_item_form = DeliveryNoteItemsForm(request.POST, request.FILES)
        if delivery_note_item_form.is_valid():

            DI_form = delivery_note_item_form.save(commit=False)

            # price = delivery_note_item_form.cleaned_data['price']
            quantity = delivery_note_item_form.cleaned_data['quantity']


            # item_price = int(float(price)) * int(quantity)
            # total_iten_price = item_price

            # new_sub_total_price = selected_delivery_note.sub_total + total_iten_price

            # selected_delivery_note.sub_total = new_sub_total_price
            selected_delivery_note.save()
  

            DI_form.dnote = selected_delivery_note
            DI_form.save()
            messages.success(request, f'Successfully added delivery note item')
            return redirect(reverse('delivery_note_details', kwargs={'id': id}))
        else:
            messages.warning(request, f'Failed to add delivery note item')
            return redirect('delivery_note')
    else:
        messages.warning(request, f'Not post request')
        return redirect('delivery_note')

@login_required
def delivery_note_delete(request, id):
    selected_delivery_note = DeliveryNote.objects.get(id=id)
    selected_delivery_note.delete()
    messages.success(request, f'Delivery note deleted successfully')
    return redirect('delivery_note')

@login_required
def convert_invoice_to_delivery_note(request, id):
    # Fetch the quotation instance
    invoice = get_object_or_404(Invoice, id=id)
    x = str(uuid.uuid4())[:5]
    client_initials = str(invoice.client)[:3]
    new_dnote_id = 'AS-' + str(client_initials) + '-' + x
    # Create a new Invoice instance with Quotation details
    delivery_note = DeliveryNote.objects.create(
        dnote_id = new_dnote_id,
        client=invoice.client,
        business_account=invoice.business_account,
        status=invoice.status,
        dnote_doc=invoice.invoice_doc,
        data=invoice.data,
        qr_code_image=invoice.qr_code_image,
        # note=invoice.note,
        submission_date=timezone.now(),
        # taxable=invoice.taxable,
        # sub_total=invoice.sub_total,
        # total_price=invoice.total_price,
    )

    # Copy each InvoiceItem to DeliveryItem
    invoice_items = InvoiceItems.objects.filter(invoice=invoice)
    for item in invoice_items:
        DeliveryNoteItems.objects.create(
            dnote=delivery_note,
            item=item.item,
            item_description=item.item_description,
            item_image=item.item_image,
            quantity=item.quantity,
            # price=item.price,
        )

    # Optionally update the quotation status or other fields
    invoice.status = True  # Mark the quotation as converted
    invoice.save()

    # Redirect to the invoice detail page with the new invoice ID
    return redirect(reverse('delivery_note_details', args=[delivery_note.id]))



@login_required
def generate_pdf_delivery_note(request, id):
    selected_delivery_note = DeliveryNote.objects.get(id=id)
    listed_delivery_note_items = DeliveryNoteItems.objects.filter(dnote=selected_delivery_note)
    business_account = request.session.get('selected_business_account')
    selected_business_account = BusinessAccount.objects.get(id=business_account) 
    # Template context variables
    context = {
        'selected_delivery_note': selected_delivery_note,
        'listed_delivery_note_items': listed_delivery_note_items,
        'selected_business_account': selected_business_account,
    }

    # Path to your image
    qr_code_url = selected_delivery_note.qr_code_image.url
    # qr_code_path = os.path.join('static/images', 'qr-code.png')
    # qr_code_url = request.build_absolute_uri(qr_code_path)

    # Update context with the image URL
    context['qr_code_url'] = qr_code_url

    # Render the HTML template with context
    html_string = render_to_string('deliverynote/delivery_note_doc.html', context)

    # Create a PDF
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf(stylesheets=[CSS(string='@page { size: A4; margin: 0.5cm }')])

    ########## Update Delivery Note Model ##############
    selected_delivery_note.dnote_doc = SimpleUploadedFile(
        selected_business_account.name + selected_delivery_note.dnote_id + '.pdf', pdf, content_type='application/pdf')
    selected_delivery_note.save()
    ################################################

    # Create a response object and specify the PDF content type
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename= '+ selected_business_account.name+'-Delivery Note-' + selected_delivery_note.dnote_id + '.pdf'

    return response

@login_required
def delivery_note_verification(request, id):
    d_note = DeliveryNote.objects.get(id=id)
    if DeliveryNote.objects.filter(id=id):
        context = {
            'delivery_note_id': id,
        }
        messages.success(request, f'Verification Successful. This Delivery Note was generated by { d_note.business_account }')
        return render(request, 'deliverynote/clients.html', context)
    else:
        context = {
            'delivery_note_id': "",
        }
        messages.warning(request, f'Verification Failed. This Delivery Note was NOT generated by { d_note.business_account }')
        return render(request, 'deliverynote/clients.html', context)





