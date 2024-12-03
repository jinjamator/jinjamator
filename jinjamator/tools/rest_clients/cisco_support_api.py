import logging
log=logging.getLogger()

try:
    from simple_cisco_support_api import CiscoSupportAPIClient
except ImportError:
    log.error("CiscoSupportAPIClient has been removed from jinjamator. Please install via pip install simple_cisco_support_api")
    