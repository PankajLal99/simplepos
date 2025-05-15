from django.urls import path
from . import views

urlpatterns = [
    path('', views.pos_home, name='pos_home'),
    path('products/', views.products_list, name='products_list'),
    path('pricing/', views.pricing, name='pricing'),
    path('sales-report/', views.sales_report, name='sales_report'),
    path('sales-report/export/pdf/', views.export_sales_report_pdf, name='export_sales_report_pdf'),
    path('api/products/search/', views.search_product, name='search_product'),
    path('api/products/', views.create_product, name='create_product'),
    path('api/products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('api/products/<int:product_id>/stock/', views.product_stock, name='product_stock'),
    path('api/check-invoice-limit/', views.check_invoice_limit, name='check_invoice_limit'),
    path('api/invoices/', views.create_invoice, name='create_invoice'),
    path('api/invoices/<int:invoice_id>/', views.delete_invoice, name='delete_invoice'),
    path('invoices/<int:invoice_id>/print/', views.print_invoice, name='print_invoice'),
] 