import math
import looker_sdk
import functools
import time
import numpy as np
from match_looker_content import parse_search_input as psi
from tenacity import retry, stop_after_attempt, wait_fixed
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures.process import ProcessPoolExecutor
from tqdm.auto import tqdm
import pandas as pd
import numpy as np


class CreateLookerEmbedding():
    def __init__(self, sdk, looker_metadata, embedding_model, query_question) -> None:
        self.sdk = sdk
        self.looker_metadata = looker_metadata
        self.embedding_model = embedding_model
        self.query_question = query_question

    def generate_batches(self, sentences: list[str], batch_size: int):
        for i in range(0, len(sentences), batch_size):
            yield sentences[i: i + batch_size]

    def encode_texts_to_embeddings(self, sentences: list[str]):
        try:
            embeddings = self.embedding_model.get_embeddings(sentences)
            return [embedding.values for embedding in embeddings]
        except Exception:
            return [None for _ in range(len(sentences))]

    def encode_text_to_embedding_batched(self, sentences: list[str], api_calls_per_second: int = 10, batch_size: int = 5):
        embeddings_list = []
        # Prepare the batches using a generator
        batches = self.generate_batches(sentences, batch_size)
        seconds_per_job = 1 / api_calls_per_second

        with ThreadPoolExecutor() as executor:
            futures = []
            for batch in tqdm(
                    batches, total=math.ceil(len(sentences) / batch_size), position=0):
                futures.append(
                    executor.submit(functools.partial(
                        self.encode_texts_to_embeddings), batch)
                )
                time.sleep(seconds_per_job)
            for future in futures:
                embeddings_list.extend(future.result())
        is_successful = [embedding is not None for sentence,
                         embedding in zip(sentences, embeddings_list)]
        embeddings_list_successful = np.squeeze(
            np.stack(
                [embedding for embedding in embeddings_list if embedding is not None])
        )
        return is_successful, embeddings_list_successful

    def extract_query_parameters(self):
        x = psi.entity_extraction(self.query_question)
        return x


    def generate_query_embeddings(self):
        entity_based_question = self.extract_query_parameters()
        query_question = [entity_based_question]
        x,y = self.encode_text_to_embedding_batched(query_question, api_calls_per_second=10, batch_size=5)

        return y

    def generate_looker_embeddings(self):
        content_metadata= self.looker_metadata['embedding_list'].tolist()

        is_successful, content_metadata_embeddings= self.encode_text_to_embedding_batched(
            content_metadata, api_calls_per_second=10, batch_size=5)

        content_metadata= np.array(content_metadata)[is_successful]

        return content_metadata_embeddings

if __name__ == "__main__":
    from vertexai.preview.language_models import TextEmbeddingModel
    ini = '/usr/local/google/home/hugoselbie/code_sample/py/ini/demo.ini'
    sdk = looker_sdk.init40(config_file=ini)
    query='test'
    looker_metadata= pd.read_csv("looker_metadata.csv")
    embedding_model = TextEmbeddingModel.from_pretrained(
        "textembedding-gecko@001")
    recommended = CreateLookerEmbedding(
    sdk=sdk, looker_metadata=looker_metadata, 
    embedding_model=embedding_model, 
    query_question=query).generate_looker_embeddings()