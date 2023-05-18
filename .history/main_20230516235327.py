from vertexai.preview.language_models import TextEmbeddingModel
from looker_metadata import get_content_metadata as gcm
from match_looker_content import VertexEmbeddings, LookerDashboardIndex
import pandas as pd
import looker_sdk

ini = '/usr/local/google/home/hugoselbie/code_sample/py/ini/Looker_23_3.ini'
sdk = looker_sdk.init40(config_file=ini)
REQUESTS_PER_MINUTE = 15
INDEX_PATH='.chroma/index'

get_content_metadata = gcm.GetDashboardMetadata(sdk)

looker_metadata = get_content_metadata.execute()
embedding = VertexEmbeddings(TextEmbeddingModel(), requests_per_minute=REQUESTS_PER_MINUTE)

reports = looker_metadata['embedding_list'].values

looker_index = LookerDashboardIndex(INDEX_PATH, text_items=reports, embedding=embedding)


# embeddings = embedding_model.get_embeddings(["What is life?"])

# for embedding in embeddings:
#     vector = embedding.values
#     print(f"Length = {len(vector)}")
#     print(vector)


