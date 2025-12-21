from django.conf import settings
from django.core.files.storage import FileSystemStorage


class PrivateMediaStorage(FileSystemStorage):
    def __init__(self, *args, **kwargs):
        kwargs["location"] = settings.PRIVATE_MEDIA_ROOT
        kwargs["base_url"] = settings.PRIVATE_MEDIA_URL
        super().__init__(*args, **kwargs)

    def get_accessed_time(self, name):
        return self.get_modified_time(name)
