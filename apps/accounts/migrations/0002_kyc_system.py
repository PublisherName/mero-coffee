# Generated migration for KYC system

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(
                choices=[('creator', 'Creator'), ('supporter', 'Supporter'), ('admin', 'Admin')],
                default='supporter',
                max_length=20
            ),
        ),
        migrations.CreateModel(
            name='KYC',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(blank=True, max_length=255)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('address', models.TextField(blank=True)),
                ('city', models.CharField(blank=True, max_length=100)),
                ('country', models.CharField(blank=True, max_length=100)),
                ('id_type', models.CharField(blank=True, max_length=50)),
                ('id_number', models.CharField(blank=True, max_length=100)),
                ('status', models.CharField(
                    choices=[('not_filed', 'Not Filed'), ('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
                    default='not_filed',
                    max_length=20
                )),
                ('rejection_reason', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='kyc', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
