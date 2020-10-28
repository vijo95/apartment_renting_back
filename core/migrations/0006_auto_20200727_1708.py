# Generated by Django 3.0.8 on 2020-07-27 20:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20200722_2338'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='installments',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='total_amount',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
