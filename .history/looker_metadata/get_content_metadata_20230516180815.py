import looker_sdk
import pandas as pd


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
                    temp = {}
                    temp['name'] = filter.get('dashboard_filter_name')
                    filterables.append(temp)
        return filterables

    def get_dashboard_element_metadata(self, sdk, dashboard_id: str) -> dict:
        data_storage = []
        dash_elements = sdk.dashboard_dashboard_elements(dashboard_id=dashboard_id)
        for dash_element in dash_elements:
            element_metadata = {}
            element_metadata['id'] = dash_element['id']
            element_metadata['dashboard_id'] = dashboard_id
            element_metadata['body_text'] = dash_element['body_text']
            element_metadata['note_text'] = dash_element['note_text']
            element_metadata['subtitle_text'] = dash_element['subtitle_text']
            element_metadata['title'] = dash_element['title']
            element_metadata['filterables'] = self.extract_filterables(sdk,dash_element)
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
        metadata['dashboard_element_metadata'] = self.get_dashboard_element_metadata(sdk, dashboard_id)
        return metadata

    def execute(self):
        response = []
        all_dashboard_id = self.get_all_dashboard_id(sdk)
        for dashboard_id in all_dashboard_id:
            dashboard_metadata = self.get_dashboard_metadata(sdk, dashboard_id)
            mdata = self.create_metadata_dict(dashboard_metadata)
            response.append(mdata)
        return response


            
if __name__ == '__main__':
    ini = '/usr/local/google/home/hugoselbie/code_sample/py/ini/Looker_23_3.ini'
    sdk = looker_sdk.init40(config_file=ini)

    get_content_metadata = GetDashboardMetadata(sdk)
    response = get_content_metadata.execute()
    df = pd.DataFrame(response)
    
    print(df.head())            
