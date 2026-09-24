from django import forms
from .models import Propiedad


class PropiedadForm(forms.ModelForm):
    class Meta:
        model = Propiedad
        exclude = ['fecha_creacion', 'fecha_actualizacion']
        widgets = {'descripcion': forms.Textarea(attrs={'rows': 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            css = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
            field.widget.attrs.setdefault('class', css)


class FiltroPropiedadForm(forms.Form):
    fecha_desde = forms.DateField(required=False, label='Creada desde',
                                  widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    fecha_hasta = forms.DateField(required=False, label='Creada hasta',
                                  widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    precio_min = forms.DecimalField(required=False, label='Precio mín.',
                                    widget=forms.NumberInput(attrs={'class': 'form-control'}))
    precio_max = forms.DecimalField(required=False, label='Precio máx.',
                                    widget=forms.NumberInput(attrs={'class': 'form-control'}))
    estado = forms.ChoiceField(required=False, label='Estado',
                               choices=[('', 'Todos (excepto inactivas)')] + Propiedad.EstadoVenta.choices,
                               widget=forms.Select(attrs={'class': 'form-select'}))


class BuscarPorIdForm(forms.Form):
    propiedad_id = forms.IntegerField(
        min_value=1, label='ID de la propiedad',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 12'}),
    )