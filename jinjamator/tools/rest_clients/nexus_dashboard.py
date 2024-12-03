import logging
log=logging.getLogger()

try:
    from simple_nexus_dashboard import NexusDashboardClient
except ImportError:
    log.error("NexusDashboardClient has been removed from jinjamator. Please install via pip install simple_nexus_dashboard")
    