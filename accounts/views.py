from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.contrib import messages, auth

from accounts.models import Token

# POST /accounts/send_login_email
def send_login_email(request):
    email = request.POST['email']
    new_token = Token.objects.create(email=email)
    login_url = request.build_absolute_uri(
        reverse('login') + '?token=%s' % new_token.uid
    )

    ebody = 'Use this link to log in:\n\n%s' % login_url

    send_mail(
        'Your login link for Superlists',
        ebody,
        'noreply@superlists',
        [email]
    )
    messages.success(
        request,
        "Check your email, we've sent you a link you can use to log in."
    )

    return redirect('/')

# GET /accounts/login?token={uid}
def login(request):
    uid = request.GET.get('token')
    user = auth.authenticate(uid=uid)
    if user:
        auth.login(request, user)
    return redirect('/')
