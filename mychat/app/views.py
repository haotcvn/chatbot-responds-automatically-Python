import json
import logging
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout, decorators
from django.contrib.auth.models import User
from django.contrib import messages
from .chat import bot1, bot2

def account(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('/')
        return render(request, 'app/login.html')

    elif request.method == 'POST':
        try:
            if 'register' in request.POST:
                # Xử lý đăng ký
                name = request.POST.get('name')
                email = request.POST.get('email')
                password = request.POST.get('password')
                
                if not User.objects.filter(email=email).exists():
                    user = User.objects.create_user(username=email, email=email, password=password, first_name=name)
                    user.save()
                    messages.success(request, 'Đăng ký thành công! Vui lòng đăng nhập.')
                    return redirect('/account/')
                else:
                    messages.info(request, 'Email đã tồn tại.')
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

            elif 'login' in request.POST:
                # Xử lý đăng nhập
                email = request.POST.get('email')
                password = request.POST.get('password')
                
                try:
                    user_obj = User.objects.get(email=email)
                except User.DoesNotExist:
                    messages.info(request, 'Tài khoản không tồn tại')
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

                authen_obj = authenticate(username=user_obj.username, password=password)

                if authen_obj:
                    login(request, authen_obj)
                    return redirect('/')

                messages.info(request, 'Mật khẩu không hợp lệ')
                return redirect('/account/')
            
            return render(request, 'app/login.html')
        except Exception as e:
            logging.error(f"Login failed: {str(e)}")
            messages.error(request, 'Có lỗi xảy ra, vui lòng thử lại sau')
            return redirect('/account/')
        
def logout_view(request):
    logout(request)
    messages.success(request, 'Bạn đã đăng xuất thành công.')
    return redirect('/')

@decorators.login_required(login_url="/account/")    
def index(request):
    return render(request, 'app/index.html')

@csrf_exempt
def get_answer(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_question = data['question']
        if not user_question:
            return JsonResponse({'error': 'Question is empty'})
        try:
            data_root = bot1.answers(user_question)
            result = bot2.answers(user_question, data_root)
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'answer': 'Lỗi không thể lấy được câu hỏi'})