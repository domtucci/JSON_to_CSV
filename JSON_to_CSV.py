import pandas as pd
import numpy as np
import json
import PySimpleGUI as sg
from pandas import json_normalize
from pathlib import Path
from itertools import chain
import argparse


# p = Path(r'c:/Users/DV0095/Documents/Python_Projects/JSON_to_CSV/JSON_FILES/Google_JSON.json') #JSON file Path/Directory

# with p.open('r', encoding='utf-8') as f:
    # data = json.load(f) #reads the JSON file

def main(): #GUI Window
    parser = argparse.ArgumentParser(description="Destinguish between GUI and command line")
    parser.add_argument("-v", "--pysimple", action="store_true", help="Use the GUI if you have PySimpleGUI")
    parser.add_argument("-c", "--command", type=str, help="Specify the JSON file path for command line mode")
    args = parser.parse_args()

    if args.pysimple:
        
        sg.theme('PythonPlus')

        layout = [[sg.T("")],
                    [sg.Text("Upload the downloaded Tree Dialogue JSON File: "), sg.Input(key="file_path"), sg.FileBrowse(key="file_path_browse")],
                    [sg.T("")],
                    [sg.Button("Submit", bind_return_key=True), sg.Button('Cancel')]]

        window = sg.Window('Main Menu', layout, size=(800, 180))

        while True:
            event, values = window.Read()
            if event == sg.WIN_CLOSED or event == 'Cancel':
                break
            elif event == 'Submit':
                json_file = values['file_path']
                window.close()

        data = json.load(open(json_file))

    elif args.command:

        p = Path(r'c:\Users\DV0095\Downloads\20250304141748.json') #JSON file Path/Directory
        # Read the JSON file
        with p.open('r', encoding='utf-8') as file:

            data = json.load(file)


    # def add_definitions_key(interp):
    #     outcomes = interp['outcomes']
    #     for outcome in outcomes:
    #         if 'definitions' not in outcome and 'attributes' in outcome:
    #             attributes = outcome.get('attributes', {})
    #             conditions = outcome.get('conditions', [])
    #             outcome['definitions'] = [
    #                 {
    #                     'attributes': attributes,
    #                     'conditions': conditions
    #                 }
    #             ]
    #         if 'definitions' not in outcome and 'attributes' in outcome:
    #             attributes = outcome.get('attributes', {})
    #             outcome['definitions'] = [
    #                 {
    #                     'attributes': attributes
    #                 }
    #             ]
    #         if 'definitions' not in outcome and 'conditions' in outcome:
    #             conditions = outcome.get('conditions', [])
    #             outcome['definitions'] = [
    #                 {
    #                     'conditions': conditions
    #                 }
    #             ]
    #         #outcome.pop('attributes', None)  # Remove 'attributes' key
    #         #outcome.pop('conditions', None)  # Remove 'conditions' key
    #     return interp

    # data = add_definitions_key(json_file_interp)


    df = pd.json_normalize(data['outcomes'], meta = ['name'])
    df.replace({pd.NA: '', np.nan: ''}, inplace=True)
    df_exploded = df.explode('definitions', ignore_index=True)

    # Extract 'attributes' and 'conditions' from each dictionary
    df_exploded['def-attributes'] = df_exploded['definitions'].apply(lambda x: x['attributes'] if isinstance(x, dict) and 'attributes' in x else None)
    df_exploded['def-conditions'] = df_exploded['definitions'].apply(lambda x: x['conditions'] if isinstance(x, dict) and 'conditions' in x else None)

    if any(col.startswith('variables.') for col in df_exploded.columns):
        variables_cols = [col for col in df_exploded.columns if col.startswith('variables.')]
        df_exploded['combined_variables'] = df_exploded[variables_cols].apply(lambda row: '\n'.join(f"{col.split('.')[1]}: {value}" for col, value in row.items() if value != ''), axis=1)
        df_exploded = df_exploded.drop(variables_cols, axis=1)
        pass
    else:
        # No 'variables.' columns exist
        pass

    if any(col.startswith('attributes.') for col in df_exploded.columns):

        attributes_cols = [col for col in df_exploded.columns if col.startswith('attributes.') and col != 'attributes.quantity.type']
        df_exploded['combined_attributes'] = df_exploded[attributes_cols].apply(lambda row: '\n'.join(f"{col.split('.')[1]}: {value}" for col, value in row.items() if value != ''), axis=1)
        df_exploded = df_exploded.drop(attributes_cols, axis=1)# Drop original 'attributes.' columns
        pass
    else: 
        pass

    ### Organization ###
    if any(col.startswith('combined_variables') for col in df_exploded.columns):
        column_order = ['name','combined_variables', 'combined_attributes', 'conditions', 'def-attributes', 'def-conditions'] #column order may be contingent on the tree JSON file
        df_exploded = df_exploded.reindex(columns=column_order)

        df_exploded.columns = ['CWI_UNIT Names', 'Variables', 'Attributes', 'Conditions', 'Def-Attributes', 'Def-Conditions']
        df_exploded.reset_index(drop=True, inplace=True)
    else: 
        column_order = ['name', 'combined_attributes', 'conditions', 'def-attributes', 'def-conditions'] #column order may be contingent on the tree JSON file
        df_exploded = df_exploded.reindex(columns=column_order)
        df_exploded.columns = ['CWI_UNIT Names', 'Attributes', 'Conditions', 'Def-Attributes', 'Def-Conditions']
        df_exploded.reset_index(drop=True, inplace=True)



    #### Remove extra cwi names ####
    #df.loc[(df['CWI_UNIT Names'].duplicated()) & (df['CWI_UNIT Names'] != 'UNIT_CODE'), 'CWI_UNIT Names'] = ''


    # print new csv file and use Tree interp name for organization.
    df_exploded.to_csv('Ubiquity_02_10_2025.csv')


    #print(df_exploded)  ##prints a view of what the data frame will look like. View/Spawns/Populates in terminal, might not be all of the info if JSON file is large.

if __name__=='__main__':
    main()

