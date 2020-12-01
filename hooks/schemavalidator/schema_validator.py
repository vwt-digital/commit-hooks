#!/usr/bin/python3

import sys
import json
import argparse
from io import StringIO
from functools import reduce
import operator
import jsonschema


def validate_schema(schema_file_name, schema, schema_folder_path):
    meta_data_schema_uri = schema['$schema']
    if 'http' in meta_data_schema_uri:
        # Find schema via its URL locally
        meta_data_file_name = meta_data_schema_uri.replace("://", "_")
    elif 'tag' in meta_data_schema_uri:
        # Find schema via its tag locally
        meta_data_file_name = meta_data_schema_uri.replace("tag:", "tag_")
        meta_data_file_name = meta_data_schema_uri.replace(":", "_")
    else:
        print('Cannot validate schema because no meta_data schema is' +
              ' found in the folder where the schema can be found.')
        sys.exit(1)
    # Check if the path to the schema exists in the schemas folder
    meta_data_file_name = meta_data_file_name.replace("/", "_")
    meta_data_schema_path = schema_folder_path + "/" + meta_data_file_name + ".json"
    try:
        with open(meta_data_schema_path, 'r') as f:
            meta_data_schema = json.load(f)
        # Also fill in references if they occur in the meta data schema
        meta_data_schema = fill_refs(meta_data_schema, schema_folder_path)
    except Exception:
        schema_id = schema.get('$id')
        if schema_id:
            print("Could not validate schema agains meta schema because could not find meta schema {}".format(meta_data_file_name) +
                  " , it should be in the same folder as the schema {}".format(schema_id))
        else:
            print("The schema {} does not have an ID field".format(schema_file_name))
        sys.exit(1)
    # Validate the schema agains the meta data schema
    try:
        jsonschema.validate(schema, meta_data_schema)
    except Exception as e:
        print("Schema is not conform meta data schema" +
              " because of {}".format(e))
        sys.exit(1)
    return True


def fill_refs(schema, schema_folder_path):
    schema_json = schema
    new_schema = StringIO()
    schema = json.dumps(schema, indent=2)
    # Make schema into list so that every newline can be printed
    schema_list = schema.split('\n')
    for line in schema_list:
        if '$ref' in line:
            # If a '#' is in the reference, it's a reference to a definition
            if '#' in line:
                if '"$ref": "' in line:
                    line_array_def = line.split('"$ref": "')
                elif '"$ref" : "' in line:
                    line_array_def = line.split('"$ref" : "')
                else:
                    line_array_def = ''
                ref_def = line_array_def[1].replace('\"', '')
                # If the reference is only '#'
                if ref_def == '#':
                    # Just write it to the stringio file
                    new_schema.write(line)
                else:
                    # Check if there is a URI in front of the '#'
                    # Because then the definition is in another schema
                    comma_at_end = False
                    if 'tag' in ref_def or 'http' in ref_def:
                        # Split on the '#/'
                        ref_def_array = ref_def.split("#/")
                        uri_part = ref_def_array[0]
                        def_part = ref_def_array[1]
                        if def_part[-1] == ',':
                            def_part = def_part[:-1]
                            comma_at_end = True
                        # Get filename
                        if 'http' in uri_part:
                            # Find schema via its URL locally
                            schema_file_name = uri_part.replace("://", "_")
                        elif 'tag' in uri_part:
                            # Find schema via its tag locally
                            schema_file_name = uri_part.replace("tag:", "tag_")
                            schema_file_name = uri_part.replace(":", "_")
                        else:
                            print("Reference is not a http(s) or tag as uri")
                            sys.exit(1)
                        schema_file_name = schema_file_name.replace('/', '_')
                        if (not schema_file_name.endswith('.json')):
                            schema_file_name = schema_file_name + '.json'
                        ref_def_schema_path = schema_folder_path + "/" + schema_file_name.replace(',', '')
                        try:
                            with open(ref_def_schema_path, 'r') as f:
                                reference_schema_def = json.load(f)
                        except Exception as e:
                            print("Schema of reference to definition cannot be openend " +
                                  "because of {}".format(e))
                    else:
                        # Reference to definition is in this schema
                        # Split on the '#/'
                        ref_def_array = ref_def.split("#/")
                        def_part = ref_def_array[1]
                        # If there's a comma at the end
                        if def_part[-1] == ',':
                            def_part = def_part[:-1]
                            comma_at_end = True
                        reference_schema_def = schema_json
                    # Now find key in json where the reference is defined
                    def_part_array = def_part.split('/')
                    def_from_dict = getFromDict(reference_schema_def, def_part_array)
                    # If type of definition reference is dict
                    if type(def_from_dict) is dict:
                        # put reference in stringio file
                        def_from_dict_txt = json.dumps(def_from_dict, indent=2)
                        def_from_dict_list = def_from_dict_txt.split('\n')
                        for i in range(len(def_from_dict_list)):
                            # Do not add the beginning '{' and '}'
                            if i != 0 and i != (len(def_from_dict_list)-1):
                                line_to_write = def_from_dict_list[i]
                                # Write the reference schema to the stringio file
                                if i == len(def_from_dict_list)-2 and comma_at_end:
                                    line_to_write = "{},".format(line_to_write)
                                new_schema.write(line_to_write)
                    else:
                        print("Definition should be dict")
            # If reference is an URL
            elif 'http' in line:
                if '"$ref": "' in line:
                    line_array = line.split('"$ref": "')
                elif '"$ref" : "' in line:
                    line_array = line.split('"$ref" : "')
                else:
                    line_array = ''
                ref = line_array[1].replace('\"', '')
                # Find schema via its URL locally
                meta_data_file_name = ref.replace("://", "_")
                # If file does not have .json as extension
                if(not meta_data_file_name.endswith('.json')):
                    meta_data_file_name = meta_data_file_name + ".json"
                # Fill reference
                new_schema = fill_from_local_schema(new_schema, schema_folder_path, ref, meta_data_file_name)
            # If reference is a tag
            elif 'tag' in line:
                if '"$ref": "' in line:
                    line_array = line.split('"$ref": "')
                elif '"$ref" : "' in line:
                    line_array = line.split('"$ref" : "')
                else:
                    line_array = ''
                ref = line_array[1].replace('\"', '')
                # Find schema via its tag locally
                meta_data_file_name = ref.replace("tag:", "tag_")
                meta_data_file_name = ref.replace(":", "_")
                # Fill reference
                new_schema = fill_from_local_schema(new_schema, schema_folder_path, ref, meta_data_file_name)
            else:
                # If the line does not contain any tag references
                # Just write it to the stringio file
                new_schema.write(line)
        else:
            # If the line does not contain any references
            # Just write it to the stringio file
            new_schema.write(line)
    contents = new_schema.getvalue()
    new_schema = json.loads(contents)
    return new_schema


def fill_from_local_schema(new_schema, schema_folder_path, meta_data_uri, meta_data_file_name):
    # Replace /
    meta_data_file_name = meta_data_file_name.replace("/", "_")
    # Path to schema
    ref_schema_path = schema_folder_path + "/" + meta_data_file_name
    # Check if the path to the schema exists in the schemas folder
    try:
        with open(ref_schema_path, 'r') as f:
            reference_schema = json.load(f)
    except Exception as e:
        print("The schema reference in path {} could not be opened because of {}".format(ref_schema_path, e))
        sys.exit(1)
    try:
        # Also fill in references if they occur in the reference schema
        reference_schema = fill_refs(reference_schema, schema_folder_path)
    except Exception as e:
        print("The references in schema with path {} ".format(ref_schema_path) +
              "could not be filled because of {}".format(e))
        sys.exit(1)
    else:
        # Double check if the uri of the schema is the same as the
        # one of the reference
        if '$id' in reference_schema:
            if reference_schema['$id'] == meta_data_uri:
                # Add the schema to the new schema
                reference_schema_txt = json.dumps(reference_schema, indent=2)
                reference_schema_list = reference_schema_txt.split('\n')
                for i in range(len(reference_schema_list)):
                    # Do not add the beginning '{' and '}'
                    if i != 0 and i != (len(reference_schema_list)-1):
                        # Write the reference schema to the stringio file
                        new_schema.write(reference_schema_list[i])
            else:
                print("ID of reference is {} while ".format(meta_data_uri) +
                      "that of the schema is {}".format(reference_schema['$id']))
                sys.exit(1)
        else:
            print("Reference schema of reference {} has no ID".format(meta_data_uri))
            sys.exit(1)
    return new_schema


# This function traverses the dictionary and gets the value of a key from a list of attributes
def getFromDict(dataDict, mapList):
    return reduce(operator.getitem, mapList, dataDict)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-jf', '--json-file', required=True)
    args = parser.parse_args()
    file_name = args.json_file
    # Get file name of json
    json_file_name = file_name.split("/")[-1]
    # Open json that needs to be verified
    try:
        with open(args.json_file, 'r') as f:
            json_file = json.load(f)
    except Exception as e:
        print("Exception occured when trying to open json, reason {}".format(e))
        sys.exit(1)
    if '$schema' in json_file:
        # Get folder where json file is from
        original_folder = file_name.replace(json_file_name, '')
        if original_folder:
            if validate_schema(json_file_name, json_file, original_folder) is False:
                sys.exit(1)
        else:
            print("Folder of meta schema cannot be found")
            sys.exit(1)
