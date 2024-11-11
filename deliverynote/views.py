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
from invoice.models import Invoice 
from decimal import Decimal
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

    if request.method == 'POST':
        delivery_note_form = DeliveryNoteForm(request.POST)
        delivery_note_form.set_request(request)
        # form = InvoiceForm(request.POST)
        # form.set_request(request)  # Ensure this is called on InvoiceForm

        form_count = int(request.POST.get('form_count', 1))
        forms = [DeliveryNoteItemsForm(request.POST, prefix=f'form{i}') for i in range(form_count)]
        x = str(uuid.uuid4())[:5]

        if delivery_note_form.is_valid() and all(f.is_valid() for f in forms):

            dn_form = delivery_note_form.save(commit=False)
            # Retrieve a business account value from the session
            dn_form.business_account = selected_business_account
            client_initials = str(dn_form.client)[:3]
            delivery_note_id_smaller = f'AS{client_initials}{x}'
            dn_form.delivery_note_id = delivery_note_id_smaller.upper()
            new_delivery_note_id = dn_form.delivery_note_id

            ###############QR CODE GENERATION#########
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            data = "www.document.arieshelby.com/invoice/invoice_verification/"+new_delivery_note_id
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
                item_price = item.price * item.quantity
                sub_total_price += item_price
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

            ########## Update Invoice Model ##############
            chosen_delivery_note.dnote_doc = SimpleUploadedFile(
                f'Arieshelby Delivery Note-{chosen_delivery_note.dnote_id}.pdf', pdf_file,
                content_type='application/pdf')
            chosen_delivery_note.save()
            ###############################
            #########   GENERATE PDF   ##################

            messages.success(request, f'Invoice saved Successfully.')
            return redirect('invoice')
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
                'draft_delivery_notes': draft_delivery_notes,
                'final_delivery_notes': final_delivery_notes,
                'final_invoices': final_invoices,
                'error_messages': error_messages
            })

    else:

        return render(request, 'deliverynote/delivery_note.html',{
            'forms': [form],
            'delivery_note_form': delivery_note_form,
            'draft_delivery_notes': draft_delivery_notes,
            'final_delivery_notes': final_delivery_notes,
            'final_invoices': final_invoices,
            
            })



def delivery_note_details(request, id):
    chosen_delivery_note = DeliveryNote.objects.get(id=id)
    listed_delivery_note_items = DeliveryNoteItems.objects.filter(dnote=chosen_delivery_note)
    DeliveryNoteItemFormSet = inlineformset_factory(DeliveryNote, DeliveryNoteItems, form=DeliveryNoteItemsForm, extra=0)

    if request.method == "POST":
        form = DeliveryNoteForm(request.POST, instance=chosen_delivery_note)
        formset = DeliveryNoteItemFormSet(request.POST, instance=chosen_delivery_note)
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


            messages.success(request, f'Updated Delivery note Successfully.')
            return redirect('delivery_note')
        else:
            messages.warning(request, f'Failed to update Delivery note details, Kindly retry again.')
            return redirect('delivery_note')
    else:
        form = DeliveryNoteForm(instance=chosen_delivery_note)
        formset = DeliveryNoteItemFormSet(instance=chosen_delivery_note)
        delivery_note_items_form = DeliveryNoteItemsForm()
        context = {
            'delivery_note_form': form,
            'delivery_note_items_form': delivery_note_items_form,
            'DIformset': formset,
            'chosen_delivery_note': chosen_delivery_note
        }
    return render(request, 'deliverynote/delivery_note_details.html', context)

@login_required
def add_delivery_note_item(request, id):
    selected_delivery_note = DeliveryNote.objects.get(id=id)
    if request.method == "POST":
        delivery_note_item_form = DeliveryNoteItemsForm(request.POST)
        if delivery_note_item_form.is_valid():

            DI_form = delivery_note_item_form.save(commit=False)

            price = delivery_note_item_form.cleaned_data['price']
            quantity = delivery_note_item_form.cleaned_data['quantity']


            item_price = int(float(price)) * int(quantity)
            total_iten_price = item_price

            new_sub_total_price = selected_delivery_note.sub_total + total_iten_price

            selected_delivery_note.sub_total = new_sub_total_price
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
        'Arieshelby Delivery note-' + selected_delivery_note.dnote_id + '.pdf', pdf, content_type='application/pdf')
    selected_delivery_note.save()
    ################################################

    # Create a response object and specify the PDF content type
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Arieshelby Delivery Note-' + selected_delivery_note.dnote_id + '.pdf"'

    return response

@login_required
def delivery_note_verification(request, id):
    if DeliveryNote.objects.filter(id=id):
        context = {
            'delivery_note_id': id,
        }
        messages.success(request, f'Verification Successful. This Delivery Note was generated by Arieshelby LLC')
        return render(request, 'deliverynote/clients.html', context)
    else:
        context = {
            'delivery_note_id': "",
        }
        messages.success(request, f'Verification Successful. This Delivery Note was generated by Arieshelby LLC')
        return render(request, 'deliverynote/clients.html', context)





