# Generated by Django 3.2.3 on 2022-04-10 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('onlfoods', '0009_auto_20220409_0837'),
    ]

    operations = [
        migrations.AddField(
            model_name='orders',
            name='delivered_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]