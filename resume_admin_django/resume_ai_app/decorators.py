# your_app/decorators.py
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from functools import wraps
from django.contrib.auth.decorators import login_required



def candidate_required(function):

    @wraps(function)
    @login_required  # Nécessite que l'utilisateur soit authentifié
    def wrap(request, *args, **kwargs):
        if hasattr(request.user, 'candidate_profile'):
            return function(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("Vous n'avez pas accès à cette page.")
    return wrap


def recruiter_required(function):
    """
    Decorator pour vérifier si l'utilisateur est un recruteur.
    """
    @wraps(function)
    @login_required
    def wrap(request, *args, **kwargs):
        if hasattr(request.user, 'recruiter_profile'):
            return function(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("Vous n'avez pas accès à cette page.")
    return wrap

def superuser_required(function):
    """
    Decorator pour vérifier si l'utilisateur est un superutilisateur.
    """
    @wraps(function)
    @login_required
    def wrap(request, *args, **kwargs):
        if request.user.is_superuser:
            return function(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("Vous n'avez pas accès à cette page.")
    return wrap

def recruiter_or_superuser_required(function):
    """
    Décorateur pour vérifier si l'utilisateur est un recruteur ou un superutilisateur.
    """
    @wraps(function)
    @login_required
    def wrap(request, *args, **kwargs):
        if hasattr(request.user, 'recruiter_profile') or request.user.is_superuser:
            return function(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("Vous n'avez pas accès à cette page.")
    return wrap
