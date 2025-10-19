from django.http import JsonResponse

def set_auth_cookies(response, access_token, refresh_token):
    response.set_cookie(
        key='access_token',
        value=access_token,
        httponly=True,
        max_age=3600,
        samesite='Lax'
    )
    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,
        max_age=3600,
        samesite='Lax'
    )
    return response

def delete_auth_cookies(response):
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response

def get_refresh_token(request):
    return request.data.get('refresh_token') or request.COOKIES.get('refresh_token')
