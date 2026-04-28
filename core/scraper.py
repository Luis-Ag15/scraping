import pandas as pd
import time
import logging

from jobspy import scrape_jobs

logger = logging.getLogger(__name__)


class JobScraper:
    """Encapsula la lógica de scraping de empleos con manejo de errores y deduplicación."""

    def scrape(self, search_terms, sites, results_wanted, hours_old, country, locations, is_remote=False):
        """
        Ejecuta el scraping para múltiples términos y ubicaciones.

        Returns:
            tuple: (list[dict], list[str]) — resultados y errores
        """
        all_jobs = []
        errors = []
        seen_ids = set()

        for location in locations:
            for search_term in search_terms:
                try:
                    jobs_df = scrape_jobs(
                        site_name=sites,
                        search_term=search_term,
                        results_wanted=results_wanted,
                        hours_old=hours_old,
                        country_indeed=country,
                        location=location,
                        is_remote=is_remote,
                    )

                    if jobs_df is not None and not jobs_df.empty:
                        count = 0
                        for _, row in jobs_df.iterrows():
                            job_id = str(row.get('id', ''))
                            if job_id and job_id not in seen_ids:
                                seen_ids.add(job_id)
                                all_jobs.append(self._row_to_dict(row, location))
                                count += 1

                        logger.info(
                            f"'{search_term}' en {location}: {count} resultados nuevos "
                            f"({len(jobs_df)} encontrados, {len(jobs_df) - count} duplicados)"
                        )
                    else:
                        logger.warning(f"Sin resultados para '{search_term}' en {location}")

                except Exception as e:
                    error_msg = f"Error scraping '{search_term}' en {location}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)

        return all_jobs, errors

    def _row_to_dict(self, row, search_location):
        """Convierte una fila del DataFrame a dict para guardar en BD."""
        return {
            'job_id': str(row.get('id', '')),
            'site': str(row.get('site', '')),
            'title': str(row.get('title', '')),
            'company': str(row.get('company', '')),
            'location': str(row.get('location', '')),
            'job_url': str(row.get('job_url', '')),
            'description': str(row.get('description', ''))[:5000],
            'date_posted': str(row.get('date_posted', '')),
            'min_amount': str(row.get('min_amount', '') or ''),
            'max_amount': str(row.get('max_amount', '') or ''),
            'currency': str(row.get('currency', '') or ''),
            'interval': str(row.get('interval', '') or ''),
            'job_type': str(row.get('job_type', '') or ''),
            'search_location': search_location,
        }
