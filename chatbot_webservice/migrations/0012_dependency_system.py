# Generated by Django 3.1.1 on 2020-11-01 22:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot_webservice', '0011_service_system'),
    ]

    operations = [
        migrations.AddField(
            model_name='dependency',
            name='system',
            field=models.CharField(default='accounting-system', max_length=200),
            preserve_default=False,
        ),
    ]
