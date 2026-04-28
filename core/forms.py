from django import forms


SITE_CHOICES = [
    ('linkedin', 'LinkedIn'),
]

COUNTRY_CHOICES = [
    ('mexico', 'México'),
    ('usa', 'Estados Unidos'),
    ('argentina', 'Argentina'),
    ('colombia', 'Colombia'),
    ('spain', 'España'),
    ('chile', 'Chile'),
    ('peru', 'Perú'),
]


class SearchForm(forms.Form):
    """Formulario para configurar una búsqueda de empleos."""

    search_terms = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Base de datos\nExcel\nPython',
            'id': 'id_search_terms',
        }),
        label="Términos de búsqueda",
        help_text="Ingresa un término por línea",
    )

    locations = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Ciudad de México\nMonterrey\nGuadalajara',
            'id': 'id_locations',
        }),
        label="Ubicaciones",
        help_text="Ingresa una ubicación por línea",
    )

    sites = forms.MultipleChoiceField(
        choices=SITE_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'id': 'id_sites'}),
        label="Sitios de búsqueda",
        initial=['linkedin'],
    )

    country = forms.ChoiceField(
        choices=COUNTRY_CHOICES,
        label="País",
        initial='mexico',
        widget=forms.Select(attrs={'id': 'id_country'}),
    )

    results_wanted = forms.IntegerField(
        min_value=10,
        max_value=500,
        initial=50,
        label="Resultados por búsqueda",
        widget=forms.NumberInput(attrs={
            'id': 'id_results_wanted',
        }),
    )

    hours_old = forms.IntegerField(
        min_value=1,
        max_value=720,
        initial=72,
        label="Antigüedad máxima (horas)",
        widget=forms.NumberInput(attrs={
            'id': 'id_hours_old',
        }),
    )

    is_remote = forms.BooleanField(
        required=False,
        initial=False,
        label="Solo trabajos remotos",
        widget=forms.CheckboxInput(attrs={
            'id': 'id_is_remote',
        }),
    )
