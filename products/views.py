from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Products, HashTag, BuyList, PointHistory
from django.core.paginator import Paginator
from django.db.models import Count
from django.db.models import Q
from django.contrib import messages

# Create your views here.
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
    print(exposedPost)
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

def detail(request, pid):
    product = Products.objects.get(id=pid)
    if request.META.get('HTTP_REFERER') and not f"/{pid}/detail/" in request.META.get('HTTP_REFERER'):
        product.hits += 1
        product.save()
    context = {
        "p": product,
    }
    return render(request, "products/detail.html", context)

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

def likey(request, pid):
    p = Products.objects.get(id=pid)
    user = request.user
    if user in p.likey.all():
        p.likey.remove(user)
        messages.error(request, "좋아요를 취소합니다.")
    else:
        p.likey.add(user)
        messages.success(request, "좋아요를 눌렀습니다.")
    return redirect("products:detail", pid)

def mine(request, pid):
    p = Products.objects.get(id=pid)
    user = request.user
    if p in user.wishprod.all():
        user.wishprod.remove(p)
        messages.error(request, "찜을 취소합니다.")
    else:
        user.wishprod.add(p)
        messages.success(request, "찜을 눌렀습니다.")
    return redirect(request.META.get('HTTP_REFERER'))

def minelist(request):
    user = request.user
    products = user.wishprod.all()
    context = {
        "products": products,
    }
    return render(request, "products/minelist.html", context)

def update(request, pid):
    p = Products.objects.get(id=pid)
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


def delete(request):
    if request.method == "POST":
        pid = request.POST.get("product_id")
        print(pid)
        p = Products.objects.get(id=pid)
        if p.seller == request.user:
            p.image.delete()
            p.delete()
            messages.error(request, "상품이 삭제되었습니다.")
        return JsonResponse({"result": True})

def myprodlist(request):
    user = request.user
    products = user.products.all()
    context = {
        "products": products,
    }
    return render(request, "products/myprodlist.html", context)

def buy(request):
    if request.method == "POST":
        pids = request.POST.getlist("product_id")
        quantities = request.POST.getlist("quantity")
        total = 0
        for pid, quantity in zip(pids, quantities):
            product = Products.objects.get(id=pid)
            quantity = int(quantity)
            total += product.display_price * quantity
        if request.user.point < total:
            messages.error(request, "포인트가 부족합니다.")
            return redirect("products:buy")
        
        for pid, quantity in zip(pids, quantities):
            product = Products.objects.get(id=pid)
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
            "products": [Products.objects.get(id=product_id)]
        }
    else:
        context = {
            "products": request.user.wishprod.all()
        }
    return render(request, "products/buy.html", context)
    
def buylist(request):
    user = request.user
    products = user.buylist.all()
    products = products.order_by("-created_at")
    context = {
        "products": products,
    }
    return render(request, "products/buylist.html", context)

def pointlist(request):
    user = request.user
    points = user.pointhistory.all()
    points = points.order_by("-created_at")
    context = {
        "points": points,
    }
    return render(request, "products/pointlist.html", context)