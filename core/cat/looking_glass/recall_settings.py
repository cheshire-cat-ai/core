"""Module for retrieving default configurations for episodic, declarative and procedural memories"""

from typing import Any
from cat.utils import BaseModelDict


class RecallSettingsMetadata(BaseModelDict):
    """Settigs's metadata for default configurations

    Variables:
        source (str): the source of the recall query
    """

    source: str


class RecallSettings(BaseModelDict):
    """Class for retrieving default configurations for episodic, declarative and procedural memories

    Variables:
        embedding (Any): the embedding of the recall query - default None
        k (int): the number of memories to return - default 3
        threshold (float): the threshold - default 0.5
        metadata (RecallSettingsMetadata): metadata - default None
    """

    embedding: Any
    k: int = 3
    threshold: float = 0.5
    metadata: RecallSettingsMetadata = None
