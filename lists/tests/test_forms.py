# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#

from django.test import TestCase

from lists.models import *
from lists.forms import ItemForm


class ItemFormTest(TestCase):

    def test_form_renders_item_text_input(self):
        form = ItemForm()
        self.assertIn('placeholder="Enter a to-do item"', form.as_p())
        self.assertIn('class="form-control input-lg"', form.as_p())

    def test_form_validation_for_blank_items(self):
        form = ItemForm(data={'text': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(
                form.errors['text'],
                list(ItemForm.Meta.error_messages['text'].values())
        )

    def test_form_save_handles_saving_to_a_list(self):
        list_ = List.objects.create()
        form = ItemForm(data={'text': 'do me'})
        new_item = form.save_for_list(list_)
        self.assertEqual(new_item, Item.objects.first())
        self.assertEqual(new_item.text, 'do me')
        self.assertEqual(new_item.list, list_)

class ExistingListItemFormTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        emdict = ItemForm.Meta.error_messages
        cls.EMPTY_ITEM_ERROR =  emdict['text']['required']
        cls.DUPLICATE_ITEM_ERROR = emdict['NON_FIELD_ERRORS']['unique_together']

    def test_form_renders_item_text_input(self):
        list_ = List.objects.create()
        form = ItemForm(for_list=list_)
        self.assertIn('placeholder="Enter a to-do item"', form.as_p())

    def test_form_validation_for_blank_items(self):
        list_ = List.objects.create()
        form = ItemForm(for_list=list_, data={'text': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['text'], [self.EMPTY_ITEM_ERROR])

    def test_form_validation_for_duplicate_items(self):
        list_ = List.objects.create()
        Item.objects.create(list=list_, text='no twins!')
        form = ItemForm(for_list=list_, data={'text': 'no twins!'})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['text'], [self.DUPLICATE_ITEM_ERROR])
