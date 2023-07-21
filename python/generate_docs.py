# Write code to call an azureml endpoint to generate docs for a github repository

import argparse
import os
import urllib.request
import json
import ssl

# Parse input arguments
parser = argparse.ArgumentParser()
parser.add_argument('--directory', type=str, help='The directory path to generate the docs')
parser.add_argument('--rootdirectory', type=str, help='The root directory path to the repository')
parser.add_argument('--key', type=str, help='The webservice key')
parser.add_argument('--url', type=str, help='The webservice url')
parser.add_argument('--repository-name', type=str, help='The repository name')
args = parser.parse_args()


def allowSelfSignedHttps(allowed):
    # bypass the server certificate verification on client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

def call_webservice(data, api_key, url):
    allowSelfSignedHttps(True) # this line is needed if you use self-signed certificate in your scoring service.

    body = str.encode(json.dumps(data))

    if not api_key:
        raise Exception("A key should be provided to invoke the endpoint")

    # The azureml-model-deployment header will force the request to go to a specific deployment.
    # Remove this header to have the request observe the endpoint traffic rules
    headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key), 'azureml-model-deployment': 'blue' }

    req = urllib.request.Request(url, body, headers)

    try:
        response = urllib.request.urlopen(req)

        result = response.read()
        print(result)
        result = json.loads(result)
    except urllib.error.HTTPError as error:
        print("The request failed with status code: " + str(error.code))

        # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
        print(error.info())
        print(error.read().decode("utf8", 'ignore'))
    return result

def print_request_info(question, search):
    print(f"Question: {question}")
    print("\n")
    print(f"Search: {search}")
    print("\n\n")

def print_response(response):
    print(f"Response: {response}")
    print("\n\n")

def generate_file(file_name, search, question, directory):
    print_request_info(question, search)
    contents = call_webservice({"question": question, "search": search}, args.key, args.url)
    print_response(contents)

    with open(os.path.join(directory, file_name), "w") as f:
        f.write(contents["output"])

    return contents

# First, ask the openai endpoint to generate rst files

# Read prompt from topics_files_request.txt
with open(os.path.join(".", "topics_files_request.txt"), "r") as f:
    topics_files_request = f.read()
    topics_files_request = topics_files_request.replace("{repository_name}", args.repository_name)

topics_search = "main top-level topics in ml-wrappers repository"

print_request_info(topics_files_request, topics_search)

topics = call_webservice({"question": topics_files_request, "search": topics_search}, args.key, args.url)

print_response(topics)

recommended_topics = topics["output"].split("\n")

rst_file_names_question = f"Generate the rst file names for the {args.repository_name} repository from the topics below.  Do not add numbers to the topics. \n\n" + "\n".join(recommended_topics)
rst_file_names_search = topics_search

sample_rst_files = ["contributing.rst",
                    "explainers.rst",
                    "importances.rst",
                    "index.rst",
                    "notebooks.rst",
                    "overview.rst",
                    "transformations.rst",
                    "usage.rst",
                    "visualizations.rst"]

rst_file_names_question += "\n\nExample:" + "\n".join(sample_rst_files)

print_request_info(rst_file_names_question, rst_file_names_search)

rst_files = call_webservice({"question": rst_file_names_question, "search": rst_file_names_search}, args.key, args.url)

recommended_rst_files = rst_files["output"]

print_response(topics)

list_rst_files = recommended_rst_files.split("\n")

# Ask the openai endpoint to generate an rst file for each topic
for rst_file, topic in zip(list_rst_files, recommended_topics):
    rst_topic_search = topic
    rst_gen_request = f"Generate the {rst_file} file for the {args.repository_name} repository for the topic {topic}. Do not add numbers to the topic. Output as a raw rst file. Do not add any full sentences at the end describing the file. Do not add triple backticks to indicate the file type at the top."
    rst_file_contents = generate_file(rst_file, rst_topic_search, rst_gen_request, args.directory)

# Ask the openai endpoint to generate the conf.py, index.rst, and .readthedocs.yaml files
requests = {
    "conf.py": f"Generate the conf.py file for the {args.repository_name} repository.  This should be similar to the file https://github.com/interpretml/interpret-community/blob/main/python/docs/conf.py.",
    "index.rst": f"Generate the index.rst file for the {args.repository_name} repository.  Produce the output as if it were an rst file (do not use triple backticks to indicate a codeblock).  It should reference the previous generated rst files: " + "\n".join(list_rst_files),
    # ".readthedocs.yaml": f"Generate the .readthedocs.yaml file for the {args.repository_name} repository.  Do not include any full sentences at the end describing the yaml."
}

for file_name, question in requests.items():
    directory = args.directory
    # if file_name == ".readthedocs.yaml":
    #     directory = args.rootdirectory
    search = topics_search
    contents = generate_file(file_name, search, question, directory)

# write the .readthedocs.yaml file directly to the root directory
read_the_docs_content = f"""
version: 2

build:
  os: ubuntu-20.04
  tools:
    python: "3.8"

sphinx:
   builder: html
   configuration: python/docs/conf.py

python:
   install:
   - requirements: requirements-doc.txt
   - method: pip
     path: python

formats:
  - epub
  - pdf
"""
with open(os.path.join(args.rootdirectory, ".readthedocs.yaml"), "w") as f:
    f.write(read_the_docs_content)
