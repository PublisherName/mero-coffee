from django.contrib.messages import get_messages
from django.test import TestCase


class BaseNewsletterTestCase(TestCase):
    """Base class for newsletter tests with common assertions."""

    def assert_message(self, response, substring, level=None):
        """Assert response contains message matching substring (case-insensitive)."""
        messages = list(get_messages(response.wsgi_request))
        matching = [msg for msg in messages if substring.lower() in str(msg).lower()]
        self.assertTrue(
            matching, f"No message found containing '{substring}' in {len(messages)} messages"
        )

        if level:
            self.assertEqual(matching[0].level_tag, level)
