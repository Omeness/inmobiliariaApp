from decimal import Decimal

from django.core.validators import (MaxValueValidator, MinLengthValidator,
                                    MinValueValidator, RegexValidator)
from django.db import models

solo_codigo = RegexValidator(
    r'^[A-Za-z0-9\-]+$',
    'El código solo puede contener letras, números y guiones (sin espacios).',
)
solo_texto = RegexValidator(
    r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s\.\-']+$",
    'La comuna solo puede contener letras, espacios, puntos y guiones.',
)


class Propiedad(models.Model):
    class EstadoVenta(models.TextChoices):
        DISPONIBLE = 'DISPONIBLE', 'Disponible'
        RESERVADA = 'RESERVADA', 'Reservada'
        VENDIDA = 'VENDIDA', 'Vendida'
        INACTIVA = 'INACTIVA', 'Inactiva/Eliminada'

    class Moneda(models.TextChoices):
        UF = 'UF', 'UF'
        CLP = 'CLP', 'CLP'

    codigo_referencia = models.CharField(
        'Código de referencia', max_length=20, unique=True,
        validators=[MinLengthValidator(3, 'El código debe tener al menos 3 caracteres.'), solo_codigo],
        error_messages={'unique': 'Ya existe una propiedad con ese código de referencia.'},
    )
    titulo = models.CharField(
        'Título', max_length=150,
        validators=[MinLengthValidator(5, 'El título debe tener al menos 5 caracteres.')],
    )
    descripcion = models.TextField(
        'Descripción',
        validators=[MinLengthValidator(20, 'La descripción debe tener al menos 20 caracteres.')],
    )
    estado_venta = models.CharField(
        'Estado de venta', max_length=12,
        choices=EstadoVenta.choices, default=EstadoVenta.DISPONIBLE,
    )
    precio_venta = models.DecimalField(
        'Precio de venta', max_digits=14, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'), 'El precio debe ser mayor que cero.')],
    )
    moneda = models.CharField(max_length=3, choices=Moneda.choices, default=Moneda.UF)
    superficie_total = models.DecimalField(
        'Superficie total (m²)', max_digits=8, decimal_places=2,
        validators=[
            MinValueValidator(Decimal('0.01'), 'La superficie debe ser mayor que cero.'),
            MaxValueValidator(Decimal('100000'), 'La superficie no puede superar 100.000 m².'),
        ],
    )
    habitaciones = models.PositiveSmallIntegerField(
        default=1,
        validators=[MaxValueValidator(50, 'El máximo permitido es 50 habitaciones.')],
    )
    banos = models.PositiveSmallIntegerField(
        'Baños', default=1,
        validators=[MaxValueValidator(20, 'El máximo permitido es 20 baños.')],
    )
    comuna = models.CharField(
        max_length=80,
        validators=[MinLengthValidator(3, 'La comuna debe tener al menos 3 caracteres.'), solo_texto],
    )
    direccion = models.CharField(
        'Dirección', max_length=200,
        validators=[MinLengthValidator(5, 'La dirección debe tener al menos 5 caracteres.')],
    )
    fotografia_principal = models.ImageField(
        'Fotografía principal', upload_to='propiedades/', blank=True, null=True,
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name_plural = 'Propiedades'

    def __str__(self):
        return f'{self.codigo_referencia} - {self.titulo}'

    @property
    def esta_vendida(self):
        return self.estado_venta == self.EstadoVenta.VENDIDA

    def dar_de_baja(self):
        """Soft delete: no borra el registro, solo cambia el estado."""
        self.estado_venta = self.EstadoVenta.INACTIVA
        self.save(update_fields=['estado_venta', 'fecha_actualizacion'])