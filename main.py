import pandas as pd
import os
import json

def create_folder_structure(base_path, folder_path):
    """
    Creates a nested folder structure if it doesn't exist.
    """
    full_path = os.path.join(base_path, folder_path)
    os.makedirs(full_path, exist_ok=True)
    return full_path

def save_json(data, file_path):
    """
    Saves a dictionary as a JSON file.
    """
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

def sheet_to_child_files(sheet_name, data, folder_path):
    """
    Creates two JSON files (English and Deutsch) for a given sheet and folder path.
    """
    english_data = {}
    deutsch_data = {}

    for _, row in data.iterrows():
        key = row.iloc[0]  # Assume the first column is the key
        english = row['english']
        deutsch = row['deutsch']
        
        # Populate the dictionaries
        english_data[key] = english
        deutsch_data[key] = deutsch

    # Save English and Deutsch JSON files
    english_file_path = os.path.join(folder_path, f"{sheet_name}_english.json")
    deutsch_file_path = os.path.join(folder_path, f"{sheet_name}_deutsch.json")
    save_json(english_data, english_file_path)
    save_json(deutsch_data, deutsch_file_path)

    return {
        "english": english_file_path,
        "deutsch": deutsch_file_path
    }

def create_parent_json(folder_path, child_files):
    """
    Creates a parent JSON file that references its child files.
    """
    parent_data = {}
    for language, file_path in child_files.items():
        # Store relative paths to child files
        parent_data[language] = os.path.relpath(file_path, folder_path)

    parent_file_path = os.path.join(folder_path, "parent.json")
    save_json(parent_data, parent_file_path)
    return parent_file_path

def create_root_json(output_base, parent_files, language):
    """
    Creates a root JSON file for a specific language that imports all parent files.
    """
    root_data = {}
    for sheet_name, parent_file in parent_files.items():
        # Get the relative path to the parent file
        relative_path = os.path.relpath(parent_file, output_base)
        root_data[sheet_name] = os.path.join(relative_path, f"{language}.json")

    root_file_path = os.path.join(output_base, f"{language}.json")
    save_json(root_data, root_file_path)
    print(f"{language.capitalize()} root file created: {root_file_path}")

def excel_to_json_folder(excel_path, output_base, tree_structure):
    """
    Reads an Excel file, processes each sheet, and saves data as a tree structure.
    """
    # Read all sheets
    sheets = pd.read_excel(excel_path, sheet_name=None)

    parent_files = {}

    for sheet_name, data in sheets.items():
        # Check for required columns
        if 'english' not in data.columns or 'deutsch' not in data.columns:
            print(f"Skipping sheet '{sheet_name}' due to missing required columns.")
            continue

        # Determine folder structure from tree_structure mapping
        folder_path = tree_structure.get(sheet_name, sheet_name)
        full_path = create_folder_structure(output_base, folder_path)

        # Create child files (English and Deutsch)
        child_files = sheet_to_child_files(sheet_name, data, full_path)

        # Create a parent file that references child files
        parent_file_path = create_parent_json(full_path, child_files)
        parent_files[sheet_name] = parent_file_path

    # Create separate root files for each language
    for language in ["english", "deutsch"]:
        create_root_json(output_base, parent_files, language)

# Example Tree Structure Mapping
tree_structure = {
    "greetings": "language/phrases/greetings",
    "farewells": "language/phrases/farewells",
    "numbers": "language/concepts/numbers",
    # Add more mappings as needed
}

# Example usage
excel_file_path = "translation.xlsx"
output_folder = "./output"
excel_to_json_folder(excel_file_path, output_folder, tree_structure)
