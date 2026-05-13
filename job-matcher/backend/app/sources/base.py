"""Base class for job source connectors."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class JobSourceConnector(ABC):
    """Base class for all job source connectors."""

    source_name: str = "unknown"

    @abstractmethod
    async def fetch_jobs(self, keywords: List[str] = None, location: str = None) -> List[Dict[str, Any]]:
        """Fetch job postings from the source."""
        pass
