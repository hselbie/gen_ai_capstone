Flask-LookerApp-Search
===================

A simple flask application that calls various GCP gen ai services.

### Installation

To run this application install the requirements in a virtual environment, run `python chat.py` and visit `http://localhost:5000` on one or more browser tabs.

    $ python chat.py


### For GenAI reviewers
The concept here is to gather a series of metadata about Looker Dashboard and create a dashboard recommender service.

First we gather the metadata about the Looker Dashboard this can be seen in the Looker Metadata folder under `get_content_metadata.py`.
This data can is then used to create embeddings. I originally used Vertex AI to create embeddings for the dashboards, but have also experimented using Chroma instead. The vertex embedding is under `looker_metadata/create_looker_embeddings.py` and the chroma workflow is in the `app/main/routes.py`

This is all wrapped in a flask application and executed from the browser. Please see the video in the appropriate drive folder.

Once the correct match has been returned the metadata is sent to the bison model to summarize the metadata for dashboards as a single shot prompt. This can be found in `match_looker_content/parse_search_input.py`.
