# Write code to call an azureml endpoint to generate docs for a github repository

import argparse
import os
import urllib.request
import json
import ssl

# Parse input arguments
parser = argparse.ArgumentParser()
parser.add_argument('--directory', type=str, help='The directory path to generate the docs')
parser.add_argument('--key', type=str, help='The webservice key')
parser.add_argument('--url', type=str, help='The webservice url')
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



# First, ask the openai endpoint to generate rst files

# read prompt from topics_files_request.txt

import os
with open(os.path.join(".", "topics_files_request.txt"), "r") as f:
    topics_files_request = f.read()

print(topics_files_request)

topics = call_webservice({"question": topics_files_request}, args.key, args.url)

recommended_topics = topics["output"].split("\n")

rst_file_names_request = "Generate the rst file names for the ml-wrappers repository from the topics: " + "\n".join(recommended_topics)

sample_rst_files = ["contributing.rst",
                    "explainers.rst",
                    "importances.rst",
                    "index.rst",
                    "notebooks.rst",
                    "overview.rst",
                    "transformations.rst",
                    "usage.rst",
                    "visualizations.rst"]

rst_file_names_request += "\nExample:" + "\n".join(sample_rst_files)

rst_files = call_webservice({"question": rst_file_names_request}, args.key, args.url)

recommended_rst_files = rst_files["output"]

print(rst_files)

list_rst_files = recommended_rst_files.split("\n")

for rst_file, topic in zip(list_rst_files, recommended_topics):
    rst_gen_request = ("Generate the " + rst_file + " file for the ml-wrappers repository for the topic " + topic)
    rst_file_contents = call_webservice({"question": rst_gen_request}, args.key, args.url)
    print(rst_file_contents)
    with open(os.path.join(args.directory, rst_file), "w") as f:
        f.write(rst_file_contents["output"])
