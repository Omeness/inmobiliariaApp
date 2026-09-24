from decimal import Decimal

from django import forms

from .models import Propiedad

MAX_FOTO_MB = 5
UF_MAX = Decimal('500000')      # ajustable
CLP_MIN = Decimal('1000000')    # ajustable


class PropiedadBaseForm(forms.ModelForm):
    """Reglas comunes a crear y editar."""

    class Meta:
        model = Propiedad
        exclude = ['fecha_creacion', 'fecha_actualizacion']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
            'fotografia_principal': forms.FileInput(attrs={'accept': 'image/*'}),
            'precio_venta': forms.NumberInput(attrs={'min': '0.01', 'step': '0.01'}),
            'superficie_total': forms.NumberInput(attrs={'min': '0.01', 'step': '0.01'}),
            'habitaciones': forms.NumberInput(attrs={'min': '0', 'max': '50'}),
            'banos': forms.NumberInput(attrs={'min': '0', 'max': '20'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                css = 'form-check-input'
            elif isinstance(field.widget, forms.Select):
                css = 'form-select'
            else:
                css = 'form-control'
            field.widget.attrs.setdefault('class', css)

    # --- Normalización / validación campo a campo ---
    def clean_codigo_referencia(self):
        return self.cleaned_data['codigo_referencia'].strip().upper()

    def clean_comuna(self):
        return self.cleaned_data['comuna'].strip().title()

    def clean_fotografia_principal(self):
        foto = self.cleaned_data.get('fotografia_principal')
        # Solo un archivo recién subido tiene .size y .content_type
        if foto and hasattr(foto, 'content_type'):
            if foto.size > MAX_FOTO_MB * 1024 * 1024:
                raise forms.ValidationError(f'La imagen no puede pesar más de {MAX_FOTO_MB} MB.')
        return foto

    # --- Validación entre campos ---
    def clean(self):
        datos = super().clean()
        precio, moneda = datos.get('precio_venta'), datos.get('moneda')
        if precio is not None and moneda == Propiedad.Moneda.UF and precio > UF_MAX:
            self.add_error('precio_venta', f'El precio en UF no puede superar {UF_MAX:,.0f} UF.')
        if precio is not None and moneda == Propiedad.Moneda.CLP and precio < CLP_MIN:
            self.add_error('precio_venta', f'El precio en CLP debe ser al menos ${CLP_MIN:,.0f}.')
        return datos


class PropiedadCrearForm(PropiedadBaseForm):
    """Al crear, una propiedad solo puede nacer Disponible o Reservada."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        E = Propiedad.EstadoVenta
        self.fields['estado_venta'].choices = [
            (E.DISPONIBLE.value, E.DISPONIBLE.label),
            (E.RESERVADA.value, E.RESERVADA.label),
        ]


class PropiedadEditarForm(PropiedadBaseForm):
    """
    Al editar: el código queda bloqueado y se puede eliminar la fotografía
    (borra solo la imagen, el registro de la propiedad se conserva).
    """
    eliminar_fotografia = forms.BooleanField(
        required=False, label='Eliminar la fotografía actual',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['codigo_referencia'].disabled = True
        # Nombre de la foto que tenía antes de esta edición
        self._foto_previa = self.instance.fotografia_principal.name or None
        if not self._foto_previa:
            del self.fields['eliminar_fotografia']   # nada que eliminar

    def clean(self):
        datos = super().clean()
        subio_nueva = 'fotografia_principal' in self.changed_data and datos.get('fotografia_principal')
        if datos.get('eliminar_fotografia') and subio_nueva:
            self.add_error('eliminar_fotografia',
                           'No puedes subir una fotografía nueva y eliminar la actual a la vez.')
        return datos

    def save(self, commit=True):
        eliminar = self.cleaned_data.get('eliminar_fotografia')
        reemplazada = ('fotografia_principal' in self.changed_data
                       and self.cleaned_data.get('fotografia_principal'))
        if eliminar and self._foto_previa:
            # Borra el archivo del disco y deja el campo en NULL
            self.instance.fotografia_principal.delete(save=False)
        propiedad = super().save(commit=commit)
        if commit and reemplazada and self._foto_previa \
                and self._foto_previa != propiedad.fotografia_principal.name:
            # Se subió una foto nueva: limpia el archivo anterior para no dejar huérfanos
            propiedad.fotografia_principal.storage.delete(self._foto_previa)
        return propiedad


class FiltroPropiedadForm(forms.Form):
    fecha_desde = forms.DateField(required=False, label='Creada desde',
                                  widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    fecha_hasta = forms.DateField(required=False, label='Creada hasta',
                                  widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    precio_min = forms.DecimalField(required=False, min_value=0, label='Precio mín.',
                                    widget=forms.NumberInput(attrs={'class': 'form-control'}))
    precio_max = forms.DecimalField(required=False, min_value=0, label='Precio máx.',
                                    widget=forms.NumberInput(attrs={'class': 'form-control'}))
    estado = forms.ChoiceField(required=False, label='Estado',
                               choices=[('', 'Todos (excepto inactivas)')] + Propiedad.EstadoVenta.choices,
                               widget=forms.Select(attrs={'class': 'form-select'}))

    def clean(self):
        d = super().clean()
        if d.get('precio_min') is not None and d.get('precio_max') is not None \
                and d['precio_min'] > d['precio_max']:
            raise forms.ValidationError('El precio mínimo no puede ser mayor que el máximo.')
        if d.get('fecha_desde') and d.get('fecha_hasta') and d['fecha_desde'] > d['fecha_hasta']:
            raise forms.ValidationError('La fecha "desde" no puede ser posterior a "hasta".')
        return d


class BuscarPorIdForm(forms.Form):
    propiedad_id = forms.IntegerField(
        min_value=1, label='ID de la propiedad',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 12'}),
    )