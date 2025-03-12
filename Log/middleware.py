from threading import local

_user = local()

# 获取当前登录用户
class CurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _user.value = request.user  # 保存当前请求的用户
        response = self.get_response(request)

        del _user.value
        return response

# 获取当前用户的方法
def get_current_user():
    return getattr(_user, 'value', None)