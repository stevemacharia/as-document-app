# Generated by Django 4.2.14 on 2024-10-30 17:44

from django.db import migrations, models
import django.db.models.deletion
import invoice.models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_paymentoption_options'),
        ('invoice', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='payment_account',
            field=models.ForeignKey(default=invoice.models.get_default_payment_option_account, on_delete=django.db.models.deletion.CASCADE, to='accounts.paymentoption'),
        ),
    ]