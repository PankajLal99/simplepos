from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Product, Stock, StockTransaction, Invoice, InvoiceItem
import json
import logging
from django.utils import timezone
from django.db.models import Sum, Count
from datetime import datetime, time
from django.template.loader import render_to_string, get_template
from xhtml2pdf import pisa
from io import BytesIO

# Configure logging
logger = logging.getLogger(__name__)

def pos_home(request):
    return render(request, 'pos/home.html')

def products_list(request):
    products = Product.objects.all()
    return render(request, 'pos/products.html', {'products': products})

@csrf_exempt
@require_http_methods(['POST'])
def search_product(request):
    data = json.loads(request.body)
    query = data.get('query', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'status': 'error', 'message': 'Query too short'})
    
    products = Product.objects.filter(name__icontains=query)[:5]
    
    if not products:
        return JsonResponse({
            'status': 'not_found',
            'message': f'No products found matching "{query}". Would you like to create a new product?'
        })
    
    return JsonResponse({
        'status': 'success',
        'products': [{
            'id': p.id,
            'name': p.name,
            'price': float(p.price),
            'sku': p.sku,
            'barcode': p.barcode
        } for p in products]
    })

@csrf_exempt
@require_http_methods(['POST'])
def create_product(request):
    data = json.loads(request.body)
    
    try:
        product = Product.objects.create(
            name=data['name'],
            price=data['price'],
            maintain_stock=data.get('maintain_stock', False)
        )
        
        if product.maintain_stock:
            Stock.objects.create(product=product)
        
        return JsonResponse({
            'status': 'success',
            'product': {
                'id': product.id,
                'name': product.name,
                'price': float(product.price),
                'sku': product.sku,
                'barcode': product.barcode
            }
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(['GET', 'PUT'])
def product_detail(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        
        if request.method == 'GET':
            return JsonResponse({
                'id': product.id,
                'name': product.name,
                'price': float(product.price),
                'sku': product.sku,
                'barcode': product.barcode,
                'maintain_stock': product.maintain_stock
            })
        else:  # PUT
            data = json.loads(request.body)
            product.name = data['name']
            product.price = data['price']
            product.maintain_stock = data['maintain_stock']
            product.save()
            
            # Handle stock management
            if product.maintain_stock and not hasattr(product, 'stock'):
                Stock.objects.create(product=product)
            elif not product.maintain_stock and hasattr(product, 'stock'):
                product.stock.delete()
            
            return JsonResponse({'status': 'success'})
    except Product.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Product not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@csrf_exempt
@require_http_methods(['GET', 'POST'])
def product_stock(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        
        if not product.maintain_stock:
            return JsonResponse({'status': 'error', 'message': 'Stock management not enabled for this product'}, status=400)
        
        stock, created = Stock.objects.get_or_create(product=product)
        
        if request.method == 'GET':
            transactions = StockTransaction.objects.filter(stock=stock).order_by('-created_at')[:10]
            return JsonResponse({
                'current_quantity': stock.current_quantity,
                'transactions': [{
                    'transaction_type': t.transaction_type,
                    'quantity': t.quantity,
                    'created_at': t.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'notes': t.notes
                } for t in transactions]
            })
        else:  # POST
            data = json.loads(request.body)
            transaction = StockTransaction.objects.create(
                stock=stock,
                transaction_type=data['transaction_type'],
                quantity=data['quantity'],
                notes=data.get('notes', '')
            )
            return JsonResponse({'status': 'success'})
    except Product.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Product not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def pricing(request):
    return render(request, 'pos/pricing.html')

@require_http_methods(["GET"])
def check_invoice_limit(request):
    """Check if user has exceeded their free invoice limit"""
    # Get total invoices created
    total_invoices = Invoice.objects.count()
    
    # Free limit is 100 invoices
    FREE_LIMIT = 100
    
    if total_invoices >= FREE_LIMIT:
        return JsonResponse({
            'status': 'limit_exceeded',
            'message': f'You have reached the free limit of {FREE_LIMIT} invoices. Please subscribe to continue creating invoices.'
        })
    
    return JsonResponse({
        'status': 'ok',
        'remaining': FREE_LIMIT - total_invoices
    })

@csrf_exempt
@require_http_methods(["POST"])
def create_invoice(request):
    try:
        # Parse request data
        try:
            data = json.loads(request.body)
            logger.info(f'Parsed JSON data: {data}')
        except Exception as e:
            logger.error(f'JSON decode error: {str(e)}')
            return JsonResponse({'status': 'error', 'message': f'Invalid JSON data: {str(e)}'}, status=400)

        if not isinstance(data, dict) or 'items' not in data or not isinstance(data['items'], list):
            return JsonResponse({'status': 'error', 'message': 'Invalid data format'}, status=400)

        # Create invoice
        invoice = Invoice.objects.create(total_amount=0)
        total_amount = 0

        for item in data['items']:
            try:
                product = Product.objects.get(id=item['product_id'])
                invoice_item = InvoiceItem.objects.create(
                    invoice=invoice,
                    product=product,
                    quantity=item['quantity'],
                    price=item['price']
                )
                total_amount += invoice_item.subtotal
            except Exception as e:
                invoice.delete()
                return JsonResponse({'status': 'error', 'message': f'Error processing item: {str(e)}'}, status=400)

        invoice.total_amount = total_amount
        invoice.save()

        return JsonResponse({'status': 'success', 'invoice_id': invoice.id})

    except Exception as e:
        logger.error(f'Unexpected error in create_invoice: {str(e)}')
        return JsonResponse({'status': 'error', 'message': f'Error creating invoice: {str(e)}'}, status=500)

def print_invoice(request, invoice_id):
    try:
        invoice = Invoice.objects.get(id=invoice_id)
        is_modal = request.GET.get('modal', 'false').lower() == 'true'
        if hasattr(invoice, 'round_off') and invoice.round_off:
            grand_total = float(invoice.total_amount) + float(invoice.round_off)
        else:
            grand_total = float(invoice.total_amount)
        if is_modal:
            # Return only the invoice content for modal
            return render(request, 'pos/invoice_content.html', {
                'invoice': invoice,
                'is_modal': True,
                'grand_total': grand_total,
            })
        else:
            # Return full print layout
            return render(request, 'pos/print.html', {
                'invoice': invoice,
                'is_modal': False,
                'grand_total': grand_total,
            })
    except Invoice.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Invoice not found'}, status=404)

def sales_report(request):
    # Get all dates that have invoices
    available_dates = Invoice.objects.dates('created_at', 'day').order_by('-created_at')
    
    # Format dates for JavaScript
    formatted_dates = [date.strftime('%Y-%m-%d') for date in available_dates]
    dates_json = json.dumps(formatted_dates)
    
    # Get selected date from request or default to today
    selected_date = request.GET.get('date')
    if selected_date:
        try:
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        except ValueError:
            selected_date = timezone.now().date()
    else:
        selected_date = timezone.now().date()

    # Get invoices for selected date
    start_of_day = timezone.make_aware(datetime.combine(selected_date, time.min))
    end_of_day = timezone.make_aware(datetime.combine(selected_date, time.max))
    
    invoices = Invoice.objects.filter(
        created_at__range=(start_of_day, end_of_day)
    ).order_by('-created_at')

    # Calculate grand_total for each invoice
    invoice_list = []
    for invoice in invoices:
        if hasattr(invoice, 'round_off') and invoice.round_off:
            grand_total = float(invoice.total_amount) + float(invoice.round_off)
        else:
            grand_total = float(invoice.total_amount)
        invoice.grand_total = grand_total
        invoice_list.append(invoice)

    # Calculate total sales and items
    total_sales = sum(invoice.total_amount for invoice in invoices)
    total_invoices = invoices.count()

    # Get top selling products
    top_products = InvoiceItem.objects.filter(
        invoice__in=invoices
    ).values(
        'product__name'
    ).annotate(
        quantity_sold=Sum('quantity'),
        total_sales=Sum('subtotal')
    ).order_by('-total_sales')[:5]

    context = {
        'invoices': invoice_list,
        'total_sales': total_sales,
        'total_invoices': total_invoices,
        'top_products': top_products,
        'selected_date': selected_date,
        'available_dates': available_dates,
        'formatted_dates': formatted_dates,
        'dates_json': dates_json,
    }
    return render(request, 'pos/sales_report.html', context)

@csrf_exempt
@require_http_methods(['DELETE'])
def delete_invoice(request, invoice_id):
    try:
        invoice = Invoice.objects.get(id=invoice_id)
        
        # Get all items before deleting
        items = invoice.items.all()
        
        # Delete the invoice (this will trigger the cascade delete for items)
        invoice.delete()
        
        # Update stock for products that maintain stock
        for item in items:
            if item.product.maintain_stock:
                stock = Stock.objects.get(product=item.product)
                # Add back the quantity to stock
                StockTransaction.objects.create(
                    stock=stock,
                    transaction_type='IN',
                    quantity=item.quantity,
                    reference=f"INV-{invoice.invoice_number}-DELETED",
                    notes=f"Stock returned due to invoice deletion"
                )
        
        return JsonResponse({'status': 'success'})
    except Invoice.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Invoice not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def export_sales_report_pdf(request):
    selected_date = request.GET.get('date')
    if selected_date:
        try:
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        except ValueError:
            selected_date = timezone.now().date()
    else:
        selected_date = timezone.now().date()

    start_of_day = timezone.make_aware(datetime.combine(selected_date, time.min))
    end_of_day = timezone.make_aware(datetime.combine(selected_date, time.max))

    invoices = Invoice.objects.filter(
        created_at__range=(start_of_day, end_of_day)
    ).order_by('-created_at')

    total_sales = sum(invoice.total_amount for invoice in invoices)
    total_invoices = invoices.count()

    top_products = InvoiceItem.objects.filter(
        invoice__in=invoices
    ).values(
        'product__name'
    ).annotate(
        quantity_sold=Sum('quantity'),
        total_sales=Sum('subtotal')
    ).order_by('-total_sales')[:5]

    context = {
        'selected_date': selected_date,
        'invoices': invoices,
        'total_sales': total_sales,
        'total_invoices': total_invoices,
        'top_products': top_products,
        'now': timezone.now(),
    }

    template = get_template('pos/sales_report_pdf.html')
    html = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'filename="sales_report_{selected_date}.pdf"'
        return response
    else:
        return HttpResponse('Error generating PDF', status=500)
