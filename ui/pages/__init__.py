"""页面包。"""

from .favorites_page import FavoritesPage
from .prompt_detail_page import PromptDetailPage
from .prompt_list_page import PromptListPage
from .search_page import SearchPage

__all__ = [
    "PromptListPage",
    "PromptDetailPage",
    "SearchPage",
    "FavoritesPage",
]
