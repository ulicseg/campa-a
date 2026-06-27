from django.test import TestCase


class SmokeTest(TestCase):
    def test_settings_have_apps(self):
        from django.conf import settings
        for app in ["usuarios", "territorio", "encuestas", "dashboard"]:
            self.assertIn(app, settings.INSTALLED_APPS)
