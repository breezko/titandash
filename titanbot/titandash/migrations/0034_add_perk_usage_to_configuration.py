# Generated by Django 2.2.5 on 2019-11-15 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('titandash', '0033_remove_configuration_emulator'),
    ]

    operations = [
        migrations.AddField(
            model_name='botinstance',
            name='next_perk_check',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Next Perk Check'),
        ),
        migrations.AddField(
            model_name='configuration',
            name='enable_adrenaline_rush',
            field=models.BooleanField(default=False, help_text='Enable the adrenaline rush perk.', verbose_name='Enable Adrenaline Rush'),
        ),
        migrations.AddField(
            model_name='configuration',
            name='enable_clan_crate',
            field=models.BooleanField(default=False, help_text='Enable the clan crate perk.', verbose_name='Enable Clan Crate'),
        ),
        migrations.AddField(
            model_name='configuration',
            name='enable_doom',
            field=models.BooleanField(default=False, help_text='Enable the doom perk.', verbose_name='Enable Doom'),
        ),
        migrations.AddField(
            model_name='configuration',
            name='enable_make_it_rain',
            field=models.BooleanField(default=False, help_text='Enable the make it rain perk.', verbose_name='Enable Make It Rain'),
        ),
        migrations.AddField(
            model_name='configuration',
            name='enable_mana_potion',
            field=models.BooleanField(default=False, help_text='Enable the mana potion perk.', verbose_name='Enable Mana Potion'),
        ),
        migrations.AddField(
            model_name='configuration',
            name='enable_perk_diamond_purchase',
            field=models.BooleanField(default=False, help_text="Enable the ability to purchase a perk with diamonds if you don't currently have one.", verbose_name='Enable Perk Diamond Purchase'),
        ),
        migrations.AddField(
            model_name='configuration',
            name='enable_perk_only_tournament',
            field=models.BooleanField(default=False, help_text='Enable the ability to only check and use perks when a tournament is joined initially.', verbose_name='Enable Perks Only During Tournaments'),
        ),
        migrations.AddField(
            model_name='configuration',
            name='enable_perk_usage',
            field=models.BooleanField(default=False, help_text='Enable the ability to use and purchase perks in game.', verbose_name='Enable Perks'),
        ),
        migrations.AddField(
            model_name='configuration',
            name='enable_power_of_swiping',
            field=models.BooleanField(default=False, help_text='Enable the power of swiping perk.', verbose_name='Enable Power Of Swiping'),
        ),
        migrations.AddField(
            model_name='configuration',
            name='use_perk_on_prestige',
            field=models.CharField(choices=[('none', 'None'), ('power_of_swiping', 'Power Of Swiping'), ('adrenaline_rush', 'Adrenaline Rush'), ('make_it_rain', 'Make It Rain'), ('mana_potion', 'Mana Potion'), ('doom', 'Doom'), ('clan_crate', 'Clan Crate')], default='none', help_text='Choose a specific perk that you would like to use or purchase (if enabled) when a prestige occurs.', max_length=255, verbose_name='Use Perk On Prestige'),
        ),
        migrations.AddField(
            model_name='configuration',
            name='use_perks_every_x_hours',
            field=models.PositiveIntegerField(default=12, help_text='Specify the amount of hours to wait in between each perk usage process.', verbose_name='Use Perks Every X Hours'),
        ),
        migrations.AddField(
            model_name='configuration',
            name='use_perks_on_start',
            field=models.BooleanField(default=False, help_text='Should perks be used or purchased when a session is started.', verbose_name='Use Perks On Session Start'),
        ),
    ]
