import looker_sdk
import math
from tenacity import retry, stop_after_attempt, wait_fixed
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures.process import ProcessPoolExecutor
from tqdm.auto import tqdm
import pandas as pd
import numpy as np
import ast
import re
import sys
print(sys.path)


class GetDashboardMetadata():
    def __init__(self, sdk) -> None:
        self.sdk = sdk

    def get_all_dashboard_id(self, sdk):
        dashboards = sdk.all_dashboards(fields='id, folder')
        dashboards = [dash for dash in dashboards if not dash.folder.is_personal]
        dashboards = [dashboard['id'] for dashboard in dashboards if '::' not in dashboard['id']]
        return dashboards

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(10))
    def get_looker_dashboard(self, sdk, dashboard_id: str):
        resp = sdk.dashboard(dashboard_id=dashboard_id)
        return resp


    def get_dashboard_metadata(self, sdk, dashboard_id: str) -> dict:
        dashboard = self.get_looker_dashboard(sdk, dashboard_id)
        dashboard_metadata = {}
        dashboard_metadata['id'] = dashboard['id']
        dashboard_metadata['title'] = dashboard['title']
        dashboard_metadata
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

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(10))
    def get_looker_dashboard_elements(self, sdk, dashboard_id: str):
        resp = sdk.dashboard_dashboard_elements(dashboard_id=dashboard_id)
        return resp

    def get_dashboard_element_metadata(self, sdk, dashboard_id: str) -> dict:
        data_storage = []
        dash_elements = self.get_looker_dashboard_elements(sdk, dashboard_id)

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
        for dashboard_id in tqdm(all_dashboard_id, total=math.ceil(len(all_dashboard_id)), position=0):
            print(dashboard_id)
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
        response['embedding_list'] = response[response.columns[0:]].apply(
            lambda x: ','.join(x.dropna().astype(str)),
            axis=1
        )
        response['embedding_list'] = response['embedding_list'].apply(
            lambda x: self.clean_embedding_data(x)
        )

        return response


if __name__ == '__main__':
    ini = '/usr/local/google/home/hugoselbie/code_sample/py/ini/Looker_23_3.ini'
    sdk = looker_sdk.init40(config_file=ini)

    get_content_metadata = GetDashboardMetadata(sdk)
    response = get_content_metadata.execute()
    df = pd.DataFrame(response)
    df.to_csv('looker_metadata.csv')
