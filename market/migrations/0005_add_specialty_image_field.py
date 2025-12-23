# Generated manually to add image field to Specialty model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0004_alter_user_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='specialty',
            name='image',
            field=models.ImageField(blank=True, default='default-product.jpg', null=True, upload_to='product_images/'),
        ),
    ]