from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Product, Comment, Cart, Rating
from app_users.models import Customer
from .forms import CommentForm
from django.db.models import Avg



def home_page(request):
    query = request.GET.get('q')
    search = request.GET.get('search', '')

    products = Product.objects.filter(name__icontains=search)

    if query:
        if query == 'expensive':
            products = products.order_by('-new_price')
        elif query == 'cheap':
            products = products.order_by('new_price')
        elif query == 'rating':
            products = sorted(products, key=lambda p: p.ratings.aggregate(avg=Avg('value'))['avg'] or 0, reverse=True)
        elif query == 'new-arrivals':
            products = products.order_by('-created')

    # Yulduzlar bo‘yicha strukturani qurish
    products_with_stars = []
    for product in products:
        ratings = product.ratings.all()
        avg_rating = round(sum(r.value for r in ratings) / ratings.count(), 1) if ratings.exists() else 0
        full = int(avg_rating)
        half = 1 if avg_rating - full >= 0.5 else 0
        empty = 5 - full - half

        products_with_stars.append({
            'product': product,
            'full_stars': range(full),
            'half_star': half,
            'empty_stars': range(empty),
            'avg_rating': avg_rating,
        })

    context = {
        'products_with_stars': products_with_stars,
        'search': search,
        'is_home_page': True,
        'cart_products_quantity': len(request.user.cart_set.all()) if request.user.is_authenticated else 0,
    }

    return render(request, 'index.html', context)




def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Reytingni tekshirish
    user_rating = None
    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(product=product, user=request.user).first()

    # POST so'rovini qayta ishlash
    if request.method == 'POST' and request.user.is_authenticated:
        if 'rating' in request.POST:
            if user_rating:
                messages.info(request, "Siz allaqachon reyting bergansiz.")
            else:
                value = int(request.POST.get('rating'))
                Rating.objects.create(product=product, user=request.user, value=value)
                messages.success(request, "Reytingingiz saqlandi.")
            return redirect(f'/detail/{product_id}#rating-section')

        # Izohni saqlash
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.owner = request.user
            comment.product = product
            comment.save()
            messages.success(request, "Izohingiz muvaffaqiyatli saqlandi.")
            return redirect(f'/detail/{product_id}#comments-section')
    else:
        form = CommentForm()

    # Reyting hisoblash
    ratings = product.ratings.all()
    avg_rating = round(sum(r.value for r in ratings) / ratings.count(), 1) if ratings.exists() else 0

    # Yulduzlar soni (to‘liq, yarim, bo‘sh)
    full_stars = int(avg_rating)
    half_star = 1 if (avg_rating - full_stars) >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star

    context = {
        'product': product,
        'form': form,
        'last_3_comments': product.comment_set.all().order_by('-created')[:5],
        'user_rating': user_rating,
        'avg_rating': avg_rating,
        'full_stars': range(full_stars),
        'half_star': half_star,
        'empty_stars': range(empty_stars),
    }

    return render(request, 'detail.html', context)





@login_required(login_url='login')
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')

        try:
            cart = Cart.objects.create(
                product=get_object_or_404(Product, id=product_id),
                user=get_object_or_404(Customer, id=request.user.id),
                quantity=quantity
            )
            cart.save()
        except:
            product = request.user.cart_set.all().get(product__id=product_id)
            product.quantity += int(quantity)
            product.save()

    return redirect('detail', product_id=product_id)


@login_required(login_url='login')
def change_cart_product_quantity(request, cart_product_id, action):
    cart_product = get_object_or_404(Cart, id=cart_product_id)
    cart_product.quantity += 1 if action == "increment" else -1
    cart_product.save()
    return redirect('cart')


