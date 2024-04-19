import pandas as pd
import json
import PySimpleGUI as sg
from pandas import json_normalize
from pathlib import Path

# p = Path(r'c:/Users/DV0095/Documents/Python_Projects/JSON_to_CSV/JSON_FILES/Google_JSON.json') #JSON file Path/Directory

# with p.open('r', encoding='utf-8') as f:
    # data = json.load(f) #reads the JSON file

def main():
    sg.theme('PythonPlus')

    layout = [[sg.T("")],
                [sg.Text("Upload the JSON version of the Interpretation File: "), sg.Input(key="file_path"), sg.FileBrowse(key="file_path_browse")],
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


    json_file_interp = json.load(open(json_file))


    def add_definitions_key(interp):
        outcomes = interp['outcomes']
        for outcome in outcomes:
            if 'definitions' not in outcome and 'attributes' in outcome:
                attributes = outcome.get('attributes', {})
                conditions = outcome.get('conditions', [])
                outcome['definitions'] = [
                    {
                        'attributes': attributes,
                        'conditions': conditions
                    }
                ]
            if 'definitions' not in outcome and 'attributes' in outcome:
                attributes = outcome.get('attributes', {})
                outcome['definitions'] = [
                    {
                        'attributes': attributes
                    }
                ]
            if 'definitions' not in outcome and 'conditions' in outcome:
                conditions = outcome.get('conditions', [])
                outcome['definitions'] = [
                    {
                        'conditions': conditions
                    }
                ]
                outcome.pop('attributes', None)  # Remove 'attributes' key
                outcome.pop('conditions', None)  # Remove 'conditions' key
        return interp

    data = add_definitions_key(json_file_interp)

    df = pd.json_normalize(data['outcomes'], meta = ['name'], record_path=['definitions']) #flattens JSON data into a dataframe. Most notably flattens the ['definitions'] dictionary in the JSON file. Turns out all cwi's need 'definitions'
    df.fillna('', inplace=True) #removes all NaN values in the csv file/helps clear empty spaces when combining column strings. The difference between null and ''.


    if any(col.startswith('variables.') for col in df.columns):
        variables_cols = [col for col in df.columns if col.startswith('variables.')]
        df['combined_variables'] = df[variables_cols].apply(lambda row: '\n'.join(f"{col.split('.')[1]}: {value}" for col, value in row.iteritems() if value != ''), axis=1)
        df = df.drop(variables_cols, axis=1)
        pass
    else:
        # No 'variables.' columns exist
        pass

    if any(col.startswith('attributes.') for col in df.columns):
        #df= df.drop('attributes.quantity.type')
        attributes_cols = [col for col in df.columns if col.startswith('attributes.') and col != 'attributes.quantity.type']
        df['combined_attributes'] = df[attributes_cols].apply(lambda row: '\n'.join(f"{col.split('.')[1]}: {value}" for col, value in row.iteritems() if value != ''), axis=1)
        df = df.drop(attributes_cols, axis=1)# Drop original 'attributes.' columns
        pass
    else: 
        pass


    #df['combined_attributes'] = df.apply(lambda row: '\n'.join(f"{key.split('.')[1]}: {value}" for key, value in row.iteritems() if key.startswith('attributes.') and value != ''), axis=1)
    #drop any unneeded columns. Possibly contingent on the tree JSON file
    #df.drop(['attributes.quantity.question','attributes.quantity','attributes.quantity.operation','attributes.quantity.args'], axis=1, inplace=True)

    ### Organization ###
    if any(col.startswith('combined_variables') for col in df.columns):
    # Define the desired column order
        column_order = ['name','combined_variables', 'combined_attributes', 'conditions'] #column order may be contingent on the tree JSON file
    # Reorder the columns using reindex
        df = df.reindex(columns=column_order)
    # change the names of any of the columns *must be in the order layout above*
        df.columns = ['CWI_UNIT Names', 'Variables', 'Attributes', 'Conditions']
        df.reset_index(drop=True, inplace=True)
    else: 
        column_order = ['name', 'combined_attributes', 'conditions'] #column order may be contingent on the tree JSON file
        df = df.reindex(columns=column_order)
        df.columns = ['CWI_UNIT Names', 'Attributes', 'Conditions']
        df.reset_index(drop=True, inplace=True)

    #### Remove extra cwi names ####
    df.loc[(df['CWI_UNIT Names'].duplicated()) & (df['CWI_UNIT Names'] != 'UNIT_CODE'), 'CWI_UNIT Names'] = ''



    # print new csv file and use Tree interp name for organization.
    df.to_csv('ANSCO_ATT_SVA_Tree.csv') #NAME THE FILE TO THE TREE YOU ARE USING. Contructs and saves the data frame into a csv file. Must have a directory location in terminal.
    #print(df)  ##prints a view of what the data frame will look like. View/Spawns/Populates in terminal, might not be all of the info if JSON file is large.

if __name__=='__main__':
    main()




#### 1) remove index column 1.1) SUCCESS! hide unused columns 
# df.index.name = 'Index'

#### 2) remove row duplicates/remove row indecies (mainly for cwi_names) 
#### 3) SUCCESS! DONE! combine the quantity.operations and args columns in ['quantity']
#### 4) SUCCESS! move column values so that it is more organized. IE. cwi_name, attributes, conditions.
#### 5) maybe skip lines so the information is not so bunched??

# SUCCESS all keys need a definitons value!! Fix when you have the time. Fixed with the function.
