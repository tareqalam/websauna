"""Cross-site request forgery test views."""
from pyramid.response import Response
from pyramid.view import view_config

from websauna.system.core.csrf import csrf_exempt


@view_config(route_name="home")
def home(request):
    """We need one GET request to initialize session and set CSRF token."""
    return Response("OK")


@view_config(route_name="csrf_sample")
def csrf_sample(request):
    assert request.method == "POST"
    return Response("OK")


@view_config(route_name="csrf_exempt_sample")
@csrf_exempt
def csrf_exempt_sample(request):
    assert request.method == "POST"
    return Response("OK")


@view_config(route_name="csrf_exempt_sample_context")
@csrf_exempt
def csrf_exempt_sample_context(context, request):
    assert request.method == "POST"
    return Response("OK")