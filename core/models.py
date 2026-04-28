from django.db import models
from django.utils import timezone


class SearchConfig(models.Model):
    """Almacena una configuración de búsqueda ejecutada por el usuario."""

    SITE_CHOICES = [
        ('linkedin', 'LinkedIn'),
    ]

    search_terms = models.TextField(
        verbose_name="Términos de búsqueda",
        help_text="Uno por línea"
    )
    locations = models.TextField(
        verbose_name="Ubicaciones",
        help_text="Una por línea"
    )
    sites = models.TextField(
        verbose_name="Sitios",
        default="linkedin",
        help_text="linkedin"
    )
    country = models.CharField(
        max_length=50,
        default="mexico",
        verbose_name="País"
    )
    results_wanted = models.PositiveIntegerField(
        default=50,
        verbose_name="Resultados por búsqueda"
    )
    hours_old = models.PositiveIntegerField(
        default=72,
        verbose_name="Antigüedad máxima (horas)"
    )
    is_remote = models.BooleanField(
        default=False,
        verbose_name="Solo remoto"
    )
    total_jobs_found = models.PositiveIntegerField(
        default=0,
        verbose_name="Total empleos encontrados"
    )
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Fecha de ejecución")
    duration_seconds = models.FloatField(default=0, verbose_name="Duración (segundos)")
    status = models.CharField(
        max_length=20,
        choices=[
            ('running', 'En ejecución'),
            ('completed', 'Completada'),
            ('failed', 'Fallida'),
        ],
        default='running',
        verbose_name="Estado"
    )
    error_message = models.TextField(blank=True, default='', verbose_name="Mensaje de error")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Búsqueda"
        verbose_name_plural = "Búsquedas"

    def __str__(self):
        terms = self.search_terms.replace('\n', ', ')[:50]
        return f"[{self.get_status_display()}] {terms} — {self.created_at.strftime('%d/%m/%Y %H:%M')}"

    def get_search_terms_list(self):
        return [t.strip() for t in self.search_terms.strip().splitlines() if t.strip()]

    def get_locations_list(self):
        return [l.strip() for l in self.locations.strip().splitlines() if l.strip()]

    def get_sites_list(self):
        return [s.strip() for s in self.sites.strip().split(',') if s.strip()]


class JobResult(models.Model):
    """Almacena cada oferta de trabajo encontrada."""

    search = models.ForeignKey(
        SearchConfig,
        on_delete=models.CASCADE,
        related_name='jobs',
        verbose_name="Búsqueda"
    )
    job_id = models.CharField(max_length=255, verbose_name="ID del empleo")
    site = models.CharField(max_length=50, blank=True, default='', verbose_name="Sitio")
    title = models.CharField(max_length=500, blank=True, default='', verbose_name="Título")
    company = models.CharField(max_length=300, blank=True, default='', verbose_name="Empresa")
    location = models.CharField(max_length=300, blank=True, default='', verbose_name="Ubicación")
    job_url = models.URLField(max_length=1000, blank=True, default='', verbose_name="URL")
    description = models.TextField(blank=True, default='', verbose_name="Descripción")
    date_posted = models.CharField(max_length=100, blank=True, default='', verbose_name="Fecha publicación")
    min_amount = models.CharField(max_length=50, blank=True, default='', verbose_name="Salario mínimo")
    max_amount = models.CharField(max_length=50, blank=True, default='', verbose_name="Salario máximo")
    currency = models.CharField(max_length=10, blank=True, default='', verbose_name="Moneda")
    interval = models.CharField(max_length=50, blank=True, default='', verbose_name="Intervalo salarial")
    job_type = models.CharField(max_length=100, blank=True, default='', verbose_name="Tipo de empleo")
    search_location = models.CharField(max_length=200, blank=True, default='', verbose_name="Ubicación de búsqueda")

    class Meta:
        ordering = ['-id']
        verbose_name = "Oferta de empleo"
        verbose_name_plural = "Ofertas de empleo"
        constraints = [
            models.UniqueConstraint(
                fields=['search', 'site', 'job_id'],
                name='uniq_job_per_search_site_id',
            ),
        ]
        indexes = [
            models.Index(fields=['search', 'site'], name='job_search_site_idx'),
            models.Index(fields=['company'], name='job_company_idx'),
            models.Index(fields=['location'], name='job_location_idx'),
        ]

    def __str__(self):
        return f"{self.title} — {self.company}"

    def get_salary_display(self):
        if self.min_amount and self.max_amount:
            return f"${self.min_amount} - ${self.max_amount} {self.currency}/{self.interval}"
        elif self.min_amount:
            return f"${self.min_amount} {self.currency}/{self.interval}"
        elif self.max_amount:
            return f"${self.max_amount} {self.currency}/{self.interval}"
        return "No especificado"
