from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0002_apitoken'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='fcm_token',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
    ]



