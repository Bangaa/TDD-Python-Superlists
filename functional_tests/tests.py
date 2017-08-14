from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
import time

class NewVisitorTest(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.refresh()
        self.browser.quit()

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
        self._assertRowInTable("1: Buy peacock feathers", 5)

        # There is still a text box inviting him to add another item. He
        # enters "Use peacock feathers to make a fly" (Juanito is very methodical)
        self.add_todo_element("Use peacock feathers to make a fly")

        # The page updates again, and now shows both items on his list

        self._assertRowInTable("1: Buy peacock feathers", 10)
        self._assertRowInTable('2: Use peacock feathers to make a fly', 10)

        # Satisfied, he goes back to sleep

    def test_multiple_users_can_start_lists_at_different_urls(self):
        # Edith start a new to-do list
        self.browser.get(self.live_server_url)
        self.add_todo_element('Buy peacock feathers')
        self._assertRowInTable('1: Buy peacock feathers')

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
        self._assertRowInTable('1: Buy milk')

        # Francis gets his own unique URL
        francis_list_url = self.browser.current_url
        self.assertRegex(francis_list_url, '/lists/.+')
        self.assertNotEqual(francis_list_url, edith_list_url)

        # Again, there is no trace of Edith's list
        self._assertRowNotInTable('1: Buy peacock feathers', 1)
        self._assertRowInTable('1: Buy milk')

        # Satisfied, they both go back to sleep

    ##
    # Comprueba que exista una fila determinada en la tabla que contiene la
    # lista de elementos.
    # @param row_text Es el texto de la fila que se busca
    # @param max_wait Es el tiempo maximo que se espera, en segundos, antes que
    # la busqueda se determine como un fracaso
    def _assertRowInTable(self, row_text, max_wait=5):
        start_time = time.time()

        while True:
            try:
                table = self.browser.find_element_by_id('id_list_table')
                rows = table.find_elements_by_tag_name("tr")
                self.assertIn(row_text, [row.text for row in rows])
                break
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > max_wait:
                    raise e
                else:
                    time.sleep(0.1)

    def _assertRowNotInTable(self, row_text, max_wait=5):
        start_time = time.time()

        while time.time() - start_time < max_wait:
            try:
                table = self.browser.find_element_by_id('id_list_table')
                rows = table.find_elements_by_tag_name("tr")
                self.assertNotIn(row_text, [row.text for row in rows])

            except  WebDriverException as e:
                if time.time() - start_time > max_wait:
                    raise e
                else:
                    time.sleep(0.1)

    def add_todo_element(self, todo_text):
        inputbox = self.browser.find_element_by_id('id_new_item')
        inputbox.send_keys(todo_text)
        inputbox.send_keys(Keys.ENTER)

    def test_layout_and_styling(self):
        # Edith goes to the home page
        self.browser.get(self.live_server_url)
        self.browser.set_window_size(1024, 768)

        # She notices the input box is nicely centered
        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertAlmostEqual(
            inputbox.location['x'] + inputbox.size['width'] / 2, 512,
            delta=10
        )

        # She starts a new list and sees the input is nicely centered there too
        self.add_todo_element('testing')
        self._assertRowInTable('1: testing')
        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertAlmostEqual(
            inputbox.location['x'] + inputbox.size['width'] / 2,
            512,
            delta=10
        )

if __name__ == '__main__':
    unittest.main(warnings='ignore')
