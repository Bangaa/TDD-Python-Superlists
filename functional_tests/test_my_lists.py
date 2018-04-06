#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Ian Mejias
#
# Distributed under terms of the GPL license.

from django.conf import settings
from django.contrib import auth
from django.contrib.sessions.backends.db import SessionStore
from .base import FunctionalTest

User = auth.get_user_model()

class MyListsTests(FunctionalTest):
    def create_pre_authenticated_session(self, email):
        user = User.objects.create(email=email)

        session = SessionStore()
        session[auth.SESSION_KEY] = user.pk
        session[auth.BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
        session.save()

        # para crear una cookie primero se debe visitar el dominio
        # Las pagínas no existentes (error 404) cargan más rápido

        self.browser.get(self.live_server_url + "/404_no_such_url")
        self.browser.add_cookie(dict(
            name=settings.SESSION_COOKIE_NAME,
            value=session.session_key,
            path='/'
        ))

    def test_logged_in_users_lists_are_saved_as_my_lists(self):
        email = 'edith@example.com'
        self.browser.get(self.live_server_url)
        self.wait_to_be_logged_out(email)

        # Edith is a logged-in user
        self.create_pre_authenticated_session(email)
        self.browser.get(self.live_server_url)
        self.wait_to_be_logged_in(email)
