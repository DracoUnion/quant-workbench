"""页面包。"""

from .dashboard import DashboardPage
from .favorites_page import FavoritesPage
from .prompt_detail_page import PromptDetailPage
from .prompt_list_page import PromptListPage
from .search_page import SearchPage
from .workflows import WorkflowsPage
from .runs import RunsPage
from .knowledge import KnowledgePage
from .research import ResearchPage
from .portfolio import PortfolioPage
from .signals import SignalsPage
from .events import EventsPage
from .clients import ClientsPage
from .compliance import CompliancePage
from .office import OfficePage
from .settings import SettingsPage

__all__ = [
    "DashboardPage",
    "FavoritesPage",
    "PromptDetailPage",
    "PromptListPage",
    "SearchPage",
    "WorkflowsPage",
    "RunsPage",
    "KnowledgePage",
    "ResearchPage",
    "PortfolioPage",
    "SignalsPage",
    "EventsPage",
    "ClientsPage",
    "CompliancePage",
    "OfficePage",
    "SettingsPage",
]
