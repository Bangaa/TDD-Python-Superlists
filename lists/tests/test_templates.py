# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Tests de las vistas de la app 'List'

from django.test import TestCase
from lists.views import home_page   # Funcion que retorna la URL de home
from lists.models import Item, List

class HomePageTest(TestCase):

    def test_uses_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

class ViewListTest(TestCase):

    def test_display_only_items_for_that_list(self):
        listA = List.objects.create()
        Item.objects.create(text='TODO item 1, list A', list=listA)
        Item.objects.create(text='TODO item 2, list A', list=listA)

        listB = List.objects.create()
        Item.objects.create(text='TODO item 1, list B', list=listB)

        # Se  fracasa si se encuentran elementos de la lista B
        response = self.client.get(f'/lists/{listA.id}/')
        self.assertContains(response, 'list A')
        self.assertNotContains(response, 'list B')

        # Se  fracasa si se encuentran elementos de la lista A
        response = self.client.get(f'/lists/{listB.id}/')
        self.assertContains(response, 'list B')
        self.assertNotContains(response, 'list A')

    def test_uses_list_template(self):
        list_ = List.objects.create()
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertTemplateUsed(response, 'list.html')

class NewListTest(TestCase):

    def test_can_save_a_POST_request(self):
        self.client.post('/lists/new', data={'item_text': 'A new list item'})

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, "A new list item")

    def test_redirect_after_POST(self):
        response = self.client.post('/lists/new', data={'item_text': 'A new list item'})
        new_list = List.objects.first()
        self.assertRedirects(response, f'/lists/{new_list.id}/')

    def test_can_save_a_POST_request_to_existing_list(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        self.client.post(
            f'/lists/{correct_list.id}/add_item',
            data={'item_text': 'A new item for an existing list'}
        )

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new item for an existing list')
        self.assertEqual(new_item.list, correct_list)

    def test_redirects_to_list_view(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.post(
            f'/lists/{correct_list.id}/add_item',
            data={'item_text': 'A new item for an existing list'}
        )

        self.assertRedirects(response, f'/lists/{correct_list.id}/')

    def test_passes_correct_list_to_template(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()
        response = self.client.get(f'/lists/{correct_list.id}/')
        self.assertEqual(response.context['list'], correct_list)

