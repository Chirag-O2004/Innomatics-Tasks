from fastapi import FastAPI,Query
 
app = FastAPI()
 
# ── Temporary data — acting as our database for now ──────────
products = [
    {'id': 1, 'name': 'Wireless Mouse', 'price': 499, 'category': 'Electronics', 'in_stock': True},
    {'id': 2, 'name': 'Notebook', 'price': 99, 'category': 'Stationery', 'in_stock': True},
    {'id': 3, 'name': 'USB Hub', 'price': 799, 'category': 'Electronics', 'in_stock': False},
    {'id': 4, 'name': 'Pen Set', 'price': 49, 'category': 'Stationery', 'in_stock': True},

    {'id': 5, 'name': 'Bluetooth Keyboard', 'price': 1299, 'category': 'Electronics', 'in_stock': True},
    {'id': 6, 'name': 'Sticky Notes', 'price': 59, 'category': 'Stationery', 'in_stock': True},
    {'id': 7, 'name': 'Laptop Stand', 'price': 999, 'category': 'Electronics', 'in_stock': True},
    {'id': 8, 'name': 'Highlighter Set', 'price': 149, 'category': 'Stationery', 'in_stock': False},
]
 
# ── Endpoint 0 — Home ────────────────────────────────────────
@app.get('/')
def home():
    return {'message': 'Welcome to our E-commerce API'}

@app.get("/products/deals")
def get_deals():
    cheapest_products = min(products, key=lambda p: p['price'])
    expensive_products = max(products, key=lambda p: p['price'])
    return {'best_deals': cheapest_products, 'expensive_deals': expensive_products, 'count': len(cheapest_products)}
 
# ── Endpoint 1 — Return all products ──────────────────────────
@app.get('/products')
def get_all_products():
    return {'products': products, 'total': len(products)}

@app.get('/products/filter')
def filter_products(
    category:  str  = Query(None, description='Electronics or Stationery'),
    max_price: int  = Query(None, description='Maximum price'),
    in_stock:  bool = Query(None, description='True = in stock only')
):
    result = products          # start with all products
 
    if category:
        result = [p for p in result if p['category'] == category]
 
    if max_price:
        result = [p for p in result if p['price'] <= max_price]
 
    if in_stock is not None:
        result = [p for p in result if p['in_stock'] == in_stock]
 
    return {'filtered_products': result, 'count': len(result)}
 
@app.get('/products/category/{category_name}')
def get_products_by_category(category_name: str):
    category_products = [p for p in products if p['category'].lower() == category_name.lower()]
    if not category_products:
        return {'error': f'No products found in category "{category_name}"'}
    return {'products': category_products, 'count': len(category_products)}

@app.get('/products/instock')
def get_in_stock_products():
    in_stock_products = [p for p in products if p['in_stock'] == True]
    return {'in_stock_products': in_stock_products, 'count': len(in_stock_products)}

# ── Endpoint 2 — Return one product by its ID ──────────────────
@app.get('/products/{product_id}')
def get_product(product_id: int):
    for product in products:
        if product['id'] == product_id:
            return {'product': product}
    return {'error': 'Product not found'}

@app.get('/store/summary')
def store_summary():
    total_products = len(products)
    in_stock_count = sum(1 for p in products if p['in_stock'])
    out_of_stock_count = total_products - in_stock_count
    categories = list(set(p['category'] for p in products))
    average_price = sum(p['price'] for p in products) / total_products if total_products > 0 else 0
    return {
        'store_name': 'My E-commerce Store',
        'total_products': total_products,
        'in_stock': in_stock_count,
        'out_of_stock': out_of_stock_count,
        'average_price': average_price,
        'categories': categories
    }

@app.get("/products/search/{keyword}")
def search_products(keyword: str):
    keyword_lower = keyword.lower()
    matching_products = [p for p in products if keyword_lower in p['name'].lower()]
    if not matching_products:
        return {'message': f'No products found matching "{keyword}"'}
    return {'keyword': keyword, 'matching_products': matching_products, 'count': len(matching_products)}

