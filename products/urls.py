from django.urls import path
from . import views

app_name = "products"
urlpatterns = [
    path("index/", views.index, name="index"),
    path("<int:pid>/detail/", views.detail, name="detail"),
    path("create/", views.create, name="create"),
    path("<int:pid>/likey/", views.likey, name="likey"),
    path("myprodlist/", views.myprodlist, name="myprodlist"),
    path("minelist/", views.minelist, name="minelist"),
    path("<int:pid>/mine/", views.mine, name="mine"),
    path("<int:pid>/update/", views.update, name="update"),
    path("delete/", views.delete, name="delete"),
    path("buy/", views.buy, name="buy"),
    path("buylist/", views.buylist, name="buylist"),
    path("pointlist/", views.pointlist, name="pointlist"),
]