# Generated by Django 2.1.7 on 2019-12-03 03:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('image', '0002_auto_20191203_0130'),
    ]

    operations = [
        migrations.AddField(
            model_name='simage',
            name='model',
            field=models.CharField(choices=[('1', 'Red Neuronal 1'), ('2', 'Red Neuronal 2'), ('3', 'Naive Bayes 1'), ('4', 'Naive Bayes 2')], default='1', max_length=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='simage',
            name='status',
            field=models.CharField(choices=[('1', 'Processing'), ('2', 'Processed')], default='1', max_length=2),
            preserve_default=False,
        ),
    ]
