from base.models import Auth
from base.tests import BaseTestCase
from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.utils import timezone
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException


from selenium import webdriver
from selenium.webdriver.common.by import By
from voting.models import Question, Voting, QuestionOption


class VisualizerTestCase(StaticLiveServerTestCase):
    def create_votings(self):

        q = Question(desc='test question', types='OQ')
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option="Opcion {}".format(i + 1))
            opt.save()
        v_open = Voting(name="test voting", question=q, start_date=timezone.now())
        v_open.save()

        v_closed = Voting(
            name="test voting closed", question=q, start_date=timezone.now()
        )
        v_closed.save()

        v_not_started = Voting(name="test voting not started", question=q)
        v_not_started.save()

        a, _ = Auth.objects.get_or_create(
            url=settings.BASEURL, defaults={"me": True, "name": "test auth"}
        )
        a.save()
        v_open.auths.add(a)
        v_closed.auths.add(a)
        v_not_started.auths.add(a)

        v_closed.end_date = timezone.now()
        v_closed.save()

        return v_open, v_closed, v_not_started

    def setUp(self):
        self.v_open, self.v_closed, self.v_not_started = self.create_votings()

        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = False
        self.driver = webdriver.Chrome(options=options)
        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()
        self.base.tearDown()

    def test_votacion_cerrada(self):

        self.driver.get(f"{self.live_server_url}/visualizer/{self.v_closed.id}")

        WebDriverWait(self.driver, 10).until(EC.title_contains("Decide"))

        self.assertIn("Decide", self.driver.title)
        self.assertIn("Results:", self.driver.page_source)

        bar_chart = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "barChart"))
        )
        pie_chart = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "pieChart"))
        )

        self.assertTrue(bar_chart.is_displayed())
        self.assertTrue(pie_chart.is_displayed())

    
    def test_votacion_abierta(self):

        self.driver.get(f"{self.live_server_url}/visualizer/{self.v_open.id}")

        self.assertTrue(len(self.driver.find_elements(By.ID, "app-visualizer")) == 1)

    def test_votacion_no_empezada(self):

        self.driver.get(f"{self.live_server_url}/visualizer/{self.v_not_started.id}")

        self.assertTrue(self.driver.find_element(By.ID, "app-visualizer").is_displayed())

        with self.assertRaises(NoSuchElementException):
            self.driver.find_element(By.ID, "barChart")

        with self.assertRaises(NoSuchElementException):
            self.driver.find_element(By.ID, "pieChart")