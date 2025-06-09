from django.db import models
from django.core.validators import MinValueValidator
import uuid


class Client(models.Model):
    """Modelo para almacenar datos de clientes"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name="Nombre del Cliente")
    ruc = models.CharField(max_length=20, verbose_name="RUC")
    phone = models.CharField(max_length=15, verbose_name="Teléfono")
    address = models.TextField(verbose_name="Dirección")
    email = models.EmailField(verbose_name="Correo Electrónico")
    contact_person = models.CharField(max_length=200, verbose_name="Persona de Contacto")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Parameter(models.Model):
    """Catálogo de parámetros disponibles por categoría"""
    CATEGORY_CHOICES = [
        ('water', 'Monitoreo de Agua'),
        ('gas', 'Emisiones Gaseosas'),
        ('noise', 'Monitoreo de Ruido'),
        ('logistics', 'Logística'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name="Nombre del Parámetro")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="Categoría")
    default_unit = models.CharField(max_length=50, verbose_name="Unidad por Defecto")
    default_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Base")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Parámetro"
        verbose_name_plural = "Parámetros"
        unique_together = ['name', 'category']

    def __str__(self):
        return f"{self.name} - {self.get_category_display()}"


class Method(models.Model):
    """Métodos/Referencias disponibles para análisis"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name="Nombre del Método")
    description = models.TextField(blank=True, verbose_name="Descripción")
    category = models.CharField(max_length=20, choices=Parameter.CATEGORY_CHOICES, verbose_name="Categoría")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Método"
        verbose_name_plural = "Métodos"

    def __str__(self):
        return self.name


class Technique(models.Model):
    """Técnicas disponibles para análisis"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name="Nombre de la Técnica")
    description = models.TextField(blank=True, verbose_name="Descripción")
    category = models.CharField(max_length=20, choices=Parameter.CATEGORY_CHOICES, verbose_name="Categoría")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Técnica"
        verbose_name_plural = "Técnicas"

    def __str__(self):
        return self.name


class Proforma(models.Model):
    """Modelo principal para proformas"""
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('sent', 'Enviada'),
        ('approved', 'Aprobada'),
        ('rejected', 'Rechazada'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Cliente")
    proforma_number = models.CharField(max_length=20, unique=True, verbose_name="Número de Proforma")
    date = models.DateField(verbose_name="Fecha")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Estado")
    
    # Totales calculados
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Subtotal")
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="IVA")
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Total")
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, verbose_name="Creado por")

    class Meta:
        verbose_name = "Proforma"
        verbose_name_plural = "Proformas"
        ordering = ['-created_at']

    def __str__(self):
        return f"Proforma {self.proforma_number} - {self.client.name}"

    def calculate_totals(self):
        """Calcula los totales de la proforma"""
        self.subtotal = sum([analysis.subtotal for analysis in self.analysis_set.all()])
        self.tax_amount = self.subtotal * 0.12  # IVA 12%
        self.total = self.subtotal + self.tax_amount
        self.save()


class Analysis(models.Model):
    """Análisis individual dentro de una proforma"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proforma = models.ForeignKey(Proforma, on_delete=models.CASCADE, verbose_name="Proforma")
    
    # Datos del análisis
    parameter = models.ForeignKey(Parameter, on_delete=models.CASCADE, verbose_name="Parámetro")
    unit = models.CharField(max_length=50, verbose_name="Unidad")
    method = models.ForeignKey(Method, on_delete=models.CASCADE, verbose_name="Método/Referencia")
    technique = models.ForeignKey(Technique, on_delete=models.CASCADE, verbose_name="Técnica")
    
    # Precios y cantidades
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Precio Unitario")
    quantity = models.IntegerField(validators=[MinValueValidator(1)], default=1, verbose_name="Cantidad")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, editable=False, verbose_name="Subtotal")
    
    # Orden para mostrar
    order = models.PositiveIntegerField(default=0, verbose_name="Orden")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")

    class Meta:
        verbose_name = "Análisis"
        verbose_name_plural = "Análisis"
        ordering = ['order', 'created_at']

    def save(self, *args, **kwargs):
        """Calcula el subtotal antes de guardar"""
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)
        # Recalcular totales de la proforma
        self.proforma.calculate_totals()

    def __str__(self):
        return f"{self.parameter.name} - {self.proforma.proforma_number}"


# Modelo para configuración de empresa
class CompanySettings(models.Model):
    """Configuración de la empresa para las proformas"""
    company_name = models.CharField(max_length=200, verbose_name="Nombre de la Empresa")
    company_address = models.TextField(verbose_name="Dirección")
    company_phone = models.CharField(max_length=20, verbose_name="Teléfono")
    company_email = models.EmailField(verbose_name="Email")
    company_ruc = models.CharField(max_length=20, verbose_name="RUC")
    company_logo = models.ImageField(upload_to='logos/', blank=True, null=True, verbose_name="Logo")
    
    # Configuración de numeración
    proforma_prefix = models.CharField(max_length=10, default="PRF", verbose_name="Prefijo Proformas")
    next_proforma_number = models.IntegerField(default=1, verbose_name="Siguiente # de Proforma")
    
    tax_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0.12, verbose_name="Tasa de IVA")

    class Meta:
        verbose_name = "Configuración de Empresa"
        verbose_name_plural = "Configuración de Empresa"

    def __str__(self):
        return self.company_name

    def get_next_proforma_number(self):
        """Genera el siguiente número de proforma"""
        current_number = self.next_proforma_number
        self.next_proforma_number += 1
        self.save()
        return f"{self.proforma_prefix}-{current_number:04d}"