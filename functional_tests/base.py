from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
import time

class FunctionalTest(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.refresh()
        self.browser.quit()

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
                self.assertIn(row_text, [row.text.split(maxsplit=1)[1] for row in rows])
                return None
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

