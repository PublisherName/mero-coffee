from django_viewcomponent import component


@component.register("textarea_input")
class TextareaInput(component.Component):
    template_name = "components/textarea_input/textarea_input.html"

    def __init__(
        self,
        field=None,
        name=None,
        label=None,
        required=False,
        placeholder="",
        help_text=None,
        input_class="",
        container_class="",
        rows=4,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.field = field
        self.name = name or (field.name if field else "")
        self.label = label or (field.label if field else "")
        self.required = required or (field.field.required if field else False)
        self.placeholder = placeholder or (
            field.field.widget.attrs.get("placeholder", "") if field else ""
        )
        self.help_text = help_text or (field.help_text if field else "")
        self.input_class = input_class
        self.container_class = container_class
        self.rows = rows
        self.errors = field.errors if field else None

    def get_context_data(self):
        base_input_classes = (
            "w-full px-4 py-3 bg-page/50 border "
            "rounded-lg text-white placeholder-subtle focus:outline-none "
            "focus:ring-2 transition-all duration-300 resize-none"
        )

        if self.errors:
            base_input_classes += " border-accent focus:border-accent focus:ring-accent/50"
        else:
            base_input_classes += (
                " border-surface focus:border-surface-muted focus:ring-surface/50"
            )

        if self.input_class:
            base_input_classes += f" {self.input_class}"

        return {
            "name": self.name,
            "label": self.label,
            "required": self.required,
            "placeholder": self.placeholder,
            "help_text": self.help_text,
            "errors": self.errors,
            "input_classes": base_input_classes,
            "container_class": self.container_class,
            "field_id": self.field.field.widget.attrs.get("id") or f"id_{self.name}"
            if self.field
            else f"id_{self.name}",
            "rows": self.rows,
            "value": self.field.value() if self.field else "",
            "attrs": self.field.field.widget.attrs if self.field else {},
        }
