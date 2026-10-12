from django.http import JsonResponse
from django.views.csrf import csrf_failure as default_csrf_failure

def csrf_failure(request, reason=''):
    if request.path.startswith('/api/'):
        return JsonResponse({'error': 'Your session security token has expired. Refresh the page and try again.'}, status=403)
    return default_csrf_failure(request, reason=reason)
