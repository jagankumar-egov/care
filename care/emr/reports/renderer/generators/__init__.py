from care.emr.reports.renderer.generators import html_generator
from care.emr.reports.renderer.generators.registry import GeneratorRegistry

# Import weasyprint_generator separately to allow graceful failure
# if system libraries are not available
try:
    from care.emr.reports.renderer.generators import weasyprint_generator
except (ImportError, OSError):
    weasyprint_generator = None  # noqa: F841
