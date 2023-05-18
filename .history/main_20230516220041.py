from vertexai.preview.language_models import TextGenerationModel,\
                                            ChatModel,\
                                            InputOutputTextPair,\
                                            TextEmbeddingModel
import looker_metadata as lm
import match_looker_content as mlc
import pandas as pd
import looker_sdk

ini = '/usr/local/google/home/hugoselbie/code_sample/py/ini/Looker_23_3.ini'
sdk = looker_sdk.init40(config_file=ini)

get_content_metadata = lm.GetDashboardMetadata(sdk)
looker_metadata = get_content_metadata.execute()

embedding_model = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")

looker_metadata['embedding_values'] = [emb.values for emb in embedding_model.get_embeddings(looker_metadata['embedding_list'].values)]

print(looker_metadata.head())


embeddings = embedding_model.get_embeddings(["What is life?"])

for embedding in embeddings:
    vector = embedding.values
    print(f"Length = {len(vector)}")
    print(vector)


