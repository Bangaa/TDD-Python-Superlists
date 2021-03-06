# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Tests de las vistas de la app 'List'

import unittest
from django.test import TestCase
from lists.models import Item, List
from lists.forms import ItemForm
from django.contrib.auth import get_user_model

from django.http import HttpRequest
from lists.views import new_list

User = get_user_model()
EMPTY_ITEM_ERROR = ItemForm.Meta.error_messages['text']['required']

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
        self.assertContains(response, EMPTY_ITEM_ERROR)

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

class NewListViewIntegratedTest(TestCase):
    def test_can_save_a_POST_request(self):
        self.client.post('/lists/new', data={'text': 'A new list item'})
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new list item')

    def test_for_invalid_input_doesnt_save_but_shows_errors(self):
        response = self.client.post('/lists/new', data={'text': ''})
        self.assertEqual(List.objects.count(), 0)
        self.assertContains(response, EMPTY_ITEM_ERROR)

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

@unittest.mock.patch('lists.views.NewListForm')
class NewListViewUnitTest(unittest.TestCase):
    def setUp(self):
        self.request = HttpRequest()
        self.request.POST['text'] = 'new list item'
        self.request.user = unittest.mock.Mock()

    def test_passes_POST_data_to_NewListForm(self, NewListForm_m):
        new_list(self.request)
        NewListForm_m.assert_called_once_with(data=self.request.POST)

    def test_saves_form_with_owner_if_form_valid(self, NewListForm_m):
        mock_form = NewListForm_m.return_value
        mock_form.is_valid.return_value = True
        new_list(self.request)
        mock_form.save.assert_called_once_with(owner=self.request.user)

    @unittest.mock.patch('lists.views.redirect')
    def test_redirects_to_form_returned_object_if_form_valid(
        self, redirect_m, NewListForm_m
    ):
        mock_form = NewListForm_m.return_value
        mock_form.is_valid.return_value = True

        response = new_list(self.request)

        self.assertEqual(response, redirect_m.return_value)
        redirect_m.assert_called_once_with(mock_form.save.return_value)

    @unittest.mock.patch('lists.views.render')
    def test_renders_home_template_with_form_if_form_invalid(
        self, render_m, NewListForm_m
    ):
        mock_form = NewListForm_m.return_value
        mock_form.is_valid.return_value = False

        response = new_list(self.request)

        self.assertEqual(response, render_m.return_value)
        render_m.assert_called_once_with(
            self.request, 'home.html', {'form': mock_form}
        )

    def test_does_not_save_if_form_invalid(self, NewListForm_m):
        mock_form = NewListForm_m.return_value
        mock_form.is_valid.return_value = False
        new_list(self.request)
        self.assertFalse(mock_form.save.called, "Form saved even if invalid")
