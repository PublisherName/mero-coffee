from django_viewcomponent import component


@component.register("turnstile_input")
class TurnstileInput(component.Component):
    template_name = "components/turnstile_input/turnstile_input.html"

    def __init__(self, field=None, **kwargs):
        super().__init__(**kwargs)
        self.field = field
        self.errors = field.errors if field else None

    def get_context_data(self):
        return {
            "errors": self.errors,
            "field": self.field,
        }
