from django.http import HttpResponse


def home(request):
    return HttpResponse('Публичная часть сайта — в разработке')