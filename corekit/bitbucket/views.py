from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from . import signals


@csrf_exempt
@require_http_methods(["POST"])
def hook(request, app_key):
    '''
    curl -X POST -H "Content-Type: application/json" -d '{"repository": {"name": "coolsite", "owner": {"name": "hoge"}  }}' http://localhost/bitbucket/hook
    '''
    payload, user, repo = get_payload(request)

    if not user and not repo:
        return JsonResponse({'success': False, 'message': 'No JSON data or URL argument : cannot identify hook'})

    signals.bitbucket_webhook.send(sender=request, app_key=app_key, payload=payload, user=user, repo=repo)

    return JsonResponse({'success': True})


def get_payload(request):
    if request.META.get('CONTENT_TYPE') == "application/json":
        payload = json.loads(request.body.decode('utf8'))
    else:
        # Probably application/x-www-form-urlencoded
        payload = json.loads(request.POST.get("payload", "{}"))

    repo_data = payload.get('repository', {})
    user = repo_data.get('owner', {})
    repo = repo_data.get('name', None)

    if isinstance(user, dict):
        user = user.get('name', user.get('username', None))

    return payload, user, repo