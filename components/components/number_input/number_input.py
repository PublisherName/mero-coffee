from django_viewcomponent import component


@component.register("number_input")
class NumberInput(component.Component):
    template_name = "components/number_input/number_input.html"

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
        prefix=None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.field = field
        self.name = name or (field.name if field else "")
        self.label = label or (field.label if field else "")
        self.required = required or (field.field.required if field else False)
        self.widget_attrs = self.field.field.widget.attrs if self.field else {}
        self.field_id = self.widget_attrs.get("id") or f"id_{self.name}"
        self.placeholder = placeholder or self.widget_attrs.get("placeholder", "")
        self.prefix = prefix

        self.help_text = help_text or (field.help_text if field else "")
        self.input_class = input_class
        self.container_class = container_class
        self.errors = field.errors if field else None

    def get_context_data(self):
        base_input_classes = (
            "w-full px-4 py-3 bg-slate-900/50 border "
            "rounded-lg text-white placeholder-slate-500 focus:outline-none "
            "focus:ring-2 transition-all duration-300"
        )

        if self.prefix:
            base_input_classes += " has-prefix"

        if self.errors:
            base_input_classes += " border-red-500 focus:border-red-500 focus:ring-red-500/50"
        else:
            base_input_classes += (
                " border-slate-700 focus:border-slate-600 focus:ring-slate-500/30"
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
            "field_id": self.field_id,
            "prefix": self.prefix,
            "value": self.field.value() if self.field else "",
            "attrs": self.widget_attrs,
        }
