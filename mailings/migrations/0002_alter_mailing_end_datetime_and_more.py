# Generated by Django 5.1.4 on 2024-12-09 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mailings", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mailing",
            name="end_datetime",
            field=models.DateTimeField(null=True, verbose_name="Дата и время окончания отправки"),
        ),
        migrations.AlterField(
            model_name="mailing",
            name="start_datetime",
            field=models.DateTimeField(null=True, verbose_name="Дата и время первой отправки"),
        ),
    ]