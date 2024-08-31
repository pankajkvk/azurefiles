import azure.functions as func
import logging
import os
from microsoft_graph import GraphClient
from microsoft_graph.auth import ClientSecretCredential
from transformers import pipeline
import pandas as pd
import numpy as np
import io
from datetime import datetime

def init():
    global classifier
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def classify_file(content, candidate_labels):
    result = classifier(content, candidate_labels)
    return result['labels'][0]

def analyze_column(series):
    summary = []
    dtype = series.dtype
    name = series.name

    if pd.api.types.is_numeric_dtype(dtype):
        summary.append(f"{name} (Numeric) - Min: {series.min():.2f}, Max: {series.max():.2f}, Mean: {series.mean():.2f}")
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        summary.append(f"{name} (Date/Time) - Earliest: {series.min()}, Latest: {series.max()}")
    elif pd.api.types.is_string_dtype(dtype):
        unique_count = series.nunique()
        most_common = series.value_counts().index[0] if not series.empty else "N/A"
        summary.append(f"{name} (Text) - Unique Values: {unique_count}, Most Common: {most_common}")
    else:
        summary.append(f"{name} (Other) - Unique Values: {series.nunique()}")

    return ", ".join(summary)

def prepare_content(df):
    summary = []

    # Overall dataframe info
    summary.append(f"Rows: {len(df)}, Columns: {len(df.columns)}")

    # Analyze each column
    for col in df.columns:
        summary.append(analyze_column(df[col]))

    # Check for potential relationships
    if len(df.columns) > 1:
        corr_matrix = df.select_dtypes(include=[np.number]).corr()
        if not corr_matrix.empty:
            high_corr = np.abs(corr_matrix.values) > 0.8
            np.fill_diagonal(high_corr, False)
            if high_corr.any():
                correlated = np.where(high_corr)
                for i, j in zip(*correlated):
                    if i < j:  # to avoid duplicates
                        summary.append(f"Strong correlation between {corr_matrix.index[i]} and {corr_matrix.columns[j]}")

    return " ".join(summary)

def generate_file_name(original_name):
    base_name = os.path.splitext(original_name)[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_analyzed_{timestamp}"

def main(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {myblob.name}\n"
                 f"Blob Size: {myblob.length} bytes")

    # Initialize the Graph client
    credential = ClientSecretCredential(
        tenant_id=os.environ["TENANT_ID"],
        client_id=os.environ["CLIENT_ID"],
        client_secret=os.environ["CLIENT_SECRET"]
    )
    graph_client = GraphClient(credential)

    # Read Excel file content
    content = myblob.read()
    df = pd.read_excel(io.BytesIO(content))
    file_content = prepare_content(df)

    # Classify file
    candidate_labels = ["financial_data", "inventory_data", "sales_data", "customer_data", "operational_data"]
    file_class = classify_file(file_content, candidate_labels)

    # Generate new file name
    new_file_name = generate_file_name(myblob.name)

    # Move and rename file in OneDrive
    new_path = f"/processed_files/{file_class}/{new_file_name}.xlsx"
    
    # Create the directory if it doesn't exist
    graph_client.api(f'/me/drive/root:/processed_files/{file_class}').request().create_folder()

    # Move and rename the file
    graph_client.api(f'/me/drive/root:/{myblob.name}').move(new_path)

    logging.info(f"File processed and moved to: {new_path}")
    logging.info(f"File summary: {file_content}")

# Initialize models when the Function starts
init()