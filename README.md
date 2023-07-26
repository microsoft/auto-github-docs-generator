# Project

Generate readthedocs website documentation for your github repository auto-magically using your LLM endpoint!

The auto-github-docs-generator repository started as an AzureML hackathon FHL (Fix, Hack, Learn) project developed over July 17-26.
You can view the project video here:
https://clipchamp.com/watch/9agSQLTbEcV

Goal of this project was to experiment with using OpenAI/GPT4 to generate documentation for OSS Github repositories.

As part of this project, the following documentation website were automatically generated:

https://vision-explanation-methods.readthedocs.io/en/latest/index.html
https://ml-wrappers.readthedocs.io/en/latest/index.html

This document generator sends multiple prompts to generate the Github docs to the deployed endpoint:

![image](https://github.com/microsoft/auto-github-docs-generator/assets/24683184/ea72345b-1a97-4a18-aaf9-3fa18b14cf4b)

For this project the endpoint was a deployed webservice created from an AzureML promptflow pipeline:

![image](https://github.com/microsoft/auto-github-docs-generator/assets/24683184/7f4cb3c9-4b34-4bbe-a11d-0c1709a3abb1)

Contributions are welcome!

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
