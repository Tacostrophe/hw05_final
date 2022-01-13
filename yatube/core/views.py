from django.shortcuts import render


def page_not_found(request, exception):
    template = 'core/404.html'
    title = 'Custom 404'
    context = {
        'path': request.path,
        'title': title,
    }
    return render(request, template, context, status=404)


def csrf_failure(request, reason=''):
    template = 'core/403csrf.html'
    title = 'Custom 403'
    context = {
        'title': title,
    }
    return render(request, template, context)


def forbidden_error(request, exception):
    template = 'core/403.html'
    title = 'Custom 403'
    context = {
        'title': title,
    }
    return render(request, template, context)


def server_error(request):
    template = 'core/500.html'
    title = 'Custom 500'
    context = {
        'path': request.path,
        'title': title,
    }
    return render(request, template, context, status=500)
