# Generated by Django 3.1 on 2021-07-13 21:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0012_auto_20210712_1144'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesreturn',
            name='sale',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='inventory.sale'),
            preserve_default=False,
        ),
    ]
