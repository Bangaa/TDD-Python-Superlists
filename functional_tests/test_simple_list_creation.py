# -*- coding: utf-8 -*-
# vim:fenc=utf-8

from django.test import tag
from .base import FunctionalTest
from selenium import webdriver

@tag('functional-test')
class NewVisitorTest(FunctionalTest):

    def test_can_start_a_list_for_one_user(self):
        # Juanito has heard about a cool new online to-do app. He goes
        # to check out its homepage
        self.browser.get(self.live_server_url)

        # He notices the page title and header mention to-do lists
        self.assertIn('To-Do', self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn("To-Do", header_text)

        # He is invited to enter a to-do item straight away
        # He types "Buy peacock feathers" into a text box (Juanito's hobby
        # is tying fly-fishing lures)

        # When he hits enter, the page updates, and now the page lists
        # "1: Buy peacock feathers" as an item in a to-do list
        self.add_todo_element("Buy peacock feathers")
        self._assertRowInTable("Buy peacock feathers")

        # There is still a text box inviting him to add another item. He
        # enters "Use peacock feathers to make a fly" (Juanito is very methodical)
        self.add_todo_element("Use peacock feathers to make a fly")

        # The page updates again, and now shows both items on his list

        self._assertRowInTable("Buy peacock feathers")
        self._assertRowInTable('Use peacock feathers to make a fly')

        # Satisfied, he goes back to sleep

    def test_multiple_users_can_start_lists_at_different_urls(self):
        # Edith start a new to-do list
        self.browser.get(self.live_server_url)
        self.add_todo_element('Buy peacock feathers')
        self._assertRowInTable('Buy peacock feathers')

        # She notices that her list has a unique URL
        edith_list_url = self.browser.current_url
        self.assertRegex(edith_list_url, '/lists/.+')

        # Now a new user, Francis, comes along to the site.

        ## We use a new browser session to make sure that no information
        ## of Edith's is coming through from cookies etc
        self.browser.quit()
        self.browser = webdriver.Firefox()

        # Francis visits the home page.  There is no sign of Edith's list
        self.browser.get(self.live_server_url)

        # Francis starts a new list by entering a new item. He
        # is less interesting than Edith...
        self.add_todo_element('Buy milk')
        self._assertRowInTable('Buy milk')

        # Francis gets his own unique URL
        francis_list_url = self.browser.current_url
        self.assertRegex(francis_list_url, '/lists/.+')
        self.assertNotEqual(francis_list_url, edith_list_url)

        # Again, there is no trace of Edith's list
        self._assertRowNotInTable('1: Buy peacock feathers')
        self._assertRowInTable('Buy milk')

        # Satisfied, they both go back to sleep

