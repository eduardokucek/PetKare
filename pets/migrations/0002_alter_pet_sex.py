# Generated by Django 4.2.2 on 2023-06-09 20:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pets", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pet",
            name="sex",
            field=models.CharField(
                choices=[
                    ("Male", "Male"),
                    ("Female", "Female"),
                    ("Not Informed", "Not Informed"),
                ],
                default="Not Informed",
                max_length=20,
            ),
        ),
    ]
