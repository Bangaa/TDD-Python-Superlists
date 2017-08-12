from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
import time

class NewVisitorTest(LiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_can_start_a_list_and_retrieve_it_later(self):
        # Juanito has heard about a cool new online to-do app. He goes
        # to check out its homepage
        self.browser.get(self.live_server_url)

        # He notices the page title and header mention to-do lists
        self.assertIn('To-Do', self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn("To-Do", header_text)

        # He is invited to enter a to-do item straight away
        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertEqual(
            inputbox.get_attribute('placeholder'),
            'Enter a to-do item'
        )

        # He types "Buy peacock feathers" into a text box (Juanito's hobby
        # is tying fly-fishing lures)

        # When he hits enter, the page updates, and now the page lists
        # "1: Buy peacock feathers" as an item in a to-do list
        self.add_todo_element("Buy peacock feathers")
        self._assertRowInTable("1: Buy peacock feathers")

        # There is still a text box inviting him to add another item. He
        # enters "Use peacock feathers to make a fly" (Juanito is very methodical)
        self.add_todo_element("Use peacock feathers to make a fly")

        # The page updates again, and now shows both items on his list

        self._assertRowInTable("1: Buy peacock feathers")
        self._assertRowInTable('2: Use peacock feathers to make a fly')

        # Juanito wonders whether the site will remember his list. Then he sees
        # that the site has generated a unique URL for him -- there is some
        # explanatory text to that effect.
        self.fail('Finish the test!')

        # He visits that URL - his to-do list is still there.

        # Satisfied, he goes back to sleep

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

if __name__ == '__main__':
    unittest.main(warnings='ignore')
