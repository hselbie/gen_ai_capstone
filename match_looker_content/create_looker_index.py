"""Uses Langchain and Vertex AI Embeddings to match Looker reports to a user query."""

import os
from typing import List
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.vectorstores import Chroma


class LookerDashboardIndex:
  def __init__(self, persist_directory: str, text_items: List[str], embedding):
    self.persist_directory = persist_directory
    self.embedding = embedding
    self.text_items = text_items


  def query_index(self, query: str, k: int = 3) -> List[str]:
    """Query the index and return the matching reports."""
    report_matches = []
    if os.path.isdir(self.persist_directory):
        vectorstore = Chroma(embedding_function=self.embedding, persist_directory=self.persist_directory)
        index = VectorStoreIndexWrapper(vectorstore=vectorstore)
    else:
        vectordb = Chroma.from_texts(self.text_items, self.embedding, persist_directory=self.persist_directory)
        vectordb.persist()
        index = VectorStoreIndexWrapper(vectorstore=vectordb)
    docs = index.vectorstore.similarity_search_with_score(query,k=k)
    for report in docs:
        report_title_match = report[0].page_content.split(':')[0].replace('_', ' ')
        report_matches.append(report_title_match)

    return report_matches