from vertexai.preview.language_models import TextEmbeddingModel
from looker_metadata import get_content_metadata as gcm
from match_looker_content.vertex_llm import VertexEmbeddings
from match_looker_content.create_looker_index import LookerDashboardIndex
import pandas as pd
import looker_sdk

ini = '/usr/local/google/home/hugoselbie/code_sample/py/ini/Looker_23_3.ini'
sdk = looker_sdk.init40(config_file=ini)
REQUESTS_PER_MINUTE = 15
INDEX_PATH='.chroma/index'

query_string = 'What is dashboard about sales?'

embedding_model = TextEmbeddingModel('embedding-gecko-001')

get_content_metadata = gcm.GetDashboardMetadata(sdk)

# looker_metadata = get_content_metadata.execute()
# looker_metadata.to_csv('looker_metadata.csv')
looker_metadata = pd.read_csv('looker_metadata.csv')


embedding_model = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")
recommended = gcm.CreateLookerEmbedding(sdk=sdk,looker_metadata=looker_metadata, embedding_model=embedding_model).execute()

looker_metadata['similarity_score'] = recommended

print(looker_metadata.head())
