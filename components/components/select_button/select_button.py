from django_viewcomponent import component


@component.register("select_button")
class SelectButton(component.Component):
    """
    Reusable Select Button Component for Django forms.

    This component creates a beautifully styled select dropdown that matches
    the MeroCoffee design system with dark theme, gradients, and smooth animations.

    Usage in templates:
        {% load viewcomponent_tags %}
        {% component "select_button" field=form.field_name %}

        Or with custom options:
        {% component "select_button"
            field=form.field_name
            label="Custom Label"
            choices=custom_choices
            help_text="Optional help text"
            required=True
            error_class="custom-error-class"
        %}

    Parameters:
        field: Django form field (if using with forms)
        name: Name attribute for the select (required if not using field)
        label: Label text for the select
        choices: List of tuples [(value, display_text), ...]
        selected: The value that should be selected
        required: Boolean, whether field is required (default: False)
        disabled: Boolean, whether field is disabled (default: False)
        placeholder: Placeholder option text (default: "Select an option")
        help_text: Optional help text to display below the select
        error_class: Custom CSS class for error state (default: "border-red-500")
        select_class: Additional CSS classes for the select element
        container_class: Additional CSS classes for the container
    """

    template_name = "components/select_button/select_button.html"

    def __init__(
        self,
        field=None,
        name=None,
        label=None,
        choices=None,
        selected=None,
        required=False,
        disabled=False,
        placeholder="Select an option",
        help_text=None,
        error_class="border-red-500",
        select_class="",
        container_class="",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.field = field
        self.name = name or (field.name if field else "")
        self.label = label or (field.label if field else "")
        self.choices = choices or (field.field.choices if field else [])
        self.selected = selected or (field.value() if field and field.value() else "")
        self.required = required or (field.field.required if field else False)
        self.disabled = disabled
        self.placeholder = placeholder
        self.help_text = help_text or (field.help_text if field else "")
        self.error_class = error_class
        self.select_class = select_class
        self.container_class = container_class
        self.errors = field.errors if field else None

    def get_context_data(self):
        """Prepare context data for the template"""
        base_select_classes = (
            "w-full px-4 py-3 bg-slate-900/50 border border-slate-700 "
            "rounded-lg text-white placeholder-slate-500 focus:outline-none "
            "focus:border-red-500 focus:ring-2 focus:ring-red-500/50 "
            "transition-all duration-300 appearance-none cursor-pointer "
            "hover:border-slate-600 disabled:opacity-50 disabled:cursor-not-allowed"
        )

        # Add error styling if there are errors
        if self.errors:
            base_select_classes += f" {self.error_class} focus:border-red-500"

        # Add custom classes
        if self.select_class:
            base_select_classes += f" {self.select_class}"

        return {
            "name": self.name,
            "label": self.label,
            "choices": self.choices,
            "selected": self.selected,
            "required": self.required,
            "disabled": self.disabled,
            "placeholder": self.placeholder,
            "help_text": self.help_text,
            "errors": self.errors,
            "select_classes": base_select_classes,
            "container_class": self.container_class,
            "field_id": f"id_{self.name}",
        }
