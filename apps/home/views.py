# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import json
from django.shortcuts import render, redirect
from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from .models import *
from .forms import ImportForm
import pandas as pd
from django.http import JsonResponse
from locale import setlocale, LC_TIME
from django.db.models import Sum
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_protect
from urllib.parse import parse_qs
from django.forms.models import model_to_dict
from django.utils.html import escapejs

def getMyType():
    return "Desde view"

@login_required(login_url="/login/")
def index(request):
    # Recuperar el mensaje de la sesión
    mensaje = request.session.pop('mensaje', None)
    
    #Crear la asociacion de categoria con tipo de gasto
    list_category = Category.objects.all()
    
    for item_category in list_category:
        create_new_relation = False
        result_category_relation = RelationCategoryTypeExpense.objects.filter(category=item_category.id)
        if len(result_category_relation) > 0:
            if result_category_relation[0] is None:
                create_new_relation = True
        else:
            create_new_relation = True
            
        if create_new_relation == True:
            # Create RelationCategoryTypeExpense with Type Expense blank
            new_relation = RelationCategoryTypeExpense(
                category = item_category,
                type_expense = '' 
            )
            
            new_relation.save()
        
    
    
    #Asignar las categorias a los gastos
    list_expenses = Expense.objects.all()
    
    for item_expense in list_expenses:
        if item_expense.category != None and (item_expense.type == None or item_expense.type == ''):
            nuevoType = RelationCategoryTypeExpense.objects.filter(category=item_expense.category)[0]
            
            item_expense.type = nuevoType.type_expense
            item_expense.save()
            
    
    context = {
        'segment': 'index',
        'mensaje': mensaje
    }
    
    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))

def importar_datos(request):
    
    context = {'segment': 'index'}
    new_incomes_registers = 0
    new_expenses_registers = 0
    
    try:
        if request.method == 'POST':
            form = ImportForm(request.POST, request.FILES)
            if form.is_valid():
                # Leer el archivo Excel usando pandas y seleccionar la hoja "Gastos"
                excel_data_expense = pd.read_excel(request.FILES['excel_file'], sheet_name='Gastos', header=1)
                excel_data_income = pd.read_excel(request.FILES['excel_file'], sheet_name='Ingresos', header=1)
                
                # Loop through the elements of the vector and store them in the expense database
                for index, row in excel_data_expense.iterrows():
                    account, created_account = Account.objects.get_or_create(name=row['Cuenta'])
                    category, created_category = Category.objects.get_or_create(name=row['Categoría'])
                    
                    setlocale(LC_TIME, 'es_ES.UTF-8')
                    
                    # Formato de la cadena de fecha
                    formato_fecha = "%d de %B de %Y"

                    cad_fecha = row['Fecha y hora']
                    
                    # Convertir la cadena a un objeto de fecha
                    expense_date_s = datetime.strptime(cad_fecha, formato_fecha)
                    
                    # Get descripcion
                    descriptionExpense = ""
                    if not pd.isna(row['Comentario']):
                        descriptionExpense = row['Comentario']
                    
                    if checkExpenseCreate(expense_date_s, account, category, row['Cantidad en la divisa predeterminada'], descriptionExpense) == False:
                        Expense.objects.create(
                            date=expense_date_s,
                            account=account, 
                            category=category,
                            amount=row['Cantidad en la divisa predeterminada'],
                            descripcion=descriptionExpense,
                        )
                        new_expenses_registers = new_expenses_registers + 1

                # Loop through the elements of the vector and store them in the income database
                for index, row in excel_data_income.iterrows():
                    account, created_account = Account.objects.get_or_create(name=row['Cuenta'])
                    category, created_category = Category.objects.get_or_create(name=row['Categoría'])
                    
                    setlocale(LC_TIME, 'es_ES.UTF-8')
                    
                    # Formato de la cadena de fecha
                    formato_fecha = "%d de %B de %Y"

                    cad_fecha = row['Fecha y hora']
                    
                    # Convertir la cadena a un objeto de fecha
                    income_date_s = datetime.strptime(cad_fecha, formato_fecha)
                    
                    # Get descripcion
                    descriptionIncome = ""
                    if not pd.isna(row['Comentario']):
                        descriptionIncome = row['Comentario']
                    
                    if checkIncomeCreate(income_date_s, account, category, row['Cantidad en la divisa predeterminada'], descriptionIncome) == False:
                        Income.objects.create(
                            date=income_date_s,
                            account=account, 
                            category=category,
                            amount=row['Cantidad en la divisa predeterminada'],
                            descripcion=descriptionIncome,
                        )
                        new_incomes_registers = new_incomes_registers + 1
        else:
            form = ImportForm()
        
        request.session['mensaje'] = escapejs('Importación exitosa. \n Se han registrado ' + str(new_expenses_registers) + ' nuevos registros de gastos. \n Se han registrado ' + str(new_incomes_registers) + ' nuevos registros de ingresos.')
        
        return redirect('/')

    except Exception as e:
        request.session['mensaje'] = 'Error en la importación'
        return redirect('/')
        #return JsonResponse({'status': 'error', 'message': 'ERROR EN VIEW'})

def checkExpenseCreate(date, account, category, amount, descripcion):
    result_search_expense = Expense.objects.filter(
        date=date,
        account=account, 
        category=category,
        amount=amount,
        descripcion=descripcion,
    )
    
    if len(result_search_expense) == 1:
        return True
    else:
        return False


def checkIncomeCreate(date, account, category, amount, descripcion):
    result_search_income = Income.objects.filter(
        date=date,
        account=account, 
        category=category,
        amount=amount,
        descripcion=descripcion,
    )
    
    if len(result_search_income) == 1:
        return True
    else:
        return False

def getLastMonth(mes_seleccionado):
    # Convertir la cadena a un objeto de fecha
    fecha = datetime.strptime(mes_seleccionado, "%Y-%m")

    # Retroceder un mes
    nueva_fecha = fecha - timedelta(days=fecha.day)

    # Ajustar el año si es enero
    '''if nueva_fecha.month == 12:
        nueva_fecha = nueva_fecha.replace(year=nueva_fecha.year - 1)'''

    # Convertir la nueva fecha a una cadena en el mismo formato
    nueva_cadena_fecha = nueva_fecha.strftime("%Y-%m")

    return nueva_cadena_fecha
    
def getInformationExpenses(mes_seleccionado):
    # Get last month
    last_month_selected = getLastMonth(mes_seleccionado)
    
    # Get all expenses
    list_expenses = Expense.objects.filter(date__month=mes_seleccionado.split('-')[1], date__year=mes_seleccionado.split('-')[0])
    list_expenses_last_month = Expense.objects.filter(date__month=last_month_selected.split('-')[1], date__year=last_month_selected.split('-')[0])

    # Get expenses by category
    list_categories = Category.objects.all()
    list_expenses_by_category = []
    for category in list_categories:
        expenses_by_category = Expense.objects.filter(category = category.id, date__month=mes_seleccionado.split('-')[1], date__year=mes_seleccionado.split('-')[0])
        # Get percentage expenses
        if len(list_expenses) != 0:
            percentage_expenses = (len(expenses_by_category) / len(list_expenses)) * 100
        else:
            percentage_expenses = 0
            
        # Get importe de expenses by category
        # Get the total amount of all expenses from the past month.
        total_amount_by_category = expenses_by_category.aggregate(Sum('amount'))['amount__sum']
        total_amount_by_category = total_amount_by_category if total_amount_by_category is not None else 0
         
        if total_amount_by_category != 0:
            list_expenses_by_category.append({
                'name': category.name,
                "number_expenses": len(expenses_by_category),
                "total_amount_by_category": round(total_amount_by_category, 2),
                "percentage_expenses": round(percentage_expenses, 2)
            })
    
    # Sort list category by numbers
    list_expenses_by_category = sorted(list_expenses_by_category, key=lambda x: x['number_expenses'], reverse=True)
    
    # Get the total amount of all expenses
    total_amount = list_expenses.aggregate(Sum('amount'))['amount__sum']
    total_amount = total_amount if total_amount is not None else 0
    
    # Get the total amount of all expenses from the past month.
    total_amount_last_month = list_expenses_last_month.aggregate(Sum('amount'))['amount__sum']
    total_amount_last_month = total_amount_last_month if total_amount_last_month is not None else 0
    
    # Get amount by type()
    # Basic needs
    list_expenses_basic_needs = Expense.objects.filter(type='Basic needs' ,date__month=mes_seleccionado.split('-')[1], date__year=mes_seleccionado.split('-')[0])
    total_amount_basic_needs = list_expenses_basic_needs.aggregate(Sum('amount'))['amount__sum']
    total_amount_basic_needs = total_amount_basic_needs if total_amount_basic_needs is not None else 0
    
    # Expendable expenses
    list_expenses_expendable_expenses = Expense.objects.filter(type='Expendable expenses' ,date__month=mes_seleccionado.split('-')[1], date__year=mes_seleccionado.split('-')[0])
    total_amount_expendable_expenses = list_expenses_expendable_expenses.aggregate(Sum('amount'))['amount__sum']
    total_amount_expendable_expenses = total_amount_expendable_expenses if total_amount_expendable_expenses is not None else 0
    # Other
    list_expenses_other = Expense.objects.filter(type='Other' ,date__month=mes_seleccionado.split('-')[1], date__year=mes_seleccionado.split('-')[0])
    total_amount_other = list_expenses_other.aggregate(Sum('amount'))['amount__sum']
    total_amount_other = total_amount_other if total_amount_other is not None else 0
    # Undetermined Or None Or Blank
    list_expenses_undetermined = Expense.objects.filter(type='Undetermined' ,date__month=mes_seleccionado.split('-')[1], date__year=mes_seleccionado.split('-')[0])
    total_amount_undetermined = list_expenses_undetermined.aggregate(Sum('amount'))['amount__sum']
    total_amount_undetermined = total_amount_undetermined if total_amount_undetermined is not None else 0
    
    list_expenses_none = Expense.objects.filter(type=None ,date__month=mes_seleccionado.split('-')[1], date__year=mes_seleccionado.split('-')[0])
    total_amount_none = list_expenses_none.aggregate(Sum('amount'))['amount__sum']
    total_amount_none = total_amount_none if total_amount_none is not None else 0
    
    list_expenses_blank = Expense.objects.filter(type='' ,date__month=mes_seleccionado.split('-')[1], date__year=mes_seleccionado.split('-')[0])
    total_amount_blank = list_expenses_blank.aggregate(Sum('amount'))['amount__sum']
    total_amount_blank = total_amount_blank if total_amount_blank is not None else 0
    
    total_amount_undetermined = total_amount_undetermined + total_amount_none + total_amount_blank
    
    if total_amount_basic_needs != 0:
        total_expense_basic_needs_percentage = round((total_amount_basic_needs / total_amount) * 100, 2)
    else:
        total_expense_basic_needs_percentage = 0
        
    if total_amount_expendable_expenses != 0:
        total_expense_expendable_expenses_percentage = round((total_amount_expendable_expenses / total_amount) * 100, 2)
    else:
        total_expense_expendable_expenses_percentage = 0
        
    if total_amount_other != 0:
        total_expense_other_percentage = round((total_amount_other / total_amount) * 100, 2)
    else:
        total_expense_other_percentage = 0
        
    if total_amount_undetermined != 0:
        total_expense_undetermined_percentage = round((total_amount_undetermined / total_amount) * 100, 2)
    else:
        total_expense_undetermined_percentage = 0
    
    
    json_expenses = {
        'list_expenses': list_expenses,
        'list_expenses_by_category': list_expenses_by_category,
        'total_expense': round(total_amount, 2),
        'total_expense_last_month': round(total_amount_last_month, 2),
        'diff_total_expense_last_month': round(total_amount - total_amount_last_month, 2),
        'num_expenses': len(list_expenses),
        'diff_num_expenses_last_month': round(len(list_expenses) - len(list_expenses_last_month), 2),
        
        'total_expense_basic_needs': round(total_amount_basic_needs, 2),
        'total_expense_basic_needs_percentage': total_expense_basic_needs_percentage,
        'total_expense_expendable_expenses': round(total_amount_expendable_expenses, 2),
        'total_expense_expendable_expenses_percentage': total_expense_expendable_expenses_percentage,
        'total_expense_other': round(total_amount_other, 2),
        'total_expense_other_percentage': total_expense_other_percentage,
        'total_expense_undetermined': round(total_amount_undetermined, 2),
        'total_expense_undetermined_percentage': total_expense_undetermined_percentage,
    }
    
    return json_expenses


def getInformationIncomes(mes_seleccionado):
    # Get last month
    last_month_selected = getLastMonth(mes_seleccionado)
    
    # Get all incomes
    list_incomes = Income.objects.filter(date__month=mes_seleccionado.split('-')[1], date__year=mes_seleccionado.split('-')[0])
    list_incomes_last_month = Income.objects.filter(date__month=last_month_selected.split('-')[1], date__year=last_month_selected.split('-')[0])

    # Get incomes by category
    list_categories = Category.objects.all()
    list_incomes_by_category = []
    for category in list_categories:
        incomes_by_category = Income.objects.filter(category = category.id, date__month=mes_seleccionado.split('-')[1], date__year=mes_seleccionado.split('-')[0])
        if len(list_incomes) != 0:
            percentage_incomes = (len(incomes_by_category) / len(list_incomes)) * 100
        else:
            percentage_incomes = 0
            
        # Get importe de expenses by category
        # Get the total amount of all expenses from the past month.
        total_amount_by_category = incomes_by_category.aggregate(Sum('amount'))['amount__sum']
        total_amount_by_category = total_amount_by_category if total_amount_by_category is not None else 0
        
        if total_amount_by_category != 0:
            list_incomes_by_category.append({
                'name': category.name,
                "number_incomes": len(incomes_by_category),
                "total_amount_by_category": round(total_amount_by_category, 2),
                "percentage_incomes": round(percentage_incomes, 2)
            })
    
    # Sort list category by numbers
    list_incomes_by_category = sorted(list_incomes_by_category, key=lambda x: x['number_incomes'], reverse=True)
    
    # Get the total amount of all incomes
    total_amount = list_incomes.aggregate(Sum('amount'))['amount__sum']
    total_amount = total_amount if total_amount is not None else 0
    
    # Get the total amount of all expenses from the past month.
    total_amount_last_month = list_incomes_last_month.aggregate(Sum('amount'))['amount__sum']
    total_amount_last_month = total_amount_last_month if total_amount_last_month is not None else 0
    
    json_incomes = {
        'list_incomes': list_incomes,
        'list_incomes_by_category': list_incomes_by_category,
        'total_income': total_amount,
        'total_income_last_month': round(total_amount_last_month, 2),
        'diff_total_income_last_month': round(total_amount - total_amount_last_month, 2),
        'num_incomes': len(list_incomes)
    }
    
    return json_incomes

def recargar_datos(request):
    # Obtén el mes y el año del parámetro GET
    mes_seleccionado = request.GET.get('mes')

    # Recuperar el mensaje de la sesión
    mensaje = request.session.pop('mensaje', None)
    
    context = {
        'segment': 'index',
        'mensaje': mensaje,
    }
    
    json_expenses = getInformationExpenses(mes_seleccionado)
    expense_total_data = json_expenses["total_expense"]
    expense_total_last_month_data = json_expenses["total_expense_last_month"]
    context.update(json_expenses)
    
    json_incomes = getInformationIncomes(mes_seleccionado)
    income_total_data = json_incomes["total_income"]
    income_total_data = json_incomes["total_income"]
    context.update(json_incomes)
    
    monthly_balance = income_total_data - expense_total_data
    if income_total_data != 0:
        monthly_balance_percentage = round((monthly_balance / income_total_data) * 100, 2)
    else:
        monthly_balance_percentage = 0
        
    json_monthly_balance = {
        'monthly_balance': round(monthly_balance, 2),
        'monthly_balance_percentage': monthly_balance_percentage,
    }
    context.update(json_monthly_balance)
    
    html_template = loader.get_template('home/expense_table.html')
    return HttpResponse(html_template.render(context, request))



@login_required(login_url="/login/")
@csrf_protect
def calendar(request):
    user = request.user
    templates = Templates.objects.filter(user=user)
    return render(request, "/calendar.html", {"templates": templates})

@login_required(login_url="/login/")
@csrf_protect
def create_template(request):
    print("---request----")
    print(request)
    print("-----------------")
    if request.method == "GET":
        print("---IN----")
        print(request.GET['name'])
        print("---------")
        user = request.user
        name = request.GET['name']
        notes = request.GET['notes']
        Templates.objects.create(user=user, name=name, notes=notes)
    return redirect("/calendar.html")

@login_required(login_url="/login/")
@csrf_protect
def delete_template(request):
    if request.method == "POST":
        user = request.user
        data = json.loads(request.body)
        templateId = data["templateId"]
        Templates.objects.get(user=user, id=templateId).delete()
        return redirect("/calendar.html")

@login_required(login_url="/login/")
@csrf_protect
def create_event(request):
    if request.method == "POST":
        # Analizar los datos codificados en URL
        query_data = parse_qs(request.body.decode('utf-8'))
        
        print("-query_data-")
        print(query_data)

        user = request.user
        name = query_data.get('name', [''])[0]
        amount = query_data.get('amount', [''])[0]
        date = query_data.get('date', [''])[0]
        notes = query_data.get('notes', [''])[0]
        Event.objects.create(user=user, name=name, notes=notes, amount=amount, date=date)
        
        return redirect("/calendar.html")
        
    #return JsonResponse({"message": "Event successfuly added"})

@csrf_protect
def get_event(request, id):
    if request.method == "GET":
        print("-get_event-")
        event = Event.objects.get(id=id)
        
        # Convertir el evento a un diccionario
        event_data = model_to_dict(event)
        
        # Agregar otras propiedades de la clave principal
        event_data['username'] = event.user.username
        event_data['full_name'] = event.user.first_name + " " + event.user.last_name
        
        print(event_data)
        return JsonResponse({'event': event_data})

@csrf_protect
def get_events(request, month):
    if request.method == "GET":
        print(month)
        events = list(Event.objects.filter(date__month__exact=month).values())
        templates = list(Templates.objects.all().values())
        print(events)
        return JsonResponse({'events': events,'templates': templates})

@login_required(login_url="/login/")
@csrf_protect
def delete_event(request):
    if request.method == "POST":
        data = json.loads(request.body)
        id = data["eventId"]
        user = request.user
        Event.objects.get(user=user, id=id).delete()
        return JsonResponse({"message": "You have successfuly deleted an event"})

@login_required(login_url="/login/")
@csrf_protect
def day_plan(request):
    user = request.user
    date = datetime.date.today()
    events = Event.objects.filter(user=user, date=date)
    return render(request, "app/dayplan.html", {"events": events})