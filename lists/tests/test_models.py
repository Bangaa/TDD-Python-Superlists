# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Tests de los modelos de la app 'Lists'

from django.test import TestCase
from lists.models import Item, List
from django.core.exceptions import ValidationError

from django.contrib.auth import get_user_model
User = get_user_model()

class ItemModelTest(TestCase):

    def test_default_text(self):
        item = Item()
        self.assertEqual(item.text, '')

    def test_item_is_related_to_list(self):
        list_ = List.objects.create()

        item = Item()
        item.list = list_
        item.save()

        self.assertIn(item, list_.item_set.all())

    def test_cannot_save_empty_list_items(self):
        list_ = List.objects.create()
        item = Item(list=list_, text="")

        with self.assertRaises(ValidationError):
            item.save()
            item.full_clean()

    def test_duplicate_items_are_invalid(self):
        list_ = List.objects.create()
        Item.objects.create(text='bla', list=list_)

        with self.assertRaises(ValidationError):
            item = Item(text='bla', list=list_)
            item.full_clean()

    def test_CAN_save_items_to_different_lists(self):
        list1 = List.objects.create()
        list2 = List.objects.create()

        Item.objects.create(text='bla', list=list1)
        otro_item = Item(text='bla', list=list2)

        otro_item.full_clean()  # should not raise

class ListModelTest(TestCase):
    """Tests del modelo <List>"""
    def test_get_absolute_url(self):
        list_ = List.objects.create()

        self.assertEqual(list_.get_absolute_url(),
                '/lists/%d/' % list_.id)

    def test_create_new_method_creates_list_and_first_item(self):
        list_ = List.create_new(first_item_text='new item')
        saved_list = List.objects.first()
        self.assertEqual(saved_list, list_)

        first_item = Item.objects.first()
        self.assertEqual(first_item.text, 'new item')

    def test_create_new_optionally_saves_owner(self):
        user = User.objects.create()
        List.create_new(first_item_text='new item text', owner=user)
        new_list = List.objects.first()
        self.assertEqual(new_list.owner, user)

    def test_create_new_returns_new_list_object(self):
        list_ = List.create_new(first_item_text='new item')
        saved_list = List.objects.first()

        self.assertEqual(list_, saved_list)

    def test_lists_can_have_owners(self):
        List(owner=User())  # should not raise

    def test_list_owner_is_optional(self):
        List().full_clean()  # should not raise

    def test_list_name_is_first_item_text(self):
        list_ = List.objects.create()
        Item.objects.create(list=list_, text='first item')
        Item.objects.create(list=list_, text='second item')
        self.assertEqual(list_.name, 'first item')
