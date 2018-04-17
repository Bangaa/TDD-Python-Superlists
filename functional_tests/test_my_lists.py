#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Ian Mejias
#
# Distributed under terms of the GPL license.

from django.test import tag
from django.conf import settings
from django.contrib import auth
from django.contrib.sessions.backends.db import SessionStore
from .base import FunctionalTest

User = auth.get_user_model()

@tag('functional-test')
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
        # Edith is a logged-in user
        self.create_pre_authenticated_session('edith@example.com')

        # She goes to the home page and starts a list
        self.browser.get(self.live_server_url)
        self.add_todo_element('Reticulate splines')
        self._assertRowInTable('Reticulate splines')
        self.add_todo_element('Immanentize eschaton')
        self._assertRowInTable('Immanentize eschaton')
        first_list_url = self.browser.current_url

        # She notices a new sidenav with the title "My lists", for the first
        # time.
        sidenav = self.browser.find_element_by_css_selector('ul.nav-pills.nav-stacked')

        # She sees that her list is in there, named according to its
        # first list item
        self.wait_for(
            lambda: sidenav.find_element_by_link_text('Reticulate splines')
        )
        sidenav.find_element_by_link_text('Reticulate splines').click()
        self.wait_for(
            lambda: self.assertEqual(self.browser.current_url, first_list_url,
                "El link hacia la primera lista no funciona")
        )

        # She decides to start another list, just to see
        self.browser.get(self.live_server_url)
        self.add_todo_element('Click cows')
        self._assertRowInTable('Click cows')
        second_list_url = self.browser.current_url

        # In the sidenav, her new list appears
        sidenav = self.browser.find_element_by_css_selector('ul.nav-pills.nav-stacked')
        self.wait_for(
            lambda: sidenav.find_element_by_link_text('Click cows')
        )

        # From her second list page she go to her first list page
        self.assertEqual(self.browser.current_url, second_list_url)
        self.browser.find_element_by_link_text('Reticulate splines').click()
        self.wait_for(
            lambda: self.assertEqual(self.browser.current_url, first_list_url)
        )

        # She logs out.  The sidenav disappears
        self.browser.find_element_by_link_text('Log out').click()
        self.wait_for(lambda: self.assertEqual(
            self.browser.find_elements_by_link_text('My lists'),
            []
        ))

    def test_correct_list_in_sidenav_is_highlighted(self):
        # Juanito es un usuario registrado
        self.create_pre_authenticated_session('juanito@email.com')

        # Juanito se dirige a la pagina principal y empieza una lista

        self.browser.get(self.live_server_url)
        self.add_todo_element('Sopa')
        self._assertRowInTable('Sopa')

        # se da cuenta que en el sidenav se encuentra su lista 'Sopa'
        # seleccionada

        sidenav = self.browser.find_element_by_css_selector('ul.nav-pills.nav-stacked')
        selected = sidenav.find_element_by_css_selector('li.active>a')

        self.assertEqual(selected.text, 'Sopa')

        # empieza otra lista y ahora su nueva lista se encuentra seleccionada
        # y la antigua no.

        self.browser.get(self.live_server_url)
        self.add_todo_element('Vino')
        self._assertRowInTable('Vino')

        sidenav = self.browser.find_element_by_css_selector('ul.nav-pills.nav-stacked')
        selected = sidenav.find_elements_by_css_selector('li.active>a')

        self.assertEqual(len(selected), 1, 'El sidenav tiene más de 1 elemento seleccionado')
        self.assertEqual(selected[0].text, 'Vino')
