# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms

class ImportForm(forms.Form):
    excel_file = forms.FileField()