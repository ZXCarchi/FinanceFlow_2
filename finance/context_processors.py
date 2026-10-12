def finance_globals(request):
    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)
        return {'app_currency': profile.currency if profile else 'PLN'}
    return {'app_currency': 'PLN'}
