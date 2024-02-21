# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views
from .views import *

urlpatterns = [

    # The home page
    path('', views.index, name='home'),

    path('importar-datos/', importar_datos, name='importar_datos'),
    path('recargar_datos/', recargar_datos, name='recargar_datos'),
    
    path("calendar/", views.calendar, name="calendar"),
    path("create-template/", create_template, name="create-template"),
    path("delete-template/", views.delete_template, name="delete-template"),
    path("create-event/", create_event, name="create-event"),
    path("get-event/<int:id>/", get_event, name="get-event"),
    path("get-events/<int:month>/", views.get_events, name="get-events"),
    path("delete-event/", views.delete_event, name="delete-event"),
    path("day-plan/", views.day_plan, name="day-plan"),

    re_path('tables', views.pages, name='pages'),
    
    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
