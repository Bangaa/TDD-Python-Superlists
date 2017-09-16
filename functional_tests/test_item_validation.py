# -*- coding: utf-8 -*-
# vim:fenc=utf-8

from unittest import skip
from .base import FunctionalTest

class ItemValidationTest(FunctionalTest):

    def test_cannot_add_empty_list_items(self):
        # Edith goes to the home page and accidentally tries to submit
        # an empty list item. She hits Enter on the empty input box
        self.browser.get(self.live_server_url)
        self.add_todo_element("")

        # The home page refreshes, and there is an error message saying
        # that list items cannot be blank
        self.wait_for(lambda: self.assertEqual(
            self.browser.find_element_by_css_selector('.has-error').text,
            ItemForm.Meta.error_messages['text']['required']
            )
        )

        # She tries again with some text for the item, which now works
        self.add_todo_element("Comprar pan")
        self._assertRowInTable("Comprar pan")

        # Perversely, she now decides to submit a second blank list item
        self.add_todo_element("")

        # She receives a similar warning on the list page
        self.wait_for(lambda: self.assertEqual(
            self.browser.find_element_by_css_selector('.has-error').text,
            ItemForm.Meta.error_messages['text']['required']
            )
        )

        # And she can correct it by filling some text in
        self.add_todo_element("Hacerme un sandwich")
        self._assertRowInTable("Comprar pan")
        self._assertRowInTable("Hacerme un sandwich")
