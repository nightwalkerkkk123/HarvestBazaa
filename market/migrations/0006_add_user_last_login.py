# Generated manually to add last_login field to User model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0005_add_specialty_image_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True, verbose_name='last login'),
        ),
    ]