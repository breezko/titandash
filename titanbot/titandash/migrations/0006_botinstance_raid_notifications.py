# Generated by Django 2.1.7 on 2019-08-14 00:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('titandash', '0005_configuration_raid_notifications'),
    ]

    operations = [
        migrations.AddField(
            model_name='botinstance',
            name='next_raid_attack_reset',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Next Raid Attacks Reset'),
        ),
        migrations.AddField(
            model_name='botinstance',
            name='next_raid_notifications_check',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Next Raid Notifications Check'),
        ),
    ]
