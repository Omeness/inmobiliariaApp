from django.db import models


class Propiedad(models.Model):
    class EstadoVenta(models.TextChoices):
        DISPONIBLE = 'DISPONIBLE', 'Disponible'
        RESERVADA = 'RESERVADA', 'Reservada'
        VENDIDA = 'VENDIDA', 'Vendida'
        INACTIVA = 'INACTIVA', 'Inactiva/Eliminada'

    class Moneda(models.TextChoices):
        UF = 'UF', 'UF'
        CLP = 'CLP', 'CLP'

    codigo_referencia = models.CharField(max_length=20, unique=True)
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField()
    estado_venta = models.CharField(
        max_length=12, choices=EstadoVenta.choices, default=EstadoVenta.DISPONIBLE
    )
    precio_venta = models.DecimalField(max_digits=14, decimal_places=2)
    moneda = models.CharField(max_length=3, choices=Moneda.choices, default=Moneda.UF)
    superficie_total = models.DecimalField('Superficie total (m²)', max_digits=8, decimal_places=2)
    habitaciones = models.PositiveSmallIntegerField(default=1)
    banos = models.PositiveSmallIntegerField('Baños', default=1)
    comuna = models.CharField(max_length=80)
    direccion = models.CharField(max_length=200)
    fotografia_principal = models.ImageField(upload_to='propiedades/', blank=True, null=True)
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