from django.urls import path
from fileprocess import views
from fileprocess.views import (ProductCreate,  ProductUpdate, ProductDelete, ProductListView, ProductDownloadView)
from fileprocess.views import ProductSQLView


urlpatterns = [
    path('index/', views.index, name='index'),
    #path('about/', views.about, name='about'),
    path('create/', ProductCreate.as_view(), name='create'),
    path('update/<int:pk>', ProductUpdate.as_view(), name='update'),
    path('delete/<int:pk>', ProductDelete.as_view(), name='delete'),
    path('list', ProductListView.as_view(), name='list'),
    path('download/<int:pk>/', ProductDownloadView.as_view(), name='download'),
    path('sql_query/', views.ProductSQL, name='sql_query'),
    path('eir_ac/', views.eir_ac, name='eir_ac'),
    path('excel_function', views.excel_function, name='excel_function'),
    path('doc_tagging/', views.doc_tagging, name = 'doc_tagging'),
    path('combination_checker/', views.combination_checker, name='combination_checker'),

    path('action_menu/', views.action_menu, name='actionMenu'),
    path('graph/', views.graph, name='graph'),
    path('house_price/', views.house_price, name='house_price'),

    path('aws_menu/', views.aws_menu, name='aws_menu'),
    path('aws_upload_csv_create/', views.aws_upload_csv_create, name='aws_upload_csv_create'),
    path('aws_list_data3/<int:id>', views.aws_list_data3, name='aws_list_data3'),
    path('aws_list_data4/<int:id>', views.aws_list_data4, name='aws_list_data4'),
    path('aws_delete_table/<int:id>', views.aws_delete_table, name='aws_delete_table'),
    path('aws_download_table/<int:id>', views.aws_download_table, name='aws_download_table'),
    path('aws_database_details/', views.aws_database_details, name='aws_database_details'),
    path('aws_map_query/', views.aws_map_query, name='aws_map_query'),
    path('aws_map_query2/', views.aws_map_query2, name='aws_map_query2'),
    path('aws_query_outputJ/', views.aws_query_outputJ, name='aws_query_outputJ'),



    path('jspract/', views.jspract, name='jspract')


    # path('aws_database_download/', views.aws_database_download, name='aws_database_download'),



]

#to be included eventually
    #path('download/<int:pk>', views.document_download, name='download'),
    #path('action_menu/', views.action_menu, name='action_menu'),
    #path('output_sql/', views.output_sql, name='output_sql'),
    #path('clean_excel/', views.clean_excel, name='clean_excel'),
    #path('calculate_financials/', views.calculate_financials, name='calculate_financials'),
    #path('calculate_financials_template/', views.calculate_financials_template, name='calculate_financials_template'),
    # path('random/', views.random, name='random'),
    #path('image/', TemplateView.as_view(template_name="fileprocess/images_to_test.html"), name='image'),
    # path('output_sql', views.output_sql, name='output_sql')
