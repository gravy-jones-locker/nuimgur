# Generated by Django 3.1.7 on 2021-03-22 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demo', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imagefile',
            name='in_file',
            field=models.ImageField(upload_to='demo/static/'),
        ),
    ]
