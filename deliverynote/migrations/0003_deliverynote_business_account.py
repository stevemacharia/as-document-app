# Generated by Django 4.2.14 on 2024-09-16 18:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('deliverynote', '0002_remove_deliverynote_business_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliverynote',
            name='business_account',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='accounts.businessaccount'),
            preserve_default=False,
        ),
    ]