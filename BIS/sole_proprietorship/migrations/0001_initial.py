# Generated by Django 3.1 on 2021-06-25 12:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Accounts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account', models.CharField(max_length=250)),
                ('normal_balance', models.CharField(choices=[('Debit', 'Debit'), ('Credit', 'Credit')], default='Debit', max_length=7)),
                ('account_type', models.CharField(choices=[('Assest', 'Assest'), ('Investment', 'Investment'), ('liabilities', 'liabilities'), ('Revenue', 'Revenue'), ('Expenses', 'Expenses'), ('Drawings', 'Drawings')], default='Assest', max_length=50)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Account',
                'verbose_name_plural': 'Accounts',
            },
        ),
        migrations.CreateModel(
            name='ReportingPeriodConfig',
            fields=[
                ('owner', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='fs_reporting_period', serialize=False, to='auth.user')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('comment', models.CharField(blank=True, max_length=2500, null=True)),
                ('status', models.IntegerField(blank=True, choices=[(1, 'Purchase Inventory'), (2, 'Purchase return'), (3, 'Purchase Allowance'), (4, 'Freight in'), (5, 'Pay Invoice')], null=True)),
                ('inventory_price', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.inventoryprice')),
                ('inventory_return', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.inventoryreturn')),
                ('pay_invoice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.payinvoice')),
                ('purchase_inventory', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.purchaseinventory')),
            ],
        ),
        migrations.CreateModel(
            name='Journal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.FloatField()),
                ('transaction_type', models.CharField(choices=[('Debit', 'Debit'), ('Credit', 'Credit')], default='Debit', max_length=7)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sole_proprietorship.accounts')),
                ('transaction', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='sole_proprietorship.transaction')),
            ],
        ),
        migrations.AddConstraint(
            model_name='accounts',
            constraint=models.UniqueConstraint(fields=('account', 'owner'), name='unique_account'),
        ),
    ]
