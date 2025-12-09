from django_viewcomponent import component


@component.register("image_upload")
class ImageUpload(component.Component):
    template_name = "components/image_upload/image_upload.html"

    def __init__(
        self,
        field=None,
        name=None,
        label=None,
        required=False,
        help_text=None,
        container_class="",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.field = field
        self.name = name or (field.name if field else "")
        self.label = label or (field.label if field else "")
        self.required = required or (field.field.required if field else False)
        self.help_text = help_text or (field.help_text if field else "")
        self.container_class = container_class
        self.errors = field.errors if field else None

    def get_context_data(self):
        return {
            "name": self.name,
            "label": self.label,
            "required": self.required,
            "help_text": self.help_text,
            "errors": self.errors,
            "container_class": self.container_class,
            "field_id": f"id_{self.name}",
            "value": self.field.value() if self.field else "",
            "field": self.field,
            "attrs": self.field.field.widget.attrs if self.field else {},
        }
