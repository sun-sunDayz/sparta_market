from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate
from products.models import PointHistory
from django.contrib.auth.hashers import check_password
from django.http import HttpResponseRedirect, JsonResponse
from django.utils.safestring import mark_safe
from .models import User
from django.contrib import messages
from django.utils import timezone
import json

# Create your views here.
def index(request):
    return render(request, "accounts/index.html")

def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        userpass = request.POST.get("password")
        user = authenticate(request, username=username, password=userpass)
        if user is not None:
            if user.last_login:
                if user.last_login.date() != timezone.now().date():
                    user.point += 1000
                    user.save()
                    PointHistory.objects.create(user=user, change_amount=1000, reason="로그인 보너스")

                    message = mark_safe(f"{user.username} 님! \n오늘도 오셨군요! 추가로 <b class='add-point'>1000 point</b> 가 지급되었습니다!")
                    messages.success(request,message)
                else:
                    messages.success(request, f"{user.username} 님! 환영합니다!")
            else:
                user.point += 1000
                user.save()
                PointHistory.objects.create(user=user, change_amount=1000, reason="로그인 보너스")
                message = mark_safe(f"{user.username} 님! 환영합니다! \n저희 사이트는 하루에 한 번 로그인을 하면 <b class='add-point'>10 point</b> 가 지급되요!")
                messages.success(request, message)
            auth_login(request, user)
            return redirect("accounts:index")
        else:
            messages.error(request, "회원정보가 일치하지 않습니다. 다시 시도해주세요.") 
    return render(request, "accounts/login.html")

def logout(request):
    auth_logout(request)
    messages.success(request, "로그아웃 되었습니다. 다음에 또 뵙겠습니다!")
    return redirect("accounts:index")

def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        userpass = request.POST.get("regpass")
        email = request.POST.get("usermail")
        profile_pic = request.FILES.get("profile_pic")
        introduce = request.POST.get("introduce")
        if checkSignup(request, username, userpass, email):
            User.objects.create_user(username=username, password=userpass, email=email, profile_pic=profile_pic, introduce=introduce)
            message = mark_safe(f"{username} 님! \n 회원가입을 축하드립니다! \n 회원가입을 축하하며 <b class='add-point'>10000 Point</b> 를 지급해드립니다! \n로그인해주세요!")
            PointHistory.objects.create(user=User.objects.get(username=username), change_amount=10000, reason="회원가입 보너스")
            messages.success(request, message)
            return redirect("accounts:login")
        else:
            messages.success(request, "회원가입에 실패하였습니다. 다시 시도해주세요.")
    return render(request, "accounts/signup.html")

def checkSignup(request, username, userpass, email):
    if User.objects.filter(username=username).exists():
        messages.error(request, "이미 존재하는 아이디입니다.")
    if User.objects.filter(email=email).exists():
        messages.error(request, "이미 존재하는 이메일입니다.")
    if len(userpass) < 8:
        messages.error(request, "비밀번호는 8자 이상으로 설정해주세요.")
    if not any(char.isdigit() for char in userpass):
        messages.error(request, "비밀번호는 숫자를 포함해야 합니다.")
    if not any(char.isalpha() for char in userpass):
        messages.error(request, "비밀번호는 문자를 포함해야 합니다.")
    if not any(char.isupper() for char in userpass):
        messages.error(request, "비밀번호는 대문자를 포함해야 합니다.")
    if not any(char.islower() for char in userpass):
        messages.error(request, "비밀번호는 소문자를 포함해야 합니다.")
    if not any(char in "!@#$%^&*()_+-=,.<>?/;:'" for char in userpass):
        messages.error(request, "비밀번호는 특수문자를 포함해야 합니다.")
    if messages.get_messages(request):
        return False
    return True

def profile(request):
    return render(request, "accounts/profile.html")       

def seller(request, name):
    user = User.objects.get(username=name)
    context = {
        "userdata" : user,
    }
    return render(request, "products/seller.html", context)

def update(request):
    if request.method == "POST":
        user = request.user
        changePic, changeComment, changePass = request.FILES.get("changePic"), request.POST.get("changeComment"), request.POST.get("changePass")
        if changePic:
            user.profile_pic.delete()
            user.profile_pic = changePic
        if changeComment:
            user.introduce = changeComment
        if changePass:
            user.set_password(changePass)
            user.save()
            messages.success(request, "비밀번호가 변경되었습니다. 다시 로그인해주세요.")
            return redirect("accounts:login")
        # 변경사항 저장
        user.save()
        messages.success(request, "변경사항이 저장되었습니다.")
    return render(request, "accounts/profile.html")

def delete(request):
    if request.method == "POST":
        request.user.profile_pic.delete()
        request.user.delete()
        auth_logout(request)
        messages.success(request, "회원탈퇴가 완료되었습니다.")
        return JsonResponse({"result": True})

def nameDuplicate(request):
    username = request.POST.get("username")
    result = User.objects.filter(username=username).exists()
    return JsonResponse({"result": result})

def mailDuplicate(request):
    email = request.POST.get("usermail")
    result = User.objects.filter(email=email).exists()
    return JsonResponse({"result": result})

def checkpassword(request):
    print(request.POST)
    password = request.POST.get("password")
    result = check_password(password, request.user.password)
    return JsonResponse({"result": result})

def follow(request, name):
    user = request.user
    target = User.objects.get(username=name)
    if user != target:
        if target in user.following.all():
            user.following.remove(target)
            messages.error(request, f"{target.username} 님을 언팔로우합니다.")
        else:
            user.following.add(target)
            messages.success(request, f"{target.username} 님을 팔로우합니다.")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
