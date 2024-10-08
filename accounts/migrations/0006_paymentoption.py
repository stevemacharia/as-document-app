# Generated by Django 4.2.14 on 2024-10-04 19:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_businessaccount_logo'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=300)),
                ('account_no', models.CharField(blank=True, max_length=100, null=True)),
                ('Business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.businessaccount')),
            ],
        ),
    ]
