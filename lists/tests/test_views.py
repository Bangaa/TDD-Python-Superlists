# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Tests de las vistas de la app 'List'

from unittest import skip
from django.test import TestCase
from lists.views import home_page   # Funcion que retorna la URL de home
from lists.models import Item, List
from lists.forms import ItemForm
from django.contrib.auth import get_user_model

User = get_user_model()

class HomePageTest(TestCase):

    def test_uses_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_home_page_uses_item_form(self):
        response = self.client.get('/')
        self.assertIsInstance(response.context['form'], ItemForm)

class ViewListTest(TestCase):

    def test_passes_correct_list_to_template(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()
        response = self.client.get('/lists/%d/' % correct_list.id)
        self.assertEqual(response.context['list'], correct_list)

    def test_display_only_items_for_that_list(self):
        listA = List.objects.create()
        Item.objects.create(text='TODO item 1, list A', list=listA)
        Item.objects.create(text='TODO item 2, list A', list=listA)

        listB = List.objects.create()
        Item.objects.create(text='TODO item 1, list B', list=listB)

        # Se  fracasa si se encuentran elementos de la lista B
        response = self.client.get('/lists/%d/' % listA.id)
        self.assertContains(response, 'list A')
        self.assertNotContains(response, 'list B')

        # Se  fracasa si se encuentran elementos de la lista A
        response = self.client.get('/lists/%d/' % listB.id)
        self.assertContains(response, 'list B')
        self.assertNotContains(response, 'list A')

    def test_uses_list_template(self):
        list_ = List.objects.create()
        response = self.client.get('/lists/%d/' % list_.id)
        self.assertTemplateUsed(response, 'list.html')

    def test_can_save_a_POST_request_to_existing_list(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        self.client.post(
            '/lists/%d/' % correct_list.id,
            data={'text': 'A new item for an existing list'}
        )

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new item for an existing list')
        self.assertEqual(new_item.list, correct_list)

    def test_POST_redirects_to_list_view(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.post(
            '/lists/%d/' % correct_list.id,
            data={'text': 'A new item for an existing list'}
        )

        self.assertRedirects(response, '/lists/%d/' % correct_list.id)

    def post_invalid_input(self):
        """
        Metodo de ayuda. Se hace un POST invalido: item sin texto, a la url
        'view_list'
        """
        list_ = List.objects.create()
        return self.client.post('/lists/%d/' % list_.id, data={'text': ''})

    def test_for_invalid_input_nothing_saved_to_db(self):
        self.post_invalid_input()
        self.assertEqual(Item.objects.count(), 0)

    def test_for_invalid_input_renders_list_template(self):
        response = self.post_invalid_input()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'list.html')

    def test_for_invalid_input_passes_form_to_template(self):
        response = self.post_invalid_input()
        self.assertIsInstance(response.context['form'], ItemForm)

    def test_for_invalid_input_shows_error_on_page(self):
        response = self.post_invalid_input()
        self.assertContains(response, ItemForm.Meta.error_messages['text']['required'])

    def test_displays_item_form(self):
        list_ = List.objects.create()
        response = self.client.get('/lists/%d/' % list_.id)
        self.assertIsInstance(response.context['form'], ItemForm)
        self.assertContains(response, 'name="text"')

    def test_duplicate_item_validation_errors_end_up_on_lists_page(self):
        list1 = List.objects.create()
        item1 = Item.objects.create(list=list1, text='textey')
        response = self.client.post(
            '/lists/%d/' % list1.id,
            data={'text': 'textey'}
        )

        expected_error = "Este item ya existe en tu lista"
        self.assertContains(response, expected_error)
        self.assertTemplateUsed(response, 'list.html')
        self.assertEqual(Item.objects.all().count(), 1)

class NewListTest(TestCase):

    def test_can_save_a_POST_request(self):
        self.client.post('/lists/new', data={'text': 'A new list item'})

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, "A new list item")

    def test_redirect_after_POST(self):
        response = self.client.post('/lists/new', data={'text': 'A new list item'})
        new_list = List.objects.first()
        self.assertRedirects(response, '/lists/%d/' % new_list.id)

    def test_for_invalid_input_reder_home_template(self):
        response = self.client.post('/lists/new', data={'text': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_validation_errors_are_shown_on_home_page(self):
        response = self.client.post('/lists/new', data={'text': ''})
        self.assertContains(response, ItemForm.Meta.error_messages['text']['required'])

    def test_for_invalid_input_passes_form_to_template(self):
        response = self.client.post('/lists/new', data={'text': ''})
        self.assertIsInstance(response.context['form'], ItemForm)

    def test_invalid_list_items_arent_saved(self):
        self.client.post('/lists/new', data={'text': ''})
        self.assertEqual(List.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)

    def test_empy_todo_elements_arent_saved(self):
        self.client.post('/lists/new', data={'text': ''})
        self.assertEqual(List.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)

    def test_list_owner_is_saved_if_user_is_authenticated(self):
        user = User.objects.create(email='a@b.com')
        self.client.force_login(user)
        self.client.post('/lists/new', data={'text': 'new item'})
        list_ = List.objects.first()
        self.assertEqual(list_.owner, user)

class MyListsTest(TestCase):
    def test_my_lists_url_renders_my_lists_template(self):
        User.objects.create(email='a@b.com')
        response = self.client.get('/lists/users/a@b.com/')
        self.assertTemplateUsed(response, 'my_lists.html')

    def test_passes_correct_owner_to_template(self):
        User.objects.create(email='wrong@owner.com')
        correct_owner = User.objects.create(email='right@owner.com')

        response = self.client.get('/lists/users/right@owner.com/')
        self.assertEqual(response.context['owner'], correct_owner)
