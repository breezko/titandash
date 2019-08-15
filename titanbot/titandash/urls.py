from django.urls import path

from . import views


urlpatterns = [
    # MAIN DASHBOARD.
    path('', views.dashboard, name='dashboard'),

    # SECONDARY URLS.
    path('project_settings', views.project_settings, name='settings'),
    path('all_prestiges', views.all_prestiges, name='all_prestiges'),
    path('artifacts', views.artifacts, name='artifacts'),
    path('statistics', views.statistics, name='statistics'),
    path('shortcuts', views.shortcuts, name='shortcuts'),

    # SESSIONS.
    path('sessions/', views.sessions, name='sessions'),
    path('sessions/<uuid>/', views.session, name='session'),

    # RAIDS.
    path('raids/', views.raids, name='raids'),
    path('raid/<digest>/', views.raid, name='raid'),

    # LOGS.
    path('logs/<pk>/', views.log, name='log'),

    # AJAX URLS.
    path('ajax/bot_instance/get', views.instance, name='bot_instance'),
    path('ajax/bot_instance/kill', views.kill_instance, name='kill_instance'),
    path('ajax/signal', views.signal, name='signal'),
    path('ajax/prestige', views.prestiges, name='prestiges'),
    path('ajax/game_screen', views.screen, name='game_screen'),
    path('ajax/generate_queued', views.generate_queued, name='generate_queued'),
    path('ajax/theme_change', views.theme_change, name='theme_change')
]
