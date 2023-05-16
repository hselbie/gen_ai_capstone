import looker_sdk

ini = '/usr/local/google/home/hugoselbie/code_sample/py/ini/Looker_23_3.ini'

sdk = looker_sdk.init40(config_file=ini)

dashboards = sdk.all_dashboards()
