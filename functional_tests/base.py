from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
import time
from datetime import datetime
import os

SCREEN_DUMP_LOCATION = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'screendumps'
)

def wait(max_wait):
    """Decorator. Wait for a helper to be executed succesfully for 'max_wait'
    seconds top. If the helper keep raissing a exception past the 10 seconds
    mark, said exception is raissed and the test should be considered failed.

    Args:
        fn: helper function to be waited for
        max_wait: wait at most this amount of time
    """
    def wait_for_success(fn):
        def mod_helper(*args, **kwargs):
            start_time = time.time()
            while True:
                try:
                    return fn(*args, **kwargs)
                except (AssertionError, WebDriverException) as e:
                    if time.time() - start_time > max_wait:
                        raise e
                    else:
                        time.sleep(0.2)
        return mod_helper
    return wait_for_success

class FunctionalTest(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        if self._test_has_failed():
            if not os.path.exists(SCREEN_DUMP_LOCATION):
                os.makedirs(SCREEN_DUMP_LOCATION)
            for ix, handle in enumerate(self.browser.window_handles):
                self._windowid = ix
                self.browser.switch_to_window(handle)
                self.take_screenshot()
                self.dump_html()
        self.browser.quit()
        super().tearDown()

    def _test_has_failed(self):
        return any(error for (method, error) in self._outcome.errors)

    def take_screenshot(self):
        filename = self._get_filename() + '.png'
        print('screenshotting to', filename)
        self.browser.get_screenshot_as_file(filename)

    def dump_html(self):
        filename = self._get_filename() + '.html'
        print('dumping page HTML to', filename)
        with open(filename, 'w') as f:
            f.write(self.browser.page_source)

    def _get_filename(self):
        timestamp = datetime.now().isoformat().replace(':', '.')[:19]
        return '{folder}/{classname}.{method}-window{windowid}-{timestamp}'.format(
            folder=SCREEN_DUMP_LOCATION,
            classname=self.__class__.__name__,
            method=self._testMethodName,
            windowid=self._windowid,
            timestamp=timestamp
        )

    @wait(10)
    def _assertRowInTable(self, row_text):
        """Comprueba que exista una fila determinada en la tabla que contiene
        la lista de elementos.

        Args:
            row_text: Es el texto de la fila que se busca
        """
        table = self.browser.find_element_by_id('id_list_table')
        rows = table.find_elements_by_tag_name("tr")
        self.assertIn(row_text, [row.text.split(maxsplit=1)[1] for row in rows])

    @wait(10)
    def _assertRowNotInTable(self, row_text):
        table = self.browser.find_element_by_id('id_list_table')
        rows = table.find_elements_by_tag_name("tr")
        self.assertNotIn(row_text, [row.text for row in rows])

    @wait(10)
    def wait_for(self, funct):
        """Espera que se ejecute una funcion exitosamente.

        Las funciones deben pasarse como funciones lambda si es que estas
        necesitan argumentos, de caso contrario solo se debe pasar el nombre
        de la funcion.

        Args:
            funct: Es la funcion que se ejecuta hasta tener exito
            max_wait: Es la cantidad maxima de tiempo, en segundos, que se
                espera antes que se lanze la Exception de la funcion (Default
                10).
        """
        return funct()

    @wait(10)
    def wait_to_be_logged_in(self, email):
        self.wait_for(
            lambda: self.browser.find_element_by_link_text('Log out')
        )
        navbar = self.browser.find_element_by_css_selector('.navbar')
        self.assertIn(email, navbar.text)

    @wait(10)
    def wait_to_be_logged_out(self, email):
        self.wait_for(
            lambda: self.browser.find_element_by_name('email')
        )
        navbar = self.browser.find_element_by_css_selector('.navbar')
        self.assertNotIn(email, navbar.text)


    def add_todo_element(self, todo_text):
        inputbox = self.get_item_input_box()
        inputbox.send_keys(todo_text)
        inputbox.send_keys(Keys.ENTER)

    @wait(10)
    def get_item_input_box(self):
        return self.browser.find_element_by_id('id_text')
