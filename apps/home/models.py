# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import *
from django.conf import settings

# Create your models here.
class ModeloBase(models.Model):
    id = models.AutoField(primary_key=True)
    estado = models.BooleanField('Estado', default=True)
    fecha_creacion = models.DateField('Fecha de creación', auto_now=False ,auto_now_add=True)
    fecha_modificacion = models.DateField('Fecha de modificación', auto_now=True, auto_now_add=False)
    fecha_eliminacion = models.DateField('Fecha de eliminación', auto_now=True, auto_now_add=False)

    class  Meta:
        abstract = True

class Account(ModeloBase):
    name = models.CharField('Name', max_length=100)
    
    class  Meta:
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'

    def __str__(self):
        return self.name


class Category(ModeloBase):
    name = models.CharField('Name', max_length=100)
    
    class  Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name
    
    
class Expense(ModeloBase):
    
    types_of_expenses = (
        ('Basic needs', 'Basic needs'),
        ('Expendable expenses', 'Expendable expenses'),
        ('Other', 'Other'),
        ('Undetermined', 'Undetermined'),
    )
    
    date = models.DateField('Expense Date')
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.FloatField('Amount')
    type = models.CharField(choices=types_of_expenses, max_length=100, blank=True, null=True)
    descripcion = models.TextField('Descripción', blank=True, null=True)
    
    class  Meta:
        verbose_name = 'Expense'
        verbose_name_plural = 'Expenses'

    def __str__(self):
        return self.descripcion


class Income(ModeloBase):
    date = models.DateField('Income Date')
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.FloatField('Amount')
    descripcion = models.TextField('Descripción', blank=True, null=True)
    
    class  Meta:
        verbose_name = 'Income'
        verbose_name_plural = 'Income'

    def __str__(self):
        return self.descripcion
    
class RelationCategoryTypeExpense(ModeloBase):
    
    types_of_expenses = (
        ('Basic needs', 'Basic needs'),
        ('Expendable expenses', 'Expendable expenses'),
        ('Other', 'Other'),
        ('Undetermined', 'Undetermined'),
    )
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    type_expense = models.CharField(choices=types_of_expenses, max_length=100, blank=True, null=True)
        
    class  Meta:
        verbose_name = 'RelationCategoryTypeExpense'
        verbose_name_plural = 'RelationCategoryTypeExpense'

    def __str__(self):
        return self.category.name
    
    
    
class Templates(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True)
    name = models.CharField(max_length=200)
    notes = models.CharField(max_length=200, blank=True)

class Event(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True)
    name = models.CharField(max_length=200)
    amount = models.FloatField('Amount')
    notes = models.CharField(max_length=200, blank=True)
    date = models.DateField(null=True, blank=True)