from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.http import JsonResponse
from .models import Products, HashTag, BuyList, PointHistory, ProductRating
from django.core.paginator import Paginator
from django.db.models import Count
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils.safestring import mark_safe


# Create your views here.
@login_required
def index(request):
    page = request.GET.get("page", 1)
    cate = request.GET.get("cate", "")
    sort = request.GET.get("sort","")
    keyword = request.GET.get("keyword", "")
    stockOut = request.GET.get("stockOut", False)
    saleProd = request.GET.get("saleProd", False)

    if keyword:
        if cate == "title":
            products = Products.objects.filter(title__contains=keyword)
        elif cate == "seller":
            products = Products.objects.filter(seller__username=keyword)
        elif cate == "hashtag":
            products = Products.objects.filter(hashtags__name=keyword)
    else:   
        products = Products.objects.all()

    if stockOut == 'false':
        products = products.filter(~Q(stock=0))
    if saleProd == 'true':
        products = products.filter(~Q(sale_price=0))

    
    if not sort or sort == "new":
        products = products.order_by("-created_at")
    elif sort == "cheap":
        products = products.order_by("display_price")
    elif sort == "expensive":
        products = products.order_by("-display_price")
    elif sort == "hits":
        products = products.order_by("-hits")
    elif sort == "likey":
        products = products.annotate(likey_count=Count('likey')).order_by('-likey_count')
    elif sort == "score":
        products = products.order_by("-score")
        
    pag = Paginator(products, 4)
    obj = pag.get_page(page)
    exposedPost = int(page) * 4

    if exposedPost > obj.paginator.count:
        exposedPost = obj.paginator.count

    context = {
        "obj": obj,
        "page": page,
        "cate": cate,
        "keyword": keyword,
        "sort": sort,
        "stockOut": stockOut,
        "saleProd": saleProd,
        "exposedPost": exposedPost,
    }
    return render(request, "products/index.html", context)

@login_required
def detail(request, pid):
    product = get_object_or_404(Products, id=pid)
    if request.META.get('HTTP_REFERER') and not f"/{pid}/detail/" in request.META.get('HTTP_REFERER'):
        product.hits += 1
        product.save()
    context = {
        "p": product,
    }
    return render(request, "products/detail.html", context)

@login_required
def create(request):
    if request.method == "POST":
        title = request.POST.get("productTitle")
        price = request.POST.get("productPrice")
        sale_price = request.POST.get("productSalePrice")
        description = request.POST.get("productDesc")
        image = request.FILES.get("productImage")
        stock = request.POST.get("productStock")
        hashtags = request.POST.getlist("productHashtag")  
        seller = request.user
        display_price = price
        if sale_price:
            display_price = sale_price
        else:
            sale_price = 0
        if sale_price < 0 or price < 0:
            messages.warning(request, "<경고> 가격은 음수가 될 수 없습니다!")
            return redirect("products:create")
        product = Products(title=title, price=price, stock=stock, sale_price=sale_price, display_price=display_price, description=description, image=image, seller=seller)
        product.save()

        for tag in hashtags:
            tag = tag.split()[0].replace("#", "")
            if not HashTag.objects.filter(name=tag).exists():
                hashtag = HashTag(name=tag)
                hashtag.save()
            else:
                hashtag = HashTag.objects.get(name=tag)
            product.hashtags.add(hashtag)
        messages.success(request, "상품이 등록되었습니다.")
        return redirect('products:index')
    return render(request, "products/create.html")

@login_required
def likey(request, pid):
    p = get_object_or_404(Products, id=pid)
    user = request.user
    if user in p.likey.all():
        p.likey.remove(user)
        messages.error(request, "좋아요를 취소합니다.")
    else:
        p.likey.add(user)
        messages.success(request, "좋아요를 눌렀습니다.")
    return redirect("products:detail", pid)

@login_required
def mine(request, pid):
    p = get_object_or_404(Products, id=pid)
    user = request.user
    if user == p.seller:
        messages.error(request, "자신의 상품은 찜할 수 없습니다.")
        return redirect(request.META.get('HTTP_REFERER'))
    if p in user.wishprod.all():
        user.wishprod.remove(p)
        messages.error(request, "찜을 취소합니다.")
    else:
        user.wishprod.add(p)
        messages.success(request, "찜을 눌렀습니다.")
    return redirect(request.META.get('HTTP_REFERER'))

@login_required
def minelist(request):
    user = request.user
    products = user.wishprod.all()
    context = {
        "products": products,
    }
    return render(request, "products/minelist.html", context)

@login_required
def update(request, pid):
    p = get_object_or_404(Products, id=pid)
    if request.method == "POST":
        title = request.POST.get("productTitle")
        price = request.POST.get("productPrice")
        sale_price = request.POST.get("productSalePrice")
        description = request.POST.get("productDesc")
        image = request.FILES.get("productImage")
        stock = request.POST.get("productStock")
        hashtags = request.POST.getlist("productHashtag")
        pre_page = request.POST.get("prepage", "products:index")
        display_price = price
        if sale_price:
            display_price = sale_price
            p.sale_price = sale_price
        else:
            p.sale_price = 0
        p.title = title
        p.price = price
        p.description = description
        p.display_price = display_price
        p.stock = stock
        if image:
            p.image.delete()
            p.image = image
        p.save()
        p.hashtags.clear()
        for tag in hashtags:
            tag = tag.split()[0].replace("#", "")
            if not HashTag.objects.filter(name=tag).exists():
                hashtag = HashTag(name=tag)
                hashtag.save()
            else:
                hashtag = HashTag.objects.get(name=tag)
            p.hashtags.add(hashtag)
        messages.success(request, "상품이 수정되었습니다.")
        return redirect(pre_page)
    context = {
        "p": p,
        "prepage":request.META.get('HTTP_REFERER')
    }
    return render(request, "products/update.html", context)


@require_POST
def delete(request):
    pid = request.POST.get("product_id")
    p = get_object_or_404(Products, id=pid)
    if p.seller == request.user:
        p.image.delete()
        p.delete()
        messages.error(request, "상품이 삭제되었습니다.")
    return JsonResponse({"result": True})

@login_required
def myprodlist(request):
    user = request.user
    products = user.products.all()
    context = {
        "products": products,
    }
    return render(request, "products/myprodlist.html", context)

@login_required
def buy(request):
    if request.method == "POST":
        pids = request.POST.getlist("product_id")
        quantities = request.POST.getlist("quantity")
        total = 0
        for pid, quantity in zip(pids, quantities):
            product = get_object_or_404(Products, id=pid)
            quantity = int(quantity)
            total += product.display_price * quantity
        if request.user.point < total:
            messages.error(request, "포인트가 부족합니다.")
            return redirect("products:buy")
        
        for pid, quantity in zip(pids, quantities):
            product = get_object_or_404(Products, id=pid)
            quantity = int(quantity)
            BuyList(product=product, priced=product.display_price, buyer=request.user, quantity=quantity).save()
            PointHistory(user=request.user, change_amount=-(product.display_price * quantity), reason=f"{product.title} {quantity} 개 구매").save()
            product.stock -= quantity
            product.save()
            product.seller.point += product.display_price * quantity
            PointHistory(user=product.seller, change_amount=product.display_price * quantity, reason=f"{product.title} {quantity} 개 판매").save()
            product.seller.save()
        
        request.user.point -= total
        request.user.save()
        messages.success(request, "구매가 완료되었습니다.")
        return redirect("products:buylist")
    
    product_id = request.GET.get("product_id")
    if product_id:
        context = {
            "products": [get_object_or_404(Products, id=product_id)]
        }
    else:
        context = {
            "products": request.user.wishprod.all()
        }
    return render(request, "products/buy.html", context)

@login_required   
def buylist(request):
    user = request.user
    products = user.buylist.all()
    products = products.order_by("-created_at")
    context = {
        "products": products,
    }
    return render(request, "products/buylist.html", context)

@login_required
def pointlist(request):
    user = request.user
    points = user.pointhistory.all()
    points = points.order_by("-created_at")
    context = {
        "points": points,
    }
    return render(request, "products/pointlist.html", context)


@require_POST
def rating(request):
    pid = request.POST.get("product_id")
    rating = request.POST.get("rating")
    product = get_object_or_404(Products, id=pid)
    if product.buylist.filter(buyer=request.user).exists():
        if not product.ratings.filter(user=request.user).exists():
            ProductRating(user=request.user, product=product, rating=rating).save()
            request.user.point += 1000
            request.user.save()
            message = mark_safe("평가가 완료되었습니다. <br><b class='add-point'>1000 Point</b>가 지급되었습니다.")
            PointHistory(user=request.user, change_amount=1000, reason=f"{product.title} 상품 평가").save()
            messages.success(request, message)
            li = []
            for pro in product.ratings.all():
                li.append(pro.rating)
            product.score = round(sum(li)/len(li),2)
            product.save()
    else:
        messages.error(request, "구매한 상품만 평가할 수 있습니다.")
    return redirect("products:buylist")         