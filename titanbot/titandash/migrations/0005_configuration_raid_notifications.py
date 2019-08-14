# Generated by Django 2.1.7 on 2019-08-10 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('titandash', '0004_botinstance_last_prestige'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuration',
            name='enable_raid_notifications',
            field=models.BooleanField(default=False, help_text='Should notifications be sent to a user when a clan raid starts or attacks are ready.', verbose_name='Enable Raid Notifications'),
        ),
        migrations.AddField(
            model_name='configuration',
            name='raid_notifications_check_every_x_minutes',
            field=models.PositiveIntegerField(default=30, help_text='Determine how many minutes between each raid notifications check.', verbose_name='Check For Raid Notification Every X Minutes'),
        ),
        migrations.AddField(
            model_name='configuration',
            name='raid_notifications_check_on_start',
            field=models.BooleanField(default=False, help_text='Should a raid notifications check take place when a session is started.', verbose_name='Check For Raid Notification On Session Start'),
        ),
        migrations.AddField(
            model_name='configuration',
            name='raid_notifications_twilio_account_sid',
            field=models.CharField(blank=True, help_text='Specify the account sid associated with your twilio account.', max_length=255, null=True, verbose_name='Raid Notifications Twilio Account SID'),
        ),
        migrations.AddField(
            model_name='configuration',
            name='raid_notifications_twilio_auth_token',
            field=models.CharField(blank=True, help_text='Specify the auth token associated with your twilio account.', max_length=255, null=True, verbose_name='Raid Notifications Twilio Auth Token'),
        ),
        migrations.AddField(
            model_name='configuration',
            name='raid_notifications_twilio_from_number',
            field=models.CharField(blank=True, help_text='Specify the from number associated with your twilio account', max_length=255, null=True, verbose_name='Raid Notifications Twilio From Number'),
        ),
        migrations.AddField(
            model_name='configuration',
            name='raid_notifications_twilio_to_number',
            field=models.CharField(blank=True, help_text='Specify the phone number you would like to receieve notifications at (ex: +19991234567)', max_length=255, null=True, verbose_name='Raid Notifications Twilio To Number'),
        ),
    ]
