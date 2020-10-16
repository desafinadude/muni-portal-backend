# Generated by Django 2.2.10 on 2020-10-16 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20201010_1719'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactdetail',
            name='annotation',
            field=models.CharField(blank=True, help_text='Optional public note of what this contact is for, e.g. "Senior Library Assistant Ms A Jones" or "John SmithCell phone number"', max_length=250, null=True),
        ),
    ]
