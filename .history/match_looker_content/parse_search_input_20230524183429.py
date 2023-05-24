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


def entity_extraction(sentence, model: str = "text-bison-001"):
  prompt_template = """Perform entity extraction on the question below and only list entities that were given in the question. Use the following definitions for the entities to extract and only output the json object:
  
1. YEAR or Date: The year of the report, the current year is 2023.
2. CURRENCY: The currency, the default value is USD
3. REGION: The country, such as Canada, USA, Germany, Japan, etc.
4. PRODUCT: The name of product being sold, such as body scrub, laptop, pure fresh juice, etc.
5. CUSTOMER: The name of the customer, such as Standard Retail, Tachinome Stores, Tirgil Canary, etc.
6. Services:
 'IPs',
 'Date Granularity',
 'Principals Trend',
 'Query Count',
 'User Count',
 'State',
 'City',
 'Traffic Source',
 'User Gender',
 'Date',
 'Location',
 'Country',
 'Name',
 'Total Order Count',
 'web analytics',
 'top line metrics']
JSON OUTPUT FORMAT:
{{'Year': <the year>, 
'Sales': 'USD',
'IPs': <value> ,
 'Date Granularity': <value>,
 'Principals Trend': <value>,
 'Query Count': <value>,
 'User Count': <value>,
 'State': <value>,
 'City': <value>,
 'Traffic Source': <value>,
 'User Gender': <value>,
 'Date': <value>,
 'Location': <value>,
 'Country': <value>,
 'Name': <value>,
 'Total Order Count': <value>,
 'web analytics': <value>,
 'top line metrics'Currency': 'USD', 
'Region': <The region mentioned>, 
'Product': <The name of the product>,
'Customer': <the customer>}}
Now answer the following question:
Question: {}
Answer:
  """

  assembled_prompt = prompt_template.format(sentence)
  result_str = str(vertex_llm.predict(assembled_prompt, model))
  result_str = result_str.replace('null', '')
  print("prompt result entity extraction: ", result_str)
  try:
    if "```json" in result_str:
      json_result = json.loads(result_str.split("```json")[1].replace("\n","").split("```")[0].strip().replace("'", "\""))
    elif "```" in result_str:
      json_result = json.loads(result_str.split("```")[1].strip().replace("'", "\""))
    else:
      json_result = json.loads(result_str.replace('\'', '\"'))
  except:
    json_result = {}
  return json_result
  
def answer_question(question, header, table_str):
  prompt_template = f"""
  {question}
  {header}
  {table_str}
  """
  print(prompt_template)
  prompt_response = str(vertex_llm.predict(prompt_template))
  return _clean_response(prompt_response)

def summarize_response(table_str, header):
  prompt_template = f"""
  Summarize the following information:
  {header}
  {table_str}
  """
  print(prompt_template)
  prompt_response = str(vertex_llm.predict(prompt_template))
  return prompt_response

def summarize_product_sales_results(table_str):
  prompt_template = f"""
  Summarize the following products sales results:
  {table_str}
  """
  print(prompt_template)
  prompt_response = str(vertex_llm.predict(prompt_template))
  print(prompt_response)
  return prompt_response

def summarize_news_results(table_results, header):
  
  prompt_template = f"""
  Summarize the trend of the news articles by month:
  {header}
  {table_results}
  """
  print(prompt_template)
  prompt_response = str(vertex_llm.predict(prompt_template))
  print(prompt_response)
  return _clean_response(prompt_response)

def summarize_trend(table_results, header):
  
  prompt_template = f"""
  Summarize the trend for the following information:
  {header}
  {table_results}
  """
  print(prompt_template)
  prompt_response = str(vertex_llm.predict(prompt_template))
  print(prompt_response)
  return _clean_response(prompt_response)

def summarize_on_time_results(table_results, header):
  
  prompt_template = f"""
  Summarize the following on time delivery results:
  {header}
  {table_results}
  """
  print(prompt_template)
  prompt_response = str(vertex_llm.predict(prompt_template))
  print(prompt_response)
  return prompt_response

def get_top_item(question, table_str):
  prompt_template = f"""
  {question} based on the following information:
  {table_str}
  """

  prompt_response = str(vertex_llm.predict(prompt_template))
  return prompt_response

def get_selected_company(prompt_response):
  prompt_template = """
Perform NER on the following sentence and only extract the name of the company given in the sentence. Use the following definition to extract the Company:

1. Company: The name of the company

OUTPUT FORMAT:
{{'Company': <the company>}}

SENTENCE
{}

"""

  assembled_prompt = prompt_template.format(prompt_response)
  response = str(vertex_llm.predict(assembled_prompt)).replace("'", "\"")

  selected_company = json.loads(response)['Company']
  return selected_company

if __name__ == '__main__':
  print(entity_extraction(sentence="Who is my top customer last year in emea?", model="text-bison-001"))