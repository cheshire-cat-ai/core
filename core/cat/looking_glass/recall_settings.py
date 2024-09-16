"""Module for retrieving default configurations for episodic, declarative and procedural memories"""


class RecallSettings:
    """Class for retrieving default configurations for episodic, declarative and procedural memories"""

    DEFAULT_K = 3
    DEFAULT_TRESHOLD = 0.5

    def _build_settings(
        self,
        recall_query_embedding,
        user_id=None,
        k=DEFAULT_K,
        treshold=DEFAULT_TRESHOLD,
    ):
        return {
            "embedding": recall_query_embedding,
            "k": k,
            "threshold": treshold,
            "metadata": {"source": user_id} if user_id else None,
        }

    def default_episodic_config(self, recall_query_embedding, user_id):
        return self._build_settings(recall_query_embedding, user_id)

    def default_declarative_config(self, recall_query_embedding):
        return self._build_settings(recall_query_embedding)

    def default_procedural_config(self, recall_query_embedding):
        return self._build_settings(recall_query_embedding)
