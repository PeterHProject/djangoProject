from django import forms
from fileprocess.models import Document, AwsUserAccessDetails, AwsUploadDetails
from fileprocess.models import ProductFile
from django.contrib.admin import widgets


class SQLSelectForm(forms.Form):
    doc = forms.ChoiceField(choices= [])
    sql_table_name = forms.CharField(label='SQL Table Name', max_length=100)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(SQLSelectForm, self).__init__(*args, **kwargs)
        doc_list = ProductFile.objects.filter(uploaded_by=self.user)
        item_list = []
        pk_list = []
        for item in doc_list:
            item_list.append(item.file_name)
            pk_list.append(item.pk)
        choice_list = list(zip(pk_list,item_list))
        self.fields['doc'].choices = choice_list


#https://stackoverflow.com/questions/4593292/how-would-i-use-django-forms-to-prepopulate-a-choice-field-with-rows-from-a-mode
# http://citadelgrad.co/2013/how-filter-django-forms-by-user/
# https://stackoverflow.com/questions/5119994/get-current-user-in-django-form

class ExcelFunctionForm(forms.Form):
    doc = forms.ChoiceField(choices= [])

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ExcelFunctionForm, self).__init__(*args, **kwargs)
        doc_list = ProductFile.objects.filter(uploaded_by=self.user)
        item_list = []
        pk_list = []
        for item in doc_list:
            item_list.append(item.file_name)
            pk_list.append(item.pk)
        choice_list = list(zip(pk_list,item_list))
        self.fields['doc'].choices = choice_list



class CleanExcelForm(forms.Form):
    doc = forms.ChoiceField(choices= [])

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(CleanExcelForm, self).__init__(*args, **kwargs)
        doc_list = Document.objects.filter(uploaded_by=self.user)
        item_list = []
        pk_list = []
        for item in doc_list:
            item_list.append(item.document_name)
            pk_list.append(item.pk)
        choice_list = list(zip(pk_list,item_list))
        self.fields['doc'].choices = choice_list

class CalculateFinancialsForm(forms.Form):
    doc = forms.ChoiceField(choices= [])

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(CalculateFinancialsForm, self).__init__(*args, **kwargs)
        doc_list = Document.objects.filter(uploaded_by=self.user)
        item_list = []
        pk_list = []
        for item in doc_list:
            item_list.append(item.document_name)
            pk_list.append(item.pk)
        choice_list = list(zip(pk_list,item_list))
        self.fields['doc'].choices = choice_list

class FileForm(forms.Form):
    file = forms.FileField()
    file_name = forms.CharField(max_length=20)


class XirrForm(forms.Form):
    start = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    end = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    ac_date = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    coupon = forms.DecimalField(widget=forms.widgets.NumberInput)
    principal = forms.FloatField(widget=forms.widgets.NumberInput)
    redemption = forms.FloatField(widget=forms.widgets.NumberInput)

class DocTagging(forms.Form):
    text_area = forms.CharField(widget=forms.Textarea)

class CombListInputForm(forms.Form):
    request_list = forms.CharField(widget=forms.Textarea)
    input_list = forms.CharField(widget=forms.Textarea)

class AwsDatabaseForm(forms.Form):
    #host = forms.CharField(max_length = 100)
    #database = forms.CharField(max_length=100)
    #user = forms.CharField(max_length=100)
    #password = forms.CharField(widget=forms.PasswordInput)
    sql_query = forms.CharField(widget=forms.Textarea)

class AwsDatabaseUpload(forms.Form):

    file = forms.FileField()
    table_name = forms.CharField(label='SQL Table Name', max_length=100)

class AwsUserAccessDetailsForm(forms.Form):
    host = forms.CharField(max_length=100)
    database = forms.CharField(max_length=100)
    aws_user_name = forms.CharField(max_length=100)
    aws_password =  forms.CharField(widget=forms.PasswordInput)


class AwsMapQueryForm(forms.Form):
    data_table = forms.ChoiceField(choices= [])
    mapping_table = forms.ChoiceField(choices= [])
    fx_table = forms.ChoiceField(choices= [])

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(AwsMapQueryForm, self).__init__(*args, **kwargs)
        doc_list = AwsUploadDetails.objects.filter(user_id=self.user)
        item_list = []
        pk_list = []
        for item in doc_list:
            item_list.append(item.table_name)
            pk_list.append(item.pk)
        choice_list = list(zip(pk_list,item_list))
        self.fields['data_table'].choices = choice_list
        self.fields['mapping_table'].choices = choice_list
        self.fields['fx_table'].choices = choice_list

class AwsMapQueryForm2(forms.Form):
    data_table = forms.ChoiceField(choices= [])
    mapping_table = forms.ChoiceField(choices= [])
    fx_table = forms.ChoiceField(choices= [])
    data_table1 = forms.ChoiceField(choices= [])


    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(AwsMapQueryForm2, self).__init__(*args, **kwargs)
        doc_list = AwsUploadDetails.objects.filter(user_id=self.user)
        item_list = []
        pk_list = []
        for item in doc_list:
            item_list.append(item.table_name)
            pk_list.append(item.pk)
        choice_list = list(zip(pk_list,item_list))
        self.fields['data_table'].choices = choice_list
        self.fields['mapping_table'].choices = choice_list
        self.fields['fx_table'].choices = choice_list
        self.fields['data_table1'].choices = choice_list
