# Generated by Django 3.1.1 on 2020-10-11 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot_webservice', '0002_servicedata'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicedata',
            name='uri',
            field=models.CharField(default=None, max_length=300),
            preserve_default=False,
        ),
    ]
