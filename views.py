from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormView, View
from django.views.generic.list import ListView
from django.views.generic import TemplateView
from fileprocess.models import Document
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseForbidden
from fileprocess.clean_excel_commands import DataFrameClean
#from fileprocess.financial_output_calculations import XirrNpvCal
from fileproject.settings import BASE_DIR
from  fileprocess.forms import SQLSelectForm, CleanExcelForm, CalculateFinancialsForm
import pandas
import datetime
from fileproject.settings import STATICFILES_DIRS

from fileprocess.models import ProductFile
#class imort
from fileproject.aws.edit_requested_file.edit_req_class import EditRequested
#import combination_checker
from fileprocess.combination_gen import FindCombination, FindCombinationList
from fileprocess.forms import CombListInputForm

#wraps file for offline
from wsgiref.util import FileWrapper
from django.conf import settings
import os
from mimetypes import guess_type

from fileprocess.forms import SQLSelectForm, ExcelFunctionForm
from fileprocess.forms import XirrForm
from fileprocess.financial_output_calculations import XirrNpvCalOne

from fileprocess.forms import DocTagging

from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import file_html

from bs4 import BeautifulSoup
import requests
import pandas

from fileprocess.forms import AwsDatabaseForm, AwsDatabaseUpload, AwsUserAccessDetailsForm, AwsMapQueryForm, AwsMapQueryForm2
from fileprocess.aws_database import PostgresDB
from fileprocess.models import AwsUserAccessDetails, AwsUploadDetails

from django.core.mail import EmailMessage
from django.contrib import messages
from django.conf import settings
from bokeh.models import ColumnDataSource, FactorRange

# Create your views here.

#practice
import json
from django.template.loader import render_to_string
from django.core import serializers

def jspract(request):
    list_doc_normal = AwsUploadDetails.objects.filter(user_id=request.user)
    list_doc_json = serializers.serialize('json', list_doc_normal)
    #list of doc json is an obejct
    list_form_name = {'form1':"Model", 'form2':'User'}
    list_form_name_json = json.dumps(list_form_name)
    context = {}
    context['list_doc_json'] = list_doc_json
    print(type(list_doc_json))
    context['list_form_name_json'] = list_form_name_json
    if request.method == 'POST':
        print(request.POST)



    # data1 = {"number":1}
    # data2 = json.dumps(data1)
    # print(type(data2))
    # list_of_docs =
    # context = {}
    # context['data'] = data2
    # context['stuff'] = "this is some stuff"
    return render(request, 'fileprocess/jsprac.html', context)



    # return HttpResponse(json.dumps(context), content_type="application/json")



@login_required
def index(request):
    return render(request, 'fileprocess/index.html')

class ProductCreate(LoginRequiredMixin,CreateView):
    template_name = 'fileprocess/document_form.html'
    model = ProductFile
    fields = ['file', 'file_name']

    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        return super(ProductCreate, self).form_valid(form)

class ProductUpdate(LoginRequiredMixin,UpdateView):
    template_name = 'fileprocess/document_form.html'
    model = ProductFile
    fields = ['file', 'file_name']

class ProductDelete(LoginRequiredMixin,DeleteView):
    template_name = 'fileprocess/document_confirm_delete.html'
    model = ProductFile
    success_url = reverse_lazy('index')

class ProductListView(LoginRequiredMixin, ListView):
    template_name = 'fileprocess/document_list.html'
    model = ProductFile

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['file_list'] = ProductFile.objects.filter(uploaded_by=self.request.user)
        return context

class ProductDownloadView(LoginRequiredMixin,View):
    def get(self, *args, **kwargs):
        pk = kwargs.get('pk')
        download_object = ProductFile.objects.get(pk=pk)
        user = self.request.user
        if user == download_object.uploaded_by:
            aws_filepath = download_object.generate_download_url()
            return HttpResponseRedirect(aws_filepath)
        else:
            return HttpResponseForbidden("forbidden")


class ProductSQLView(LoginRequiredMixin,View):
    def get(self, *args, **kwargs):

        pk = kwargs.get('pk')
        download_object = ProductFile.objects.get(pk=pk)
        user = self.request.user
        if user == download_object.uploaded_by:
            edit_url = download_object.file.url
            edit_url = edit_url.split("?")[0].split("amazonaws.com/")[1]
            sql_query = download_object.return_sql(edit_url)
            context = {'sql_query':sql_query}
            return render(self.request, 'fileprocess/sql_output.html',context )
        else:
            return HttpResponseForbidden("forbidden")

@login_required
def action_menu(request):
    return render(request, 'fileprocess/action_menu.html')

@login_required
def ProductSQL(request):
    form = SQLSelectForm(request.user)
    stage = 'stage0'
    context = {'form': form, 'stage':stage}
    if request.method == 'POST':
        stage = 'stage1'
        pk = request.POST.get('doc')
        download_object = ProductFile.objects.get(pk=pk)
        user = request.user
        if user == download_object.uploaded_by:
            stage = 'stage1'
            edit_url = download_object.file.url
            edit_url = edit_url.split("?")[0].split("amazonaws.com/")[1]
            table_name = request.POST.get('sql_table_name')
            sql_query = download_object.return_sql(edit_url, table_name)
            context = {'sql_query':sql_query, 'form':form, 'stage':stage}
            return render(request, 'fileprocess/sql_output.html',context )
        else:
            stage = 'stage0'
            return HttpResponseForbidden("forbidden")
    else:
        form = SQLSelectForm(request.user)

    return render(request, 'fileprocess/sql_output.html', context)

@login_required
def eir_ac(request):
    form = XirrForm()
    status = 'stage0'
    context = {'form':form, 'status':status}
    if request.method == 'POST':
        status = 'stage1'
        context['status'] = status
        start = request.POST.get('start')
        end = request.POST.get('end')
        coupon = request.POST.get('coupon')
        principal = request.POST.get('principal')
        redemption = request.POST.get('redemption')
        ac_date = request.POST.get('ac_date')
        pay_profile = XirrNpvCalOne(start,end,coupon, principal, redemption).generate_pay_prof()
        string = list()
        for i, a in pay_profile:
            string.append("Payment on {} of {}".format(i.date(),a))
        context['string'] = string
        eir = XirrNpvCalOne(start,end,coupon, principal, redemption).xirr()
        eir = round(eir,2)
        context['eir'] = eir
        npv = XirrNpvCalOne(start,end,coupon, principal, redemption).xnpv(ac_date)
        npv = round(npv,2)
        context['npv'] = npv
        return render (request, 'fileprocess/eir_ac.html', context)
    return render (request, 'fileprocess/eir_ac.html', context)

@login_required
def excel_function(request):
        form = ExcelFunctionForm(request.user)
        stage = 'stage0'
        context = {'form': form, 'stage':stage}
        if request.method == 'POST' and 'initial_selection' in request.POST:
            context['stage'] = 'stage1'
            global pk
            pk = request.POST.get('doc')
            download_object = ProductFile.objects.get(pk=pk)
            edit_url = download_object.file.url
            edit_url = edit_url.split("?")[0].split("amazonaws.com/")[1]
            table_headers = download_object.return_names(edit_url)
            context['table_headers'] = table_headers
            return render(request, 'fileprocess/excel_function.html', context)
        elif request.method=='POST' and 'choice_field' in request.POST:
            download_object = ProductFile.objects.get(pk=pk)
            edit_url = download_object.file.url
            edit_url = edit_url.split("?")[0].split("amazonaws.com/")[1]
            request_list = {}
            choices = ['text', 'integer']
            for key, val in request.POST.items():
                if val in choices:
                    request_list[key] = val
            download_object.excel_function(edit_url, request_list)
            aws_filepath = download_object.generate_download_url()
            return HttpResponseRedirect(aws_filepath)

        else:
            form = ExcelFunctionForm(request.user)
        return render(request, 'fileprocess/excel_function.html', context)

@login_required
def doc_tagging(request):
    form = DocTagging()
    stage = 'stage0'
    context = {'form': form, 'stage':stage}
    if request.method == 'POST' and 'initial_text' in request.POST:
        stage = 'stage1'
        context['stage'] = stage
        global text_area
        text_area = request.POST.get('text_area')
        tags = text_area.count("<")
        tag_list = list(range(1,tags+1))
        context['tag_list'] = tag_list
        return render(request, 'fileprocess/doc_tagging.html', context)
    if request.method == 'POST' and 'submit_item' in request.POST:
        text_area_2 = text_area
        stage = 'stage2'
        context['stage'] = stage
        d_tag = {}
        for i in request.POST:
            if "tag" in i:
                d_tag[i] = request.POST.get(i)
        print(d_tag)
        for key in d_tag.keys():
            text_area_2 = text_area_2.replace(key, d_tag[key])
        print(text_area_2)
        return render(request, 'fileprocess/doc_tagging.html', context)

    return render(request, 'fileprocess/doc_tagging.html', context)

@login_required
def graph(request):

    plot = figure()
    plot.circle([1,2], [3,4])
    html = file_html(plot, CDN, "Data")

    return render(request, "fileprocess/graph.html", {'graph':html})

@login_required
def house_price(request):
    list_of = []
    for i in range(0,5):
        search = "balham"
#        url = "https://www.zoopla.co.uk/for-sale/property/{}/?identifier={}&q={}&radius=0&pn=2".format(search,search, search)
        url = "https://www.zoopla.co.uk/for-sale/property/balham/?identifier=balham&q=Balham%2C%20London&search_source=refine&radius=0&pn="
        r = requests.get(url+str(i))
        c = r.content
        soup = BeautifulSoup(c, 'html.parser')
        properties = soup.find_all("div", {"class":"listing-results-right clearfix"})
        for y in range(0,len(properties)):
            price = properties[y].find('a').text.replace('\n', '').replace(' ', '')
            bedroom = properties[y].find_all('span')[0].text

            list_of.append([price, bedroom])
    def clean_up(x):
        allowed = ["0","1", "2", "3", "4", "5", "6", "7", "8", "9", ".", "-"]
        x = str(x)
        n = ""
        for i in x:
            if i in allowed:
                n = n+i
        try:
            n = float(n)
        except:
            n = 0
        return n
    df = pandas.DataFrame(columns=['Price', 'Bedroom'])
    for i in range(0,len(list_of)):
        df.loc[i] = [list_of[i][0], list_of[i][1]]
    df['Price'] = df['Price'].apply(clean_up)
    df['Bedroom'] = df['Bedroom'].apply(clean_up)
    df2 = df.groupby('Bedroom').mean()
    df2['Price'] = round(df2['Price'] /1000,0)
    p = figure(plot_width=600, plot_height=400)
    p.vbar(x=[df.index[i] for i in range(0,len(df2))], width=0.5, bottom=0,top=df2['Price'], color="navy")
    html = file_html(p, CDN, "Data")
    return render(request, "fileprocess/graph.html", {'graph':html})


@login_required
def combination_checker(request):
    context = {}
    form = CombListInputForm(request.POST)
    context['form'] = form
    if request.method == 'POST':
        request_list = request.POST.get('request_list')
        input_list = request.POST.get('input_list')
        request_list = request_list.replace(' ','').split(',')
        request_list = [float(i) for i in request_list]
        input_list = input_list.replace(' ','').split(',')
        input_list = [float(i) for i in input_list]
        comb_output = FindCombinationList(input_list, request_list).create_comb_matchest_html()
        comb_output=comb_output.replace("""<table border="1" class="dataframe">""","""<table class="table table-hover">""").replace("""<thead>""", """<thead class="thead-inverse">""" )
        context['comb_output'] = comb_output

        return render(request, "fileprocess/combination_checker.html", context)
    return render(request, "fileprocess/combination_checker.html", context)

@login_required
def aws_menu(request):
    context = {}
    table_list = AwsUploadDetails.objects.filter(user_id=request.user)
    context['table_list'] = table_list

    return render(request, "fileprocess/aws_menu.html", context)

@login_required
def aws_upload_csv_create(request):
    context = {}
    form = AwsDatabaseUpload()
    context['form'] = form
    #1 get aws details
    aws_details = AwsUserAccessDetails.objects.filter(user_id=request.user)
    aws_details = aws_details.last()
    host = aws_details.host
    database = aws_details.database
    password = aws_details.aws_password
    user_id = aws_details.aws_user_name
    #2 set up instance
    aws_database_object = PostgresDB(host, database, user_id, password)
    #3 get the file
    if request.method == 'POST':
        table_name = request.POST.get('table_name')
        csv_file = request.FILES['file']
        #change to excel
        csv_file_df = pandas.read_excel(csv_file)
        aws_database_object.df_create_update_database(csv_file_df, table_name)
        aws_site_object = AwsUploadDetails()
        aws_site_object.user_id = request.user
        aws_site_object.table_name = table_name
        aws_site_object.save()
        return redirect('aws_menu')
    return render(request, "fileprocess/aws_database_upload.html", context)

@login_required
def aws_list_data(request, id):
    context = {}
    #1 get aws details
    aws_details = AwsUserAccessDetails.objects.filter(user_id=request.user)
    aws_details = aws_details.last()
    host = aws_details.host
    database = aws_details.database
    password = aws_details.aws_password
    user_id = aws_details.aws_user_name
    #2 set up instance
    aws_database_object = PostgresDB(host, database, user_id, password)
    aws_site_object = AwsUploadDetails.objects.get(id=id)
    table_name = aws_site_object.table_name
    context['table_name'] = table_name
    data_table = aws_database_object.show_all_data_in_html(table_name)
    data_table = data_table.replace("""<table border="1" class="dataframe">""","""<table class="table table-hover">""").replace("""<thead>""", """<thead class="thead-inverse">""" )
    context['data_table'] = data_table
    return render(request,"fileprocess/aws_listing.html", context)

@login_required
def aws_delete_table(request, id):
    context = {}
    #1 get aws details
    aws_details = AwsUserAccessDetails.objects.filter(user_id=request.user)
    aws_details = aws_details.last()
    host = aws_details.host
    database = aws_details.database
    password = aws_details.aws_password
    user = aws_details.aws_user_name
    #2 set up instance
    aws_database_object = PostgresDB(host, database, user, password)
    aws_site_object = AwsUploadDetails.objects.get(id=id)
    table_name = aws_site_object.table_name
    aws_database_object.execute_drop_table(table_name)
    aws_site_object.delete()
    return redirect('aws_menu')

@login_required
def aws_download_table(request, id):

    #1 get aws details
    aws_details = AwsUserAccessDetails.objects.filter(user_id=request.user)
    aws_details = aws_details.last()
    host = aws_details.host
    database = aws_details.database
    password = aws_details.aws_password
    user = aws_details.aws_user_name
    #2 set up instance
    aws_database_object = PostgresDB(host, database, user, password)
    aws_site_object = AwsUploadDetails.objects.get(id=id)
    table_name = aws_site_object.table_name
    sql_data = aws_database_object.show_all_data(table_name)
    df = pandas.DataFrame(sql_data)
    file = df.to_csv()
    response = HttpResponse(file, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sql_table_download.csv"'
    return response

@login_required
def aws_database_details(request):
    context = {}
    form = AwsUserAccessDetailsForm()
    context['form'] = form
    if request.method == 'POST' and 'request_data' in request.POST:
        user_id = request.user
        host = request.POST.get('host')
        database = request.POST.get('database')
        aws_user_name = request.POST.get('aws_user_name')
        aws_password = request.POST.get('aws_password')
        model = AwsUserAccessDetails()
        model.user_id = user_id
        model.host = host
        model.database = database
        model.aws_user_name = aws_user_name
        model.aws_password = aws_password
        model.save()
        return redirect('aws_menu')
    if request.method == 'POST' and 'request_data' in request.POST:
        print("sdfgda")

    return render(request, "fileprocess/aws_database.html", context)

@login_required
def aws_map_query(request):
    context = {}
    form = AwsMapQueryForm(request.user)
    context['form'] = form
    if request.method == 'POST':
        data_table = request.POST.get('data_table')
        aws_site_object = AwsUploadDetails.objects.get(id=data_table)
        data_table_name = aws_site_object.table_name
        mapping_table = request.POST.get('mapping_table')
        aws_site_object = AwsUploadDetails.objects.get(id=mapping_table)
        mapping_table_name = aws_site_object.table_name
        fx_table = request.POST.get('fx_table')
        aws_site_object = AwsUploadDetails.objects.get(id=fx_table)
        fx_table_name = aws_site_object.table_name

        aws_details = AwsUserAccessDetails.objects.filter(user_id=request.user)
        aws_details = aws_details.last()
        host = aws_details.host
        database = aws_details.database
        password = aws_details.aws_password
        user = aws_details.aws_user_name
        #2 set up instance
        aws_database_object = PostgresDB(host, database, user, password)
        #run query on above table_list
        data_table = aws_database_object.run_mappping_query(data_table_name, mapping_table_name, fx_table_name)
        data_graph = aws_database_object.run_mappping_query_graph(data_table_name, mapping_table_name, fx_table_name)
        data_graph = data_graph.groupby('nominal').sum()['amount']
        p = figure(plot_width=600, plot_height=400)
        p.vbar(x=[data_graph.index[i] for i in range(0,len(data_graph))], width=0.5, bottom=0,top=data_graph.values, color="navy")
        html_graph = file_html(p, CDN, "Data")
        context['html_graph'] = html_graph
        data_table = data_table.replace("""<table border="1" class="dataframe">""","""<table class="table table-hover">""").replace("""<thead>""", """<thead class="thead-inverse">""" )
        context['data_table'] = data_table


        return render(request, "fileprocess/aws_query_output.html", context)
    return render(request, "fileprocess/aws_query_output.html", context)


@login_required
def aws_map_query2(request):
    context = {}
    form = AwsMapQueryForm2(request.user)
    context['form'] = form
    if request.method == 'POST':
        data_table = request.POST.get('data_table')
        aws_site_object = AwsUploadDetails.objects.get(id=data_table)
        data_table_name = aws_site_object.table_name
        data_table1 = request.POST.get('data_table1')
        aws_site_object = AwsUploadDetails.objects.get(id=data_table1)
        data_table_name1 = aws_site_object.table_name
        mapping_table = request.POST.get('mapping_table')
        aws_site_object = AwsUploadDetails.objects.get(id=mapping_table)
        mapping_table_name = aws_site_object.table_name
        fx_table = request.POST.get('fx_table')
        aws_site_object = AwsUploadDetails.objects.get(id=fx_table)
        fx_table_name = aws_site_object.table_name

        aws_details = AwsUserAccessDetails.objects.filter(user_id=request.user)
        aws_details = aws_details.last()
        host = aws_details.host
        database = aws_details.database
        password = aws_details.aws_password
        user = aws_details.aws_user_name
        #2 set up instance
        aws_database_object = PostgresDB(host, database, user, password)
        #run query on above table_list
        data_table = aws_database_object.run_mappping_query(data_table_name, mapping_table_name, fx_table_name)
        data_graph1 = aws_database_object.run_mappping_query_graph(data_table_name, mapping_table_name, fx_table_name)
        data_graph2 = aws_database_object.run_mappping_query_graph(data_table_name1, mapping_table_name, fx_table_name)
        data2 = data_graph1.groupby('class').sum()['amount']
        data1 = data_graph2.groupby('class').sum()['amount']
        versions = ['v1', 'v2']
        x = [(c, v) for c in [i  for i in data1.index] for v in versions]
        counts = []
        for a,b in zip(data1.values, data2.values):
            counts.append(a)
            counts.append(b)
        counts = tuple(counts)
        source = ColumnDataSource(data=dict(x=x, counts=counts))
        p = figure(x_range=FactorRange(*x), plot_height=350, title="Comparison",)
        p.vbar(x='x', top='counts', width=0.9, source=source)
        p.y_range.start = 0
        p.x_range.range_padding = 0.1
        p.xaxis.major_label_orientation = 1
        p.xgrid.grid_line_color = None
        html_graph = file_html(p, CDN, "Data")
        context['html_graph'] = html_graph
        data_table = data_table.replace("""<table border="1" class="dataframe">""","""<table class="table table-hover">""").replace("""<thead>""", """<thead class="thead-inverse">""" )
        context['data_table'] = data_table
        return render(request, "fileprocess/aws_query_output.html", context)
    return render(request, "fileprocess/aws_query_output.html", context)

@login_required
def aws_query_outputJ(request):
    aws_database_object = None
    context = {}
    context['stage'] = 'not_run'
    list_doc_normal = AwsUploadDetails.objects.filter(user_id=request.user)
    list_doc_json = serializers.serialize('json', list_doc_normal)
    form_list = {"f1":"Data table", "f2":"Mapping Table", "f3":"FX Table"}
    form_list_json = json.dumps(form_list)
    context["form_list_json"] = form_list_json
    context["list_doc_json"] = list_doc_json
    if request.method == 'POST' and "request_data" in request.POST and "mapping_2" not in request.POST:
        print(request.POST)
        global data_table_name
        data_table_name = request.POST.get("Data_table")
        global mapping_table_name
        mapping_table_name = request.POST.get('Mapping_Table')
        global fx_table_name
        fx_table_name = request.POST.get('FX_Table')
        aws_details = AwsUserAccessDetails.objects.filter(user_id=request.user)
        aws_details = aws_details.last()
        host = aws_details.host
        database = aws_details.database
        password = aws_details.aws_password
        user = aws_details.aws_user_name
        aws_database_object = PostgresDB(host, database, user, password)
        global data_output
        data_output = aws_database_object.run_mappping_query_fetchall(data_table_name, mapping_table_name, fx_table_name)
        global data_table
        data_table = aws_database_object.run_mappping_query(data_table_name, mapping_table_name, fx_table_name)
        data_table = data_table.replace("""<table border="1" class="dataframe">""","""<table class="table table-hover">""").replace("""<thead>""", """<thead class="thead-inverse">""" )
        context['data_table'] = data_table
        context['stage'] = 'pushed'
        global data_graph
        data_graph = aws_database_object.run_mappping_query_graph(data_table_name, mapping_table_name, fx_table_name)
        data_graph = data_graph.groupby('nominal').sum()['amount']
        p = figure(plot_width=600, plot_height=400)
        p.vbar(x=[data_graph.index[i] for i in range(0,len(data_graph))], width=0.5, bottom=0,top=data_graph.values, color="navy")
        html_graph = file_html(p, CDN, "Data")
        context['html_graph'] = html_graph


    if request.method == 'POST' and "download_request" in request.POST:
        df = pandas.DataFrame(data_output)
        file = df.to_csv()
        response = HttpResponse(file, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="financial_calc_output.csv"'
        return response
    if request.method == 'POST' and "mapping_2" in request.POST:
        aws_details = AwsUserAccessDetails.objects.filter(user_id=request.user)
        aws_details = aws_details.last()
        host = aws_details.host
        database = aws_details.database
        password = aws_details.aws_password
        user = aws_details.aws_user_name
        aws_database_object = PostgresDB(host, database, user, password)
        data_table_name = request.POST.get("Data_table")
        mapping_table_name = request.POST.get('Mapping_Table')
        fx_table_name = request.POST.get('FX_Table')
        data_table_name1 = request.POST.get('mapping_2')
        data_graph1 = aws_database_object.run_mappping_query_graph(data_table_name, mapping_table_name, fx_table_name)
        data_graph2 = aws_database_object.run_mappping_query_graph(data_table_name1, mapping_table_name, fx_table_name)
        data2 = data_graph1.groupby('class').sum()['amount']
        data1 = data_graph2.groupby('class').sum()['amount']
        versions = ['v1', 'v2']
        x = [(c, v) for c in [i  for i in data1.index] for v in versions]
        counts = []
        for a,b in zip(data1.values, data2.values):
            counts.append(a)
            counts.append(b)
        counts = tuple(counts)
        source = ColumnDataSource(data=dict(x=x, counts=counts))
        p = figure(x_range=FactorRange(*x), plot_height=350, title="Comparison",)
        p.vbar(x='x', top='counts', width=0.9, source=source)
        p.y_range.start = 0
        p.x_range.range_padding = 0.1
        p.xaxis.major_label_orientation = 1
        p.xgrid.grid_line_color = None
        html_graph = file_html(p, CDN, "Data")
        context['html_graph'] = html_graph





            # form = AwsMapQueryForm2(request.user)
    # context['form'] = form
    # if request.method == 'POST':
    #     data_table = request.POST.get('data_table')
    #     aws_site_object = AwsUploadDetails.objects.get(id=data_table)
    #     data_table_name = aws_site_object.table_name
    #     data_table1 = request.POST.get('data_table1')
    #     aws_site_object = AwsUploadDetails.objects.get(id=data_table1)
    #     data_table_name1 = aws_site_object.table_name
    #     mapping_table = request.POST.get('mapping_table')
    #     aws_site_object = AwsUploadDetails.objects.get(id=mapping_table)
    #     mapping_table_name = aws_site_object.table_name
    #     fx_table = request.POST.get('fx_table')
    #     aws_site_object = AwsUploadDetails.objects.get(id=fx_table)
    #     fx_table_name = aws_site_object.table_name
    #
    #     aws_details = AwsUserAccessDetails.objects.filter(user_id=request.user)
    #     aws_details = aws_details.last()
    #     host = aws_details.host
    #     database = aws_details.database
    #     password = aws_details.aws_password
    #     user = aws_details.aws_user_name
    #     #2 set up instance
    #     aws_database_object = PostgresDB(host, database, user, password)
    #     #run query on above table_list
    #     data_table = aws_database_object.run_mappping_query(data_table_name, mapping_table_name, fx_table_name)
    #     data_graph1 = aws_database_object.run_mappping_query_graph(data_table_name, mapping_table_name, fx_table_name)
    #     data_graph2 = aws_database_object.run_mappping_query_graph(data_table_name1, mapping_table_name, fx_table_name)
    #     data2 = data_graph1.groupby('class').sum()['amount']
    #     data1 = data_graph2.groupby('class').sum()['amount']
    #     versions = ['v1', 'v2']
    #     x = [(c, v) for c in [i  for i in data1.index] for v in versions]
    #     counts = []
    #     for a,b in zip(data1.values, data2.values):
    #         counts.append(a)
    #         counts.append(b)
    #     counts = tuple(counts)
    #     source = ColumnDataSource(data=dict(x=x, counts=counts))
    #     p = figure(x_range=FactorRange(*x), plot_height=350, title="Comparison",)
    #     p.vbar(x='x', top='counts', width=0.9, source=source)
    #     p.y_range.start = 0
    #     p.x_range.range_padding = 0.1
    #     p.xaxis.major_label_orientation = 1
    #     p.xgrid.grid_line_color = None
    #     html_graph = file_html(p, CDN, "Data")
    #     context['html_graph'] = html_graph
    #     data_table = data_table.replace("""<table border="1" class="dataframe">""","""<table class="table table-hover">""").replace("""<thead>""", """<thead class="thead-inverse">""" )
    #     context['data_table'] = data_table
    #     return render(request, "fileprocess/aws_query_output.html", context)
    return render(request, "fileprocess/aws_query_outputJ.html", context)


@login_required
def aws_list_data2(request, id):
    context = {}
    #1 get aws details
    aws_details = AwsUserAccessDetails.objects.filter(user_id=request.user)
    aws_details = aws_details.last()
    host = aws_details.host
    database = aws_details.database
    password = aws_details.aws_password
    user_id = aws_details.aws_user_name
    #2 set up instance
    aws_database_object = PostgresDB(host, database, user_id, password)
    aws_site_object = AwsUploadDetails.objects.get(id=id)
    table_name = aws_site_object.table_name
    context['table_name'] = table_name
    data = aws_database_object.show_all_data(table_name)
    data_dic = {}
    context['data2'] = data
    for i in data:
        data_dic[i[0]] = i[1]
    context['data'] = data_dic
    if request.method == 'POST':
        for key in data_dic:
            new_item = request.POST.get(key)
            new_item = float(new_item)
            origional_item = data_dic[key]
            new_list = [origional_item, new_item]
            data_dic[key] = new_list
        for key in data_dic.keys():
            if data_dic[key][0] != data_dic[key][1]:
                aws_database_object.update_fx_table_sql(table_name, key, 'av_fx_rate', data_dic[key][1], 'currency' )
        return redirect('aws_menu')
    return render(request,"fileprocess/aws_listing2.html", context)

@login_required
def aws_list_data3(request, id):
    context = {}
    #1 get aws details
    aws_details = AwsUserAccessDetails.objects.filter(user_id=request.user)
    aws_details = aws_details.last()
    host = aws_details.host
    database = aws_details.database
    password = aws_details.aws_password
    user_id = aws_details.aws_user_name
    #2 set up instance
    aws_database_object = PostgresDB(host, database, user_id, password)
    aws_site_object = AwsUploadDetails.objects.get(id=id)
    table_name = aws_site_object.table_name
    context['table_name'] = table_name
    data_html_edit = aws_database_object.data_to_html_table_edit(table_name)
    data = aws_database_object.get_plain_data(table_name)['data']
    di_data = {}
    for i in data:
        di_data[i[0]] = i[1]
    context['data_html_edit'] = data_html_edit
    if request.method =='POST':
        for key in di_data.keys():
            updated_value = request.POST.get(key)
            updated_value = float(updated_value)
            origional_value = di_data.get(key)
            origional_value = float(origional_value)
            if origional_value == updated_value:
                pass
            else:
                print('to be updated')
                aws_database_object.update_fx_table_sql(table_name, key, 'av_fx_rate', updated_value, 'currency')
        data_html_edit = aws_database_object.data_to_html_table_edit(table_name)
        context['data_html_edit'] = data_html_edit
        return render(request,"fileprocess/aws_listing3.html", context)
    return render(request,"fileprocess/aws_listing3.html", context)


@login_required
def aws_list_data4(request, id):
    context = {}
    #1 get aws details
    aws_details = AwsUserAccessDetails.objects.filter(user_id=request.user)
    aws_details = aws_details.last()
    host = aws_details.host
    database = aws_details.database
    password = aws_details.aws_password
    user_id = aws_details.aws_user_name
    #2 set up instance
    aws_database_object = PostgresDB(host, database, user_id, password)
    aws_site_object = AwsUploadDetails.objects.get(id=id)
    table_name = aws_site_object.table_name
    context['table_name'] = table_name
    data_html_edit = aws_database_object.data_to_html_table_editFSOnly(table_name)
    data = aws_database_object.get_plain_data(table_name)['data']
    di_data = {}
    for i in data:
        di_data[i[0]] = i[1]
    context['data_html_edit'] = data_html_edit

    return render(request,"fileprocess/aws_listing4.html", context)















# def aws_database_upload(request):
#     context = {}
#     form = AwsDatabaseUpload(request.POST)
#     context['form'] = form
#     if request.method == 'POST':
#         print(request.user)
#         aws_details = AwsUserAccessDetails.objects.filter(user=request.user)
#         aws_details = aws_details.last()
#         host = aws_details.host
#         database = aws_details.database
#         password = aws_details.aws_password
#         user = aws_details.aws_user_name
#
#         sql_query = request.POST.get('sql_query')
#         excel_file = request.FILES['file']
#
#         sql_data = AwsDatabase(host, database, user, password).aws_database_download(sql_query)
#         context['sql_data'] = sql_data
#         df = pandas.DataFrame(sql_data)
#         file = df.to_csv()
#         response = HttpResponse(file, content_type='text/csv')
#         response['Content-Disposition'] = 'attachment; filename="financial_calc_output.csv"'
#         return response
#     return render(request, "fileprocess/aws_database.html", context)



# def aws_database_download(request):
#     context = {}
#     form = AwsDatabaseForm(request.POST)
#     context['form'] = form
#     if request.method == 'POST':
#
#         print(request.user)
#         aws_details = AwsUserAccessDetails.objects.filter(user=request.user)
#         aws_details = aws_details.last()
#         host = aws_details.host
#         database = aws_details.database
#         password = aws_details.aws_password
#         print(password)
#         user = aws_details.aws_user_name
#         sql_query = request.POST.get('sql_query')
#         sql_data = AwsDatabase(host, database, user, password).aws_database_download(sql_query)
#         context['sql_data'] = sql_data
#         df = pandas.DataFrame(sql_data)
#         file = df.to_csv()
#         response = HttpResponse(file, content_type='text/csv')
#         response['Content-Disposition'] = 'attachment; filename="financial_calc_output.csv"'
#         return response
#     return render(request, "fileprocess/aws_database.html", context)
#
# def aws_database_details(request):
#     context = {}
#     form = AwsUserAccessDetailsForm(request.POST)
#     context['form'] = form
#     if request.method == 'POST':
#         if form.is_valid():
#             user = request.user
#             host = request.POST.get('host')
#             database = request.POST.get('database')
#             aws_user_name = request.POST.get('aws_user_name')
#             aws_password = request.POST.get('aws_password')
#             model = AwsUserAccessDetails()
#             model.user = user
#             model.host = host
#             model.database = database
#             model.aws_user_name = aws_user_name
#             model.aws_password = aws_password
#             model.save()
#             return HttpResponse('Thanks - model updated with DB details')
#
#     return render(request, "fileprocess/aws_database.html", context)
#
#
#
#

#
#
# @login_required
# def output_sql(request):
#     if request.method == 'POST':
#         form = SQLSelectForm(request.user, request.POST)
#         if form.is_valid():
#             document_requested = Document.objects.get(pk=form.cleaned_data['doc'])
#             path = document_requested.document.url
#             if path[0] == '/':
#                  path = path[1::]
#             query = SQLOutput(path).create_sql_query(form.cleaned_data['sql_table_name'])
#             return render(request, 'fileprocess/output_create_sql.html', {'form':form, 'sql_output':query })
#     else:
#         form = SQLSelectForm(request.user)
#     return render(request, 'fileprocess/output_create_sql.html', {'form':form})
#
# @login_required
# def clean_excel(request):
#     status = 'stage1'
#     form = CleanExcelForm(request.user)
#     if request.method == 'POST' and 'excel_field' in request.POST:
#         status = 'stage2'
#         # https://stackoverflow.com/questions/866272/how-can-i-build-multiple-submit-buttons-django-form
#         global excel_model
#         #so can access everywhere in the below request.POST['doc']
#         # https://stackoverflow.com/questions/10588317/python-function-global-variables
#         excel_model = request.POST['doc']
#         print(excel_model)
#
#         form = CleanExcelForm(request.user, request.POST)
#         if form.is_valid():
#             document_requested = Document.objects.get(pk=form.cleaned_data['doc'])
#             path = document_requested.document.url
#             if path[0] == '/':
#                  path = path[1::]
#             items = SQLOutput(path).find_name()
#             return render(request, 'fileprocess/clean_excel.html', {'form':form, 'items': items, 'status':status,})
#     # elif request.method == 'POST' and 'choice_field' in request.POST:
#     #     print(request.POST['pol_seq'])
#     elif request.method == 'POST' and 'choice_field' in request.POST:
#         document_requested = Document.objects.get(pk=excel_model)
#         path = document_requested.document.url
#         if path[0] == '/':
#              path = path[1::]
#         with open(path) as file:
#             print(path)
#
#             file = DataFrameClean(file, request.POST.dict()).create_new_df()
#             response = HttpResponse(file, content_type='text/csv')
#             response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
#             return response
#         # list_of_fields = []
#         # list_of_request = []
#         #
#         # for i in request.POST:
#         #     list_of_fields.append(i)
#         #     list_of_request.append(request.POST[i])
#         # print(list(zip(list_of_fields, list_of_request)))
#
#     else:
#         form = CleanExcelForm(request.user)
#
#     return render(request, 'fileprocess/clean_excel.html', {'form':form, 'status':status})
#
# # https://chriskief.com/2012/12/30/django-class-based-views-with-multiple-forms/
#
# @login_required
# def calculate_financials(request):
#
#     form = CalculateFinancialsForm(request.user)
#     if request.method == 'POST':
#         excel_model = request.POST['doc']
#         print(excel_model)
#         form = CalculateFinancialsForm(request.user, request.POST)
#         if form.is_valid():
#             document_requested = Document.objects.get(pk=form.cleaned_data['doc'])
#             path = document_requested.document.url
#             if path[0] == '/':
#                  path = path[1::]
#             file = pandas.read_excel(path)
#             #file = XirrNpvCal(file).do_anything()
#             file = file.to_csv()
#             response = HttpResponse(file, content_type='text/csv')
#             response['Content-Disposition'] = 'attachment; filename="financial_calc_output.csv"'
#             return response
#
#
#             # file = pandas.read_excel(path)
#             # file = new.to_csv()
#             # response = HttpResponse(file, content_type='text/csv')
#             # response['Content-Disposition'] = 'attachment; filename="financial_calc_output.csv"'
#             # return response
#     else:
#         form = CalculateFinancialsForm(request.user)
#
#     return render(request, 'fileprocess/calculate_financials.html', {'form':form})
#
# @login_required
# def calculate_financials_template(request):
#     path = "static/templates/eir_template.csv"
#     with open(path) as file:
#         response = HttpResponse(file, content_type='text/csv')
#         response['Content-Disposition'] = 'attachment; filename="calculate_financials_template.csv"'
#         return response
# @login_required
# def file_change(filepath):
#     REQUESTED_FILE_NAME = filepath
#     s3.Bucket(BUCKET_NAME).download_file(REQUESTED_FILE_NAME, REQUESTED_FILE_NAME)
#     #method needs to be updated
#     df = pandas.read_csv(REQUESTED_FILE_NAME)
#     df['new_col4'] = '300'
#     df.to_csv(REQUESTED_FILE_NAME)
#     s3.meta.client.upload_file(REQUESTED_FILE_NAME,BUCKET_NAME, REQUESTED_FILE_NAME)




        #will put back when work out edits
        #edit_url = download_object.file.url
        #edit_url=edit_url.split("?")[0].split("amazonaws.com/")[1]

        #aws details
        # access_key = getattr(settings, 'AWS_ACCESS_KEY_ID')
        # secret_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY')
        # bucket = getattr(settings, 'AWS_STORAGE_BUCKET_NAME')
        # #EditRequested(access_key, secret_key, bucket).edit_file(edit_url)
        # aws_filepath = download_object.generate_download_url()
        # return HttpResponseRedirect(aws_filepath)


#pre edit
# class ProductDownloadView(View):
#     def get(self, *args, **kwargs):
#         pk = kwargs.get('pk')
#         download_object = ProductFile.objects.get(pk=pk)
#         aws_filepath = download_object.generate_download_url()
#         print(aws_filepath)
#         return HttpResponseRedirect(aws_filepath)


        # final_filepath = os.path.join(file_root, filepath) # where the file is stored
        # with open(final_filepath, 'rb') as f:
        #     wrapper = FileWrapper(f)
        #     mimetype = 'application/force-download'
        #     guessed_mimetype = guess_type(filepath)[0]
        #     print(guessed_mimetype)
        #     if guessed_mimetype:
        #         mimetype = guessed_mimetype
        #     response = HttpResponse(wrapper, content_type="mimetype")
        #     response['Content-Disposition'] = "attachment;filename=%s" %(download_object.file)
        #     response["X-SendFIle"] = 'SomeText.txt'
        #     return response


        #mime types: https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Complete_list_of_MIME_types


#the ofline pre to aws
# class ProductDownloadView(View):
#     def get(self, *args, **kwargs):
#         pk = kwargs.get('pk')
#         download_object = ProductFile.objects.get(pk=pk)
#         context = "some text"
#
#         filepath = download_object.file.path
#         file_root = settings.PROTECTED_ROOT
#         final_filepath = os.path.join(file_root, filepath) # where the file is stored
#         with open(final_filepath, 'rb') as f:
#             wrapper = FileWrapper(f)
#             mimetype = 'application/force-download'
#             guessed_mimetype = guess_type(filepath)[0]
#             print(guessed_mimetype)
#             if guessed_mimetype:
#                 mimetype = guessed_mimetype
#             response = HttpResponse(wrapper, content_type="mimetype")
#             response['Content-Disposition'] = "attachment;filename=%s" %(download_object.file)
#             response["X-SendFIle"] = 'SomeText.txt'
#             return response
#
#
#         #mime types: https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Complete_list_of_MIME_types

# class DocumentCreate(LoginRequiredMixin,CreateView):
#     model = Document
#     fields = ['document', 'document_name']
#
#     def form_valid(self, form):
#         form.instance.uploaded_by = self.request.user
#         return super(DocumentCreate, self).form_valid(form)
#
# class DocumentUpdate(LoginRequiredMixin,UpdateView):
#     model = Document
#     fields = ['document', 'document_name']
#
# class DocumentDelete(LoginRequiredMixin,DeleteView):-
#     model = Document
#     success_url = reverse_lazy('index')
#
# class DocumentListView(LoginRequiredMixin, ListView):
#     model = Document
#
#     def get_context_data(self, **kwargs):
#         # Call the base implementation first to get a context
#         context = super().get_context_data(**kwargs)
#         # Add in a QuerySet of all the books
#         context['document_list'] = Document.objects.filter(uploaded_by=self.request.user)
#
#         return context
#
# @login_required
# def document_download(request, pk):
#
#     document_requested = Document.objects.get(pk=pk)
#     document_requested.generate_download_url()
#
#     return HttpResponse("hi")

# @login_required
# def document_download(request, pk):
#
#     document_requested = Document.objects.get(pk=pk)
#     if request.user == document_requested.uploaded_by:
#         path = document_requested.document.url
#         print(path)
#         file = pandas.read_csv(path)
#         file = file.to_csv()
#
#         response = HttpResponse(file, content_type='text/csv')
#         response['Content-Disposition'] = 'attachment; filename="requested_file.csv"'
#         return response
#     else:
#         return Http404

# @login_required
# def document_download(request, pk):
#
#     document_requested = Document.objects.get(pk=pk)
#     if request.user == document_requested.uploaded_by:
#         path = document_requested.document.path
#         with open(path) as file:
#             response = HttpResponse(file, content_type='text/csv')
#             response['Content-Disposition'] = 'attachment; filename="requested_file.csv"'
#             return response
#     else:
#         return Http404
