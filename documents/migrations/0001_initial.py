# Generated by Django 4.2.13 on 2024-05-24 17:57

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=400)),
                ('postal_address', models.CharField(max_length=400)),
            ],
            options={
                'verbose_name': 'Clients',
                'verbose_name_plural': 'Clients',
            },
        ),
        migrations.CreateModel(
            name='QRCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('qr_image', models.ImageField(blank=True, null=True, upload_to='qr_codes/')),
            ],
        ),
        migrations.CreateModel(
            name='Quotation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quotation_id', models.CharField(blank=True, max_length=100)),
                ('status', models.BooleanField(blank=True, default='False', null=True)),
                ('quotation_doc', models.FileField(blank=True, default='default.pdf', max_length=500, null=True, upload_to='quotation_docs')),
                ('submission_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('sub_total', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('total_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='documents.client')),
            ],
        ),
        migrations.CreateModel(
            name='QuotationItems',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item', models.CharField(max_length=300)),
                ('item_description', models.CharField(max_length=800)),
                ('quantity', models.IntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=15)),
                ('quotation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='documents.quotation')),
            ],
        ),
        migrations.CreateModel(
            name='InvoiceItems',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item', models.CharField(max_length=300)),
                ('item_description', models.CharField(max_length=800)),
                ('quantity', models.IntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=15)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='documents.quotation')),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_id', models.CharField(blank=True, max_length=100)),
                ('status', models.BooleanField(blank=True, default='False', null=True)),
                ('quotation_doc', models.FileField(blank=True, default='default.pdf', max_length=500, null=True, upload_to='quotation_docs')),
                ('submission_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('sub_total', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True)),
                ('total_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='documents.client')),
            ],
        ),
    ]