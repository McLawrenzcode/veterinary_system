from .authentication import AuthenticationModule
from .appointments import AppointmentsModule
from .inventory import InventoryModule
from .points_of_sale import PointOfSaleModule
from .reports import ReportsModule
from .communications import CommunicationsModule
from .settings import SettingsModule

__all__ = [
    'AuthenticationModule',
    'AppointmentsModule',
    'InventoryModule',
    'PointOfSaleModule',
    'ReportsModule',
    'CommunicationsModule',
    'SettingsModule'
]