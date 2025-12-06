from django.apps import AppConfig


class ComponentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "components"

    def ready(self):  # noqa: PLR6301
        import components.components.email_input  # noqa: F401
        import components.components.password_input  # noqa: F401
        import components.components.select_button  # noqa: F401
        import components.components.text_input  # noqa: F401
        import components.components.textarea_input  # noqa: F401
