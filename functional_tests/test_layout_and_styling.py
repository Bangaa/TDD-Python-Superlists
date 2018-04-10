# -*- coding: utf-8 -*-
# vim:fenc=utf-8

from django.test import tag
from .base import FunctionalTest

@tag('functional-test')
class LayoutAndStylingTest(FunctionalTest):

    def test_layout_and_styling(self): # Edith goes to the home page
        self.browser.get(self.live_server_url)
        self.browser.set_window_size(1024, 768)

        # She notices the input box is nicely centered
        inputbox = self.get_item_input_box()
        self.assertAlmostEqual(inputbox.location['x'] + inputbox.size['width'] / 2, 512, delta=10)

        # She starts a new list and sees the input is nicely centered there too
        self.add_todo_element('testing')
        self._assertRowInTable('testing')
        inputbox = self.get_item_input_box()
        self.assertAlmostEqual(inputbox.location['x'] + inputbox.size['width'] / 2, 512, delta=10)

