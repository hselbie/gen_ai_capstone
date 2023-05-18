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

looker_metadata = get_content_metadata.execute()
embedding = VertexEmbeddings(TextEmbeddingModel.from_pretrained('embedding-gecko-001'), requests_per_minute=REQUESTS_PER_MINUTE)

reports = looker_metadata['embedding_list'].values

looker_index = LookerDashboardIndex(INDEX_PATH, text_items=reports, embedding=embedding)
l = looker_index.query_index(query=query_string)
print(l)

# for i in l:
#     print(i)





# embeddings = embedding_model.get_embeddings(["What is life?"])

# for embedding in embeddings:
#     vector = embedding.values
#     print(f"Length = {len(vector)}")
#     print(vector)


