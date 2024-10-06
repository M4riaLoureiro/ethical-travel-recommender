# Process and Index PDF Documents

## This notebook will be used to process the pdf files exported from WikiVoyage and index them in a vector store.

import hashlib
import os
import pickle

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

# from marker.convert import convert_single_pdf
# from marker.logger import configure_logging
# from marker.models import load_all_models
from tqdm import tqdm


def parse_file_name(filename):
    # Remove space and dots on filename
    if filename.endswith(".pdf"):
        name_part = filename[:-4]
        name_part = name_part.replace(" ", "").replace(".", "")
        cleaned_filename = name_part + ".pdf"
    else:
        cleaned_filename = filename.replace(" ", "").replace(".", "")
    return cleaned_filename


def convert_pdf_to_markdown(fname, reference_folder, model_lst, md_out_path=None):

    md_filename = fname.rsplit(".", 1)[0] + ".md"

    pdf_filename = os.path.join(reference_folder, fname)

    print(pdf_filename)
    full_text, _, _ = convert_single_pdf(pdf_filename, model_lst, batch_multiplier=1)

    if md_out_path:
        with open(os.path.join(md_out_path, md_filename), "w+") as f:
            f.write(full_text)
    else:
        return full_text


def download_and_process_pdf_file(
    f_key, text_splitter, markdown_splitter, model_lst, reference_folder="../data/"
):

    temp_file_name = parse_file_name(f_key)

    mdfile = convert_pdf_to_markdown(temp_file_name, reference_folder, model_lst, None)

    md_header_split = markdown_splitter.split_text(mdfile)

    documents = []
    for split in md_header_split:

        split_texts = text_splitter.split_text(split.page_content)

        for i, split_text in enumerate(split_texts):

            document_id = f"{f_key}_part_{i}"
            hash_object = hashlib.md5(document_id.encode())
            hash_hex = hash_object.hexdigest()
            document_id = hash_hex[:10]

            metadata_dict = {
                "document_id": document_id,
                "pdf_name": f_key,
                "pdf_part": i,
            }

            metadata_dict.update(split.metadata)

            documents.append({"metadata": metadata_dict, "content": split_text})

    return documents


def list_pdf_files(directory_path):
    """
    Lists all PDF files in the given directory and attempts to read them as binary data.

    Parameters:
        directory_path (str): The path to the directory containing PDF files.

    Returns:
        dict: A dictionary where keys are filenames and values are raw binary content or text content (if readable).
    """
    pdf_files_content = {}

    # Check if the directory exists
    if not os.path.isdir(directory_path):
        print(f"The directory '{directory_path}' does not exist.")
        return pdf_files_content

    filenames = [f for f in os.listdir(directory_path) if f.lower().endswith(".pdf")]

    return filenames


def main():

    # Usage example
    directory = "../data/"  # Replace with your directory path
    filenames = list_pdf_files(directory)
    print(f"Number of PDFs read: {len(filenames)}")

    configure_logging()
    model_lst = load_all_models()

    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    chunk_size = 500
    chunk_overlap = 100
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on
    )

    documents = []

    for filename in tqdm(filenames):

        print("\n filename: {} \n".format(filename))

        splitted_doc = download_and_process_pdf_file(
            filename,
            text_splitter,
            markdown_splitter,
            model_lst,
            reference_folder="../data/",
        )

        documents.append(splitted_doc)

    flattened_list = [item for sublist in documents for item in sublist]

    # save the documents object into a pickle file to avoid computing it again
    with open("../data/docs_processed.pickle", "wb") as f:
        pickle.dump(flattened_list, f)


if __name__ == "__main__":
    main()
