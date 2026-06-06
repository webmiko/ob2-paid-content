"""Bootstrap 5: единые CSS-классы для полей Django-форм."""

from django import forms


class StyleFormMixin:
    """Проставляет классы Bootstrap 5 полям формы после super().__init__."""

    fields: dict[str, forms.Field]

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(field, forms.BooleanField):
                widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs.setdefault("class", "form-select")
            else:
                widget.attrs.setdefault("class", "form-control")
