import sys
from unittest import TestLoader

from django.conf import settings
from django.test.runner import DiscoverRunner


class CustomTestLoader(TestLoader):
    def __init__(self):
        super().__init__()
        apps_dir = settings.BASE_DIR / "apps"
        apps_dir_str = str(apps_dir)
        if apps_dir_str not in sys.path:
            sys.path.insert(0, apps_dir_str)

    def loadTestsFromName(self, name, module=None):
        name = name.removeprefix("apps.")
        return super().loadTestsFromName(name, module)


class CustomTestRunner(DiscoverRunner):
    test_loader = CustomTestLoader()
