# Generated by Django 4.0.4 on 2022-05-26 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='attendance',
            options={'ordering': ['-date']},
        ),
        migrations.RenameField(
            model_name='attendance',
            old_name='user',
            new_name='student',
        ),
        migrations.AlterField(
            model_name='attendance',
            name='path_to_picture',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]