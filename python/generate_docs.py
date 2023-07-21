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

def generate_file(file_name, request, directory):
    contents = call_webservice({"question": request}, args.key, args.url)

    with open(os.path.join(directory, file_name), "w") as f:
        f.write(contents["output"])

    return contents

# First, ask the openai endpoint to generate rst files

# Read prompt from topics_files_request.txt
with open(os.path.join(".", "topics_files_request.txt"), "r") as f:
    topics_files_request = f.read()
    topics_files_request = topics_files_request.replace("{repository_name}", args.repository_name)

print("Topics files request:")
print(topics_files_request)
print("\n\n")

topics = call_webservice({"question": topics_files_request}, args.key, args.url)

recommended_topics = topics["output"].split("\n")

rst_file_names_request = f"Generate the rst file names for the {args.repository_name} repository from the topics below.  Do not add numbers to the topics. " + "\n".join(recommended_topics)

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

print("Recommended rst files:")
print(rst_files)
print("\n\n")

list_rst_files = recommended_rst_files.split("\n")

# Ask the openai endpoint to generate an rst file for each topic
for rst_file, topic in zip(list_rst_files, recommended_topics):
    rst_gen_request = f"Generate the {rst_file} file for the {args.repository_name} repository for the topic {topic}. Do not add numbers to the topic. Output as a raw rst file."
    rst_file_contents = generate_file(rst_file, rst_gen_request, args.directory)

    print(f"Rst file contents for file {rst_file} and topic {topic}:")
    print(rst_file_contents)
    print("\n\n")


# Ask the openai endpoint to generate the conf.py, index.rst, and .readthedocs.yaml files
requests = {
    "conf.py": f"Generate the conf.py file for the {args.repository_name} repository.  This should be similar to the file https://github.com/interpretml/interpret-community/blob/main/python/docs/conf.py.",
    "index.rst": f"Generate the index.rst file for the {args.repository_name} repository.  Produce the output as if it were an rst file (do not use triple backticks to indicate a codeblock).  It should reference the previous generated rst files: " + "\n".join(list_rst_files),
    ".readthedocs.yaml": f"Generate the .readthedocs.yaml file for the {args.repository_name} repository.  Do not include any full sentences at the end describing the yaml."
}

for file_name, value in requests.items():
    directory = args.directory
    if file_name == ".readthedocs.yaml":
        directory = args.rootdirectory
    contents = generate_file(file_name, value, directory)
    print(f"{file_name} contents:\n{contents}\n\n")
