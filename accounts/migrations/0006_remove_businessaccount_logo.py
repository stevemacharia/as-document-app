# Generated by Django 4.2.14 on 2024-09-06 18:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_businessaccount_logo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='businessaccount',
            name='logo',
        ),
    ]