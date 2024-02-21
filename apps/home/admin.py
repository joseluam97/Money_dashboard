from django.contrib import admin
from .models import *

class AccountPanel(admin.ModelAdmin):
    list_display = ('id', 'name')

class CategoryPanel(admin.ModelAdmin):
    list_display = ('id', 'name')

class ExpensePanel(admin.ModelAdmin):
    list_display = ('id', 'date', 'account', 'category', 'type', 'amount', 'descripcion')
    list_filter = ( 'account', 'category', 'type')
    
class IncomePanel(admin.ModelAdmin):
    list_display = ('id', 'date', 'account', 'category', 'amount', 'descripcion')
    list_filter = ( 'account', 'category')
    
class RelationCategoryTypeExpensePanel(admin.ModelAdmin):
    list_display = ('id', 'category', 'type_expense')
    list_filter = ( 'category', 'type_expense')
    
# Register your models here.
admin.site.register(Account, AccountPanel)
admin.site.register(Category, CategoryPanel)
admin.site.register(Expense, ExpensePanel)
admin.site.register(Income, IncomePanel)
admin.site.register(RelationCategoryTypeExpense, RelationCategoryTypeExpensePanel)
admin.site.register(Templates)
admin.site.register(Event)