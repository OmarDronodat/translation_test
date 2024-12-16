import pandas as pd
import os

def create_folder_structure(base_path, folder_path):
    """
    Creates a nested folder structure if it doesn't exist.
    """
    full_path = os.path.join(base_path, folder_path)
    os.makedirs(full_path, exist_ok=True)
    return full_path

def save_js(data, file_path):
    """
    Saves a dictionary as a JavaScript file that exports the data.
    """
    js_content = f"export default {data};\n"
    with open(file_path, 'w', encoding='utf-8') as js_file:
        js_file.write(js_content)

def sheet_to_child_files(sheet_name, data, folder_path):
    """
    Creates two JavaScript files (English and Deutsch) for a given sheet and folder path.
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

    # Save English and Deutsch JS files
    english_file_path = os.path.join(folder_path, f"{sheet_name}_english.js")
    deutsch_file_path = os.path.join(folder_path, f"{sheet_name}_deutsch.js")
    save_js(english_data, english_file_path)
    save_js(deutsch_data, deutsch_file_path)

    return {
        "english": english_file_path,
        "deutsch": deutsch_file_path
    }

def create_parent_js(folder_path, child_files):
    """
    Creates a parent JS file that imports and exports its child files.
    """
    parent_js_path = os.path.join(folder_path, "parent.js")

    # Generate import statements and prepare the export object
    imports = []
    export_object = []

    for language, file_path in child_files.items():
        variable_name = f"{language}_data"
        relative_path = os.path.relpath(file_path, folder_path).replace("\\", "/")
        imports.append(f"import {variable_name} from './{os.path.basename(relative_path)}';")
        export_object.append(f"{language}: {variable_name}")

    # Write the final content to the file
    with open(parent_js_path, 'w', encoding='utf-8') as js_file:
        js_file.write("\n".join(imports) + "\n\n")
        js_file.write(f"export default {{\n    {',\n    '.join(export_object)}\n}};\n")

    return parent_js_path




def create_root_js(output_base, parent_files, language):
    """
    Creates a root JS file for a specific language that imports and exports all parent files.
    """
    root_js_path = os.path.join(output_base, f"{language}.js")

    # Generate import and export statements
    imports = []
    export_entries = []
    for sheet_name, parent_file in parent_files.items():
        variable_name = f"{sheet_name}_data"
        relative_path = os.path.relpath(parent_file, output_base).replace("\\", "/")
        imports.append(f"import {variable_name} from './{relative_path}';")
        export_entries.append(f"{sheet_name}: {variable_name}.{language}")

    # Write imports and exports to the root file
    with open(root_js_path, 'w', encoding='utf-8') as js_file:
        js_file.write("\n".join(imports) + "\n\n")
        js_file.write(f"export default {{\n    {',\n    '.join(export_entries)}\n}};\n")

    print(f"{language.capitalize()} root file created: {root_js_path}")


def excel_to_js_folder(excel_path, output_base, tree_structure):
    """
    Reads an Excel file, processes each sheet, and saves data as a JavaScript structure.
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
        parent_js_path = create_parent_js(full_path, child_files)
        parent_files[sheet_name] = parent_js_path

    # Create separate root files for each language
    for language in ["english", "deutsch"]:
        create_root_js(output_base, parent_files, language)

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
excel_to_js_folder(excel_file_path, output_folder, tree_structure)
