"""Helper LLM Prompt functions."""
import json
from vertexai.preview.language_models import TextGenerationModel 
from match_looker_content.vertex_llm import VertexLLM

MODEL='text-bison@001'
OUTPUT_TOKENS=1024
TEMPERATURE=0
TOP_P=0.2
TOP_K=40

model = TextGenerationModel.from_pretrained(MODEL)
vertex_llm = VertexLLM(
  model=model,
  max_output_tokens=1024,
  temperature=0,
  top_p=0.2,
  top_k=40
)

def _clean_response(response: str) -> str:
  if response.startswith('> '):
    return response.replace('> ', '', 1)
  return response


def dashboard_summary_extraction(query_list, model: str = "text-bison-001"):
  prompt_template = f"""
  Summarize this dashboard features as plain text {query_list}, the first element is always the dashboard title.
  """
  result_str = str(vertex_llm.predict(prompt_template, model))
  print("prompt result entity extraction: ", result_str)
  return result_str

if __name__ == '__main__':
  pass