import looker_sdk
import random
import math
import time
import functools
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures.process import ProcessPoolExecutor
from tqdm.auto import tqdm
import pandas as pd
import numpy as np
import ast
import re


class GetDashboardMetadata():
    def __init__(self, sdk) -> None:
        self.sdk = sdk

    def get_all_dashboard_id(self, sdk):
        dashboards = sdk.all_dashboards(fields='id')
        dashboards = [dashboard['id'] for dashboard in dashboards]
        return dashboards

    def get_dashboard_metadata(self, sdk, dashboard_id: str) -> dict:
        dashboard = sdk.dashboard(dashboard_id=dashboard_id)
        return dashboard

    def extract_filterables(self, sdk, dashboard_element_metadata: dict) -> dict:
        filterables = []
        if dashboard_element_metadata['result_maker']:
            listeners = dashboard_element_metadata['result_maker']['filterables'][0]['listen']
            if listeners:
                for filter in listeners:
                    filter_name = filter.get('dashboard_filter_name')
                    filterables.append(filter_name)
        return filterables

    def extract_text_from_body_text(self, sdk, body_text: dict) -> dict:
        response = []
        if body_text:
            try:
                for text in ast.literal_eval(body_text):
                    r = text.get('children')[0].get('text')
                    response.append(r)
            except:
                print('xx')
        response = [x for x in response if len(x) > 0]
        return response

    def get_dashboard_element_metadata(self, sdk, dashboard_id: str) -> dict:
        data_storage = []
        dash_elements = sdk.dashboard_dashboard_elements(
            dashboard_id=dashboard_id)
        for dash_element in dash_elements:
            element_metadata = {}
            element_metadata['dashboard_id'] = dashboard_id
            element_metadata['body_text'] = self.extract_text_from_body_text(
                sdk, dash_element['body_text'])
            element_metadata['note_text'] = dash_element['note_text']
            element_metadata['subtitle_text'] = dash_element['subtitle_text']
            element_metadata['title'] = dash_element['title']
            element_metadata['filterables'] = self.extract_filterables(
                sdk, dash_element)
            data_storage.append(element_metadata)
        return data_storage

    def create_metadata_dict(self, dashboard_metadata: dict) -> dict:
        metadata = {}
        title = dashboard_metadata['title']
        description = dashboard_metadata['description']
        dashboard_id = dashboard_metadata['id']
        metadata['dashboard_id'] = dashboard_id
        metadata['title'] = title
        metadata['description'] = description
        return metadata

    def clean_embedding_data(self, row):
        data = row.split(',')
        data = [mystr for mystr in data if len(mystr) > 2]
        data = [re.sub('[^a-zA-Z0-9 \n\.]', '', elem) for elem in data]
        return data

    def execute(self):
        db_meta = []
        elem_df_list = []
        all_dashboard_id = self.get_all_dashboard_id(sdk=self.sdk)
        for dashboard_id in all_dashboard_id:
            element_metadata = self.get_dashboard_element_metadata(
                self.sdk, dashboard_id)
            dashboard_metadata = self.get_dashboard_metadata(
                self.sdk, dashboard_id)
            mdata = self.create_metadata_dict(dashboard_metadata)
            db_meta.append(mdata)
            elem_df = pd.DataFrame(element_metadata)
            elem_df_list.append(elem_df)
        elem_df = pd.concat(elem_df_list)

        db_df = pd.DataFrame(db_meta)
        response = pd.merge(db_df, elem_df, on='dashboard_id', how='outer')
        response.rename(columns={'title_y': 'element_title'}, inplace=True)
        response.rename(columns={'title_x': 'dash_title'}, inplace=True)
        response['embedding_list'] = response[response.columns[1:]].apply(
            lambda x: ','.join(x.dropna().astype(str)),
            axis=1
        )
        response['embedding_list'] = response['embedding_list'].apply(
            lambda x: self.clean_embedding_data(x)
        )

        return response


class CreateLookerEmbedding():
    def __init__(self, sdk, looker_metadata, embedding_model) -> None:
        self.sdk = sdk
        self.looker_metadata = looker_metadata
        self.embedding_model = embedding_model

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

    def execute(self):
        content_metadata= self.looker_metadata['embedding_list'].tolist()
        is_successful, content_metadata_embeddings= self.encode_text_to_embedding_batched(
            content_metadata, api_calls_per_second=10, batch_size=5)

        content_metadata= np.array(content_metadata)[is_successful]

        question_index = random.randint(0, 99)

        print(f"Query question = {content_metadata[question_index]}")
        x = content_metadata

        # Get similarity scores for each embedding by using dot-product.
        scores = np.dot(content_metadata_embeddings[question_index], content_metadata.T)

        # Print top 20 matches
        for index, (question, score) in enumerate(
            sorted(zip(content_metadata, scores), key=lambda x: x[1], reverse=True)[:20]
        ):
            print(f"\t{index}: {question}: {score}")



if __name__ == '__main__':
    ini = '/usr/local/google/home/hugoselbie/code_sample/py/ini/Looker_23_3.ini'
    sdk = looker_sdk.init40(config_file=ini)

    get_content_metadata = GetDashboardMetadata(sdk)
    response = get_content_metadata.execute()
    df = pd.DataFrame(response)
