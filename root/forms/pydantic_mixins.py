from pydantic import ValidationError as PydanticValidationError


class PydanticValidationMixin:
    """
    Mixin to handle Pydantic schema validation in Django forms.

    Subclasses should define a `pydantic_schema` class attribute.
    Call `self.validate_with_pydantic()` in the `clean()` method.
    For custom data transformation, pass the data dict to `validate_with_pydantic(data)`.
    """

    pydantic_schema = None

    def validate_with_pydantic(self, data=None):
        """
        Validate the provided data against the Pydantic schema.

        Args:
            data (dict, optional): Data to validate. Defaults to self.cleaned_data.
        """
        if data is None:
            data = self.cleaned_data
        if self.pydantic_schema:
            try:
                self.pydantic_schema(**data)
            except PydanticValidationError as e:
                for error in e.errors():
                    field_name = error["loc"][0] if error["loc"] else None
                    msg = error["msg"].replace("Value error, ", "").replace("  ", " ")
                    if field_name and field_name in self.fields:
                        self.add_error(field_name, msg)
                    else:
                        self.add_error(None, msg)
