# Generated by Django 5.0.4 on 2024-04-18 05:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('function_registry', '0005_alter_function_language'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='function',
            name='timeout',
        ),
    ]