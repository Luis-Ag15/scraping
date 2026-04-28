import csv
import time
import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.db import transaction
from django.db.models import Count

from .models import SearchConfig, JobResult
from .forms import SearchForm
from .scraper import JobScraper

logger = logging.getLogger(__name__)


def index(request):
    """Página principal con formulario de búsqueda e historial."""
    form = SearchForm()
    recent_searches = SearchConfig.objects.all()[:20]

    return render(request, 'core/index.html', {
        'form': form,
        'recent_searches': recent_searches,
    })


def run_search(request):
    """Ejecuta el scraping y guarda resultados en BD."""
    if request.method != 'POST':
        return redirect('core:index')

    form = SearchForm(request.POST)
    if not form.is_valid():
        recent_searches = SearchConfig.objects.all()[:20]
        return render(request, 'core/index.html', {
            'form': form,
            'recent_searches': recent_searches,
        })

    # Crear registro de búsqueda
    search_config = SearchConfig.objects.create(
        search_terms=form.cleaned_data['search_terms'],
        locations=form.cleaned_data['locations'],
        sites=','.join(form.cleaned_data['sites']),
        country=form.cleaned_data['country'],
        results_wanted=form.cleaned_data['results_wanted'],
        hours_old=form.cleaned_data['hours_old'],
        is_remote=form.cleaned_data['is_remote'],
        status='running',
    )

    # Ejecutar scraping
    start_time = time.time()
    scraper = JobScraper()

    try:
        jobs, errors = scraper.scrape(
            search_terms=search_config.get_search_terms_list(),
            sites=search_config.get_sites_list(),
            results_wanted=search_config.results_wanted,
            hours_old=search_config.hours_old,
            country=search_config.country,
            locations=search_config.get_locations_list(),
            is_remote=search_config.is_remote,
        )

        with transaction.atomic():
            job_objects = [JobResult(search=search_config, **job_data) for job_data in jobs]
            # Evita reventar la request si entran duplicados (también cubierto por constraint)
            JobResult.objects.bulk_create(job_objects, ignore_conflicts=True)

            elapsed = time.time() - start_time
            search_config.total_jobs_found = search_config.jobs.count()
            search_config.duration_seconds = round(elapsed, 2)
            search_config.status = 'completed'

            if errors:
                search_config.error_message = '\n'.join(errors)

            search_config.save()

        messages.success(
            request,
            f'✅ Búsqueda completada: {search_config.total_jobs_found} empleos guardados en {elapsed:.1f}s'
        )

    except Exception as e:
        elapsed = time.time() - start_time
        search_config.status = 'failed'
        search_config.error_message = str(e)
        search_config.duration_seconds = round(elapsed, 2)
        search_config.save()

        logger.exception("Error durante el scraping")
        messages.error(request, f'❌ Error durante la búsqueda: {str(e)}')

    return redirect('core:search_detail', pk=search_config.pk)


def search_detail(request, pk):
    """Muestra los resultados de una búsqueda."""
    search = get_object_or_404(SearchConfig, pk=pk)
    jobs = search.jobs.all()

    stats_qs = jobs.aggregate(
        total=Count('id'),
        companies=Count('company', distinct=True),
        locations=Count('location', distinct=True),
    )
    sites_used = list(jobs.values_list('site', flat=True).distinct().order_by('site'))

    return render(request, 'core/search_detail.html', {
        'search': search,
        'jobs': jobs,
        'stats': {
            'total': stats_qs['total'] or 0,
            'companies': stats_qs['companies'] or 0,
            'locations': stats_qs['locations'] or 0,
            'sites': sites_used,
        },
    })


def export_csv(request, pk):
    """Exporta resultados de una búsqueda como CSV."""
    search = get_object_or_404(SearchConfig, pk=pk)
    jobs = search.jobs.all()

    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename="empleos_busqueda_{pk}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Sitio', 'Título', 'Empresa', 'Ubicación', 'URL',
        'Fecha publicación', 'Salario mín', 'Salario máx',
        'Moneda', 'Intervalo', 'Tipo de empleo', 'Zona de búsqueda',
    ])

    for job in jobs:
        writer.writerow([
            job.site, job.title, job.company, job.location, job.job_url,
            job.date_posted, job.min_amount, job.max_amount,
            job.currency, job.interval, job.job_type, job.search_location,
        ])

    return response


def delete_search(request, pk):
    """Elimina una búsqueda y sus resultados."""
    search = get_object_or_404(SearchConfig, pk=pk)
    if request.method == 'POST':
        search.delete()
        messages.success(request, '🗑️ Búsqueda eliminada correctamente.')
    return redirect('core:index')
