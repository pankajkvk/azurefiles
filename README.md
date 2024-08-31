Description of files included in the repo:

• excel_processor.py:
  - Core logic for processing Excel files
  - Uses pandas for data manipulation and analysis
  - Implements zero-shot classification with Hugging Face Transformers
  - Functions:
    • init(): Initializes the classifier
    • classify_file(): Categorizes the file content
    • analyze_column(): Provides summary statistics for each column
    • prepare_content(): Generates a comprehensive summary of the file
    • generate_file_name(): Creates a unique, descriptive filename
    • process_excel_file(): Main function orchestrating the entire process
  - Utilizes Microsoft Graph API for OneDrive operations

• __init__.py:
  - Entry point for the Azure Function
  - Imports process_excel_file from excel_processor.py
  - Contains the main() function triggered by Azure

• function.json:
  - Defines the function's bindings and trigger
  - Configures the blob trigger for Excel files
  - Specifies the input binding for the blob storage

• requirements.txt:
  - Lists all Python package dependencies
  - Includes azure-functions, pandas, openpyxl, transformers, numpy, microsoft-graph-core

• host.json:
  - Global configuration file for the Azure Functions host
  - Defines logging settings and extension bundle version

• local.settings.json:
  - Contains local development settings and connection strings
  - Stores environment variables (TENANT_ID, CLIENT_ID, CLIENT_SECRET)
  - Not included in source control due to sensitive information

• .gitignore:
  - Specifies intentionally untracked files to ignore
  - Includes patterns for Python, Azure Functions, and IDE-specific files

Project structure:
- Root directory contains configuration files (requirements.txt, host.json, etc.)
- ExcelProcessorFunction/ subdirectory holds the actual function code

Key technical aspects:
- Leverages Azure Blob storage trigger for file processing
- Employs pandas for data analysis
- Utilizes Hugging Face Transformers for NLP-based file classification
- Integrates with Microsoft Graph API for OneDrive file management
- Designed for scalability and handling diverse Excel file structures
- Implements logging for monitoring and debugging
- Uses environment variables for secure credential management

