import time
from django.http import HttpResponseForbidden, JsonResponse
from functools import wraps
from django.core.cache import cache
from django.shortcuts import redirect
# from Users.models import Instructor, Student, Profile

# Timer Decorator
def check_load_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Function {func.__name__} took {end_time - start_time:.2f} seconds.")
        return result
    return wrapper

# Require Super user Decorator
def require_superuser(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseForbidden("Only superusers allowed.")
        return func(request, *args, **kwargs)
    return wrapper

# Blocks all POST methods
def block_post_method(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if request.method == "POST":
            return JsonResponse({"error": "POST not allowed"}, status=405)
        return func(request, *args, **kwargs)
    return wrapper

# Blocks all GET methods
def block_get_method(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if request.method == "GET":
            return JsonResponse({"error": "GET not allowed"}, status=405)
        return func(request, *args, **kwargs)
    return wrapper

# Caches request for faster response
def memoize_request(timeout=60):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            key = f"{request.get_full_path()}"
            cached = cache.get(key)
            if cached:
                return cached
            response = func(request, *args, **kwargs)
            cache.set(key, response, timeout)
            return response
        return wrapper
    return decorator

# Logs Api request
def log_api_request(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        print(f"[{request.method}] {request.path} by {request.user}")
        return func(request, *args, **kwargs)
    return wrapper

# Retries the function on failure
def retry_on_failure(retries=3, delay=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Retry {i+1}/{retries} failed: {e}")
                    time.sleep(delay)
            raise Exception("All retries failed.")
        return wrapper
    return decorator


# def only_instructor(request):
#     @wraps(func)
#     def wrapper(request, *args, **kwargs):
#         if request.user.is_authenticated:
#             profile = Profile.objects.filter(user=request.user)
#             if profile:
#                 if Instructor.objects.filter(profile=profile).exists():
#                     return func(request, *args, **kwargs)
#                 elif request.user.is_authenticated:
#                     return redirect('home') # Assuming 'home' is the URL name for your home page
#                 else:
#                     return redirect('login') # Assuming 'login' is the URL name for your login page
#         return wrapper

# def only_student(request):
#     @wraps(func)
#     def wrapper(request, *args, **kwargs):
#         if request.user.is_authenticated:
#             if Student.objects.filter(user=request.user).exists():
#                 return func(request, *args, **kwargs)
#             elif request.user.is_authenticated:
#                 return redirect('home') # Assuming 'home' is the URL name for your home page
#             else:
#                 return redirect('login') # Assuming 'login' is the URL name for your login page
#         return wrapper