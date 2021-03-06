# Generated by Django 4.0.3 on 2022-04-10 01:06

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('username', models.CharField(max_length=50)),
                ('password', models.CharField(max_length=16)),
                ('balance', models.FloatField(default=0.0)),
            ],
        ),
        migrations.CreateModel(
            name='Transactions',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('transaction_type', models.CharField(choices=[('borrow', 'borrow'), ('lend', 'lend')], max_length=25)),
                ('transaction_date', models.DateTimeField(auto_now_add=True)),
                ('transaction_status', models.CharField(choices=[('paid', 'paid'), ('unpaid', 'unpaid')], max_length=25)),
                ('transaction_amount', models.FloatField()),
                ('reason', models.CharField(max_length=100, null=True)),
                ('transaction_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transaction_from', to='api.users')),
                ('transaction_with', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transaction_with', to='api.users')),
            ],
        ),
    ]
