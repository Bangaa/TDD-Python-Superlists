# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Tests de los modelos de la app 'Lists'

from django.test import TestCase
from lists.models import Item, List
from django.core.exceptions import ValidationError

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
