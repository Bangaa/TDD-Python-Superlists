# -*- coding: utf-8 -*-
# vim:fenc=utf-8

from django import forms
from lists.models import Item, List
from django.core.exceptions import ValidationError

class ItemForm(forms.models.ModelForm):

    class Meta:
        model = Item
        fields = ('text',)
        widgets = {
            'text': forms.fields.TextInput(attrs={
                'placeholder': "Enter a to-do item",
                'class': "form-control input-lg",
            }),
        }

        error_messages = {
            'text': {'required': "No puedes crear un item sin texto"},
            'NON_FIELD_ERRORS' : {
                'unique_together' : "Este item ya existe en tu lista"
            },
        }

    def __init__(self, *args, **kwargs):
        lista = kwargs.pop('for_list', None)
        super().__init__(*args, **kwargs)
        self.instance.list = lista

    def save_for_list(self, owner_list):
        self.instance.list = owner_list
        return super().save()

    def validate_unique(self):
        try:
            self.instance.validate_unique()
        except ValidationError as e:
            e.error_dict = {'text': self.Meta.error_messages['NON_FIELD_ERRORS'].values()}
            self._update_errors(e)

class NewListForm(ItemForm):
    def save(self, owner):
        if owner.is_authenticated:
            return List.create_new(first_item_text=self.cleaned_data['text'], owner=owner)
        else:
            return List.create_new(first_item_text=self.cleaned_data['text'])



class ExistingListItemForm(ItemForm):
    pass
