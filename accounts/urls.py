from django.urls import path
from . import views

app_name = "accounts"
urlpatterns = [
    path("index/", views.index, name="index"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("signup/", views.signup, name="signup"),
    path("profile/", views.profile, name="profile"),
    path("seller/<str:name>/", views.seller, name="seller"),
    path("follow/<str:name>/", views.follow, name="follow"),
    path("update/", views.update, name="update"),
    path("delete/", views.delete, name="delete"),
    path("nameDuplicate/", views.nameDuplicate, name="nameDuplicate"),
    path("mailDuplicate/", views.mailDuplicate, name="mailDuplicate"),
    path("checkpassword/", views.checkpassword, name="checkpassword"),

]