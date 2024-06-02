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
import os
# Create your views here.
def index(request):
    quotations = Quotation.objects.all()
    context = {
        'all_quotations': quotations,
    }
    return render(request, 'documents/index.html', context)


def quotations(request):
    if request.method == 'POST':
        quotation_form = QuotationForm(request.POST)
        x = str(uuid.uuid4())[:5]

        if quotation_form.is_valid():
            q_form = quotation_form.save(commit=False)

            client = q_form.client
            # string = "Hello world"
            # string[:3]
            client_initials = str(client)[:3]
            q_form.quotation_id = 'AS/' + str(client_initials) + '/' + x

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
            chosen_quotation = Quotation.objects.get(quotation_id=new_id)

            forms = []
            form_count = int(request.POST.get('form_count', 1))
            # quotation_forms = [QuotationForm(request.POST, prefix=str(i)) for i in range(int(request.POST['form_count']))]
            sub_total_price = 0
            for i in range(form_count):
                form = QuotationItemsForm(request.POST, prefix='form{}'.format(i))
                form_replica = form.save(commit=False)
                item_price = form_replica.price * form_replica.quantity
                sub_total_price = sub_total_price + item_price
                if form.is_valid():
                    forms.append(form)
                else:
                    quotation_form = QuotationForm()
                    quotation_items_form = QuotationItemsForm()
                    context = {
                        'quotation_form': quotation_form,
                        'quotation_items_form': quotation_items_form,
                    }
                    # If any form is invalid, render the template with all forms
                    return render(request, 'documents/quotations.html', context)
            main_sub_total_price = sub_total_price
            chosen_quotation.sub_total = main_sub_total_price
            chosen_quotation.save()
            if forms:
                # If all forms are valid, save them
                for form in forms:
                    Q_Items_form = form.save(commit=False)
                    Q_Items_form.quotation = chosen_quotation
                    Q_Items_form.save()

                #########   GENERATE PDF   #############
                # chosen__quotation = Quotation.objects.get(id=id)
                template_name = get_template('documents/quotation_doc.html')
                listed_quotation_items = QuotationItems.objects.filter(quotation=chosen_quotation)
                context = {
                    'selected_quotation': chosen_quotation,
                    'listed_quotation_items': listed_quotation_items,
                }
                rendered_html = template_name.render(context)
                pdf_file = HTML(string=rendered_html).write_pdf()

                ########## Update Quotation Model ##############
                chosen_quotation.quotation_doc = SimpleUploadedFile(
                    'Arieshelby Quotation-' + str(chosen_quotation.quotation_id) + '.pdf', pdf_file,
                    content_type='application/pdf')
                chosen_quotation.save()
                ###############################
                #########   GENERATE PDF   ##################

                messages.success(request, f'Added Record Successfully.')
                return redirect('quotations')
        else:
            messages.warning(request, f'Failed to add record.')
            return redirect('quotations')


    else:
        form = QuotationItemsForm(prefix='form0')
        quotation_form = QuotationForm()
        all_quotations = Quotation.objects.all()
        # quotation_items_form = QuotationItemsForm(prefix='form0')
        # context = {
        #     'form': [quotation_items_form],
        #     'quotation_form': quotation_form,
        # }
        return render(request, 'documents/quotations.html',
                      {'forms': [form], 'quotation_form': quotation_form, 'all_quotations': all_quotations})


def quotation_details(request, id):
    chosen_quotation = Quotation.objects.get(id=id)
    listed_quotation_items = QuotationItems.objects.filter(quotation=chosen_quotation)
    QuotationItemFormSet = inlineformset_factory(Quotation, QuotationItems, form=QuotationItemsForm, extra=0)

    if request.method == "POST":
        form = QuotationForm(request.POST, instance=chosen_quotation)
        formset = QuotationItemFormSet(request.POST, instance=chosen_quotation)
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


            messages.success(request, f'Updated Quotation Successfully.')
            return redirect('quotations')
        else:
            messages.warning(request, f'Failed to update quotation details, Kindly retry again.')
            return redirect('quotations')
    else:
        form = QuotationForm(instance=chosen_quotation)
        formset = QuotationItemFormSet(instance=chosen_quotation)
        quotation_items_form = QuotationItemsForm()
        context = {
            'quotation_form': form,
            'quotation_items_form': quotation_items_form,
            'QIformset': formset,
            'chosen_quotation': chosen_quotation
        }
    return render(request, 'documents/quotation_details.html', context)


def add_quotation_item(request, id):
    selected_quotation = Quotation.objects.get(id=id)
    if request.method == "POST":
        quotation_item_form = QuotationItemsForm(request.POST)
        if quotation_item_form.is_valid():
            QI_form = quotation_item_form.save(commit=False)
            QI_form.quotation = selected_quotation
            QI_form.save()
            messages.success(request, f'Successfully added quotation item')
            return redirect(reverse('quotation_details', kwargs={'id': id}))
        else:
            messages.warning(request, f'Failed to add quotation item')
            return redirect('quotations')
    else:
        messages.warning(request, f'Not post request')
        return redirect('quotations')


def quotation_delete(request, id):
    selected_quotation = Quotation.objects.get(id=id)
    selected_quotation.delete()
    messages.success(request, f'Quotation deleted successfully')
    return redirect('quotations')




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


def client_delete(request, id):
    selected_client = Client.objects.get(id=id)
    selected_client.delete()
    messages.success(request, f'Client details deleted successfully')
    return redirect('clients')

def generate_pdf_quotation(request, id):
    selected_quotation = Quotation.objects.get(id=id)
    listed_quotation_items = QuotationItems.objects.filter(quotation=selected_quotation)
    # Template context variables
    context = {
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
        'Arieshelby Quotation-' + selected_quotation.quotation_id + '.pdf', pdf, content_type='application/pdf')
    selected_quotation.save()
    ################################################

    # Create a response object and specify the PDF content type
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Arieshelby Quotation-' + selected_quotation.quotation_id + '.pdf"'

    return response

def quotation_verification(request, id):
    if Quotation.objects.filter(id=id):
        context = {
            'quotation_id': id,
        }
        messages.success(request, f'Verification Successful. This quotations was generated by Arieshelby LLC')
        return render(request, 'documents/clients.html', context)
    else:
        context = {
            'quotation_id': "",
        }
        messages.success(request, f'Verification Successful. This quotations was generated by Arieshelby LLC')
        return render(request, 'documents/clients.html', context)
#############start of invoices#############
#############end of invoices#############



