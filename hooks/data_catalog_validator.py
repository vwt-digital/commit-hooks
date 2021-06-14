import argparse
import json
import sys
from datetime import datetime

import jsondiff


def compare_with_old_file(json_file_old, json_file_new, file_name_new):
    # Compare differences between old json and new json
    diff_json = jsondiff.diff(json_file_old, json_file_new)
    # Get keys of object that is different now
    diff_json_keys = list(diff_json.keys())
    # Check if first key is dataset
    if diff_json_keys[0] != "dataset":
        print(
            "INFO: Difference between old file {} on Git and new local one is not in a dataset".format(
                file_name_new
            )
        )
        sys.exit(0)
    diff_json_first_obj = diff_json["dataset"]
    diff_json_first_obj_keys = list(diff_json_first_obj.keys())
    dataset_nrs = []
    # For every key that is changed
    for dataset_key in diff_json_first_obj_keys:
        # If the key is an integer
        if isinstance(dataset_key, int):
            # Add it to the list of dataset numbers that has been changed
            dataset_nrs.append(dataset_key)
        # If it is a jsondiff symbol
        elif isinstance(dataset_key, jsondiff.symbols.Symbol):
            # Get changes
            changes = diff_json_first_obj[dataset_key]
            if isinstance(changes, list):
                for change in changes:
                    # Check if change is tuple
                    dataset_nrs = check_change(change, dataset_nrs)
            else:
                print(
                    "INFO: changes computed from file {} are not a list, consider updating data catalog validator".format(
                        file_name_new
                    )
                )
    # For every dataset number found
    for dataset_nr in dataset_nrs:
        dataset = json_file_new["dataset"][dataset_nr]
        check_dataset(dataset, file_name_new)


def check_change(change, dataset_nrs):
    if isinstance(change, tuple):
        # Get the dataset number
        dataset_nr = change[0]
        # Check if value is integer
        if isinstance(dataset_nr, int):
            # Add it to the list of dataset numbers that has been changed
            dataset_nrs.append(dataset_nr)
        else:
            print(
                "INFO: value in changes tuple in file {} is not integer, consider updating data catalog validator".format(
                    file_name_new
                )
            )
    elif isinstance(change, int):
        dataset_nr = change
    else:
        print(
            "INFO: value in changes list in file {} is not tuple or integer, consider updating data catalog validator".format(
                file_name_new
            )
        )
    return dataset_nrs


def qualified_relation_check(distribution, file_name):
    # Check if distribution contains the field "qualifiedRelation"
    qualifiedRelationDist = distribution.get("qualifiedRelation")
    if not qualifiedRelationDist:
        print(
            "ERROR: Dataset {} of file {} contains distribution {} that doet not contain the field 'qualifiedRelation'".format(
                dataset["identifier"], file_name, distribution["title"]
            )
        )
        print(
            "For more information see https://vwt-digital.github.io/project-company-data.github.io/v1.1/schema/#qualifiedRelation"
        )
        sys.exit(1)
    for qrd in qualifiedRelationDist:
        hadRoleDist = qrd.get("hadRole")
        if not hadRoleDist:
            print(
                "ERROR: Dataset {} of file {} contains a 'qualifiedRelation' in distribution {}".format(
                    dataset["identifier"], file_name, distribution["title"]
                )
                + " that does not contain the field 'hadRole'"
            )
            print(
                "For more information see https://vwt-digital.github.io/project-company-data.github.io/v1.1/schema/#qualifiedRelation"
            )
            sys.exit(1)
        relationDist = qrd.get("relation")
        if not relationDist:
            print(
                "ERROR: Dataset {} of file {} contains a 'qualifiedRelation' in distribution {}".format(
                    dataset["identifier"], file_name, distribution["title"]
                )
                + " that does not contain the field 'relation'"
            )
            print(
                "For more information see https://vwt-digital.github.io/project-company-data.github.io/v1.1/schema/#qualifiedRelation"
            )
            sys.exit(1)


def lifespan_check(distribution, file_name):
    topic_ended = False
    # Check if topic distribution contains the field "lifespan"
    if distribution.get("format") == "topic":
        lifespanDist = distribution.get("lifespan")
        if not lifespanDist:
            print(
                "ERROR: Dataset {} of file {} contains distribution {} that doet not contain the field 'lifespan'".format(
                    dataset["identifier"], file_name, distribution["title"]
                )
            )
            print(
                "For more information see https://vwt-digital.github.io/project-company-data.github.io/v1.1/schema/#distribution-lifespan"
            )
            sys.exit(1)
        startDateDist = lifespanDist.get("startDate")
        if not startDateDist:
            print(
                "ERROR: Dataset {} of file {} contains a 'lifespan' in distribution {}".format(
                    dataset["identifier"], file_name, distribution["title"]
                )
                + " that does not contain the field 'startDate'"
            )
            print(
                "For more information see https://vwt-digital.github.io/project-company-data.github.io/v1.1/schema/#distribution-lifespan"
            )
            sys.exit(1)
        endDateDist = lifespanDist.get("endDate")
        if endDateDist:
            past = datetime.strptime(endDateDist, "%Y-%m-%d")
            present = datetime.now()
            check_date = past.date() <= present.date()
            if check_date is False:
                topic_ended = True
    return topic_ended


def check_dataset(dataset, file_name):
    # Check if dataset contains field "qualifiedRelation"
    check_qualifiedrelation_dataset(dataset, file_name)
    # Check if dataset contains a distribution
    distributions = dataset.get("distribution")
    if not distributions:
        print(
            "INFO: Dataset in data catalog that contains changes does not have a distribution"
        )
        sys.exit(0)
    # Check distributions
    format_list = []
    for distribution in distributions:
        format_list.append(distribution.get("format"))
        qualified_relation_check(distribution, file_name)
        topic_ended = lifespan_check(distribution, file_name)
    # Check if distribution list contains subscriptions but no topics
    if "subscription" in format_list:
        if "topic" not in format_list:
            print(
                "ERROR: Dataset {} of file {} contains a subscription in the distribution list but no topic".format(
                    dataset["identifier"], file_name
                )
            )
            sys.exit(1)
        if topic_ended:
            print(
                "ERROR: Dataset {} of file {} contains a subscription in the distribution list but topic has an end date of today"
                " or before today".format(dataset["identifier"], file_name)
            )
            sys.exit(1)


def check_qualifiedrelation_dataset(dataset, file_name):
    qualifiedRelation = dataset.get("qualifiedRelation")
    if not qualifiedRelation:
        print(
            "ERROR: Dataset {} in file {} doet not contain field 'qualifiedRelation'".format(
                dataset["identifier"], file_name
            )
        )
        print(
            "For more information see https://vwt-digital.github.io/project-company-data.github.io/v1.1/schema/#qualifiedRelation"
        )
        sys.exit(1)
    for qr in qualifiedRelation:
        hadRole = qr.get("hadRole")
        if not hadRole:
            print(
                "ERROR: A 'qualifiedRelation' in dataset {} of file {} does not contain field 'hadRole'".format(
                    dataset["identifier"], file_name
                )
            )
            print(
                "For more information see https://vwt-digital.github.io/project-company-data.github.io/v1.1/schema/#qualifiedRelation"
            )
            sys.exit(1)
        relation = qr.get("relation")
        if not relation:
            print(
                "ERROR: A 'qualifiedRelation' in dataset {} of file {} does not contain field 'relation'".format(
                    dataset["identifier"], file_name
                )
            )
            print(
                "For more information see https://vwt-digital.github.io/project-company-data.github.io/v1.1/schema/#qualifiedRelation"
            )
            sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-jfo", "--json-file-old", required=False)
    parser.add_argument("-jfn", "--json-file-new", required=True)
    args = parser.parse_args()
    compare = False
    if args.json_file_old:
        file_name_old = args.json_file_old
        # Get file name of old json
        json_file_name_old = file_name_old.split("/")[-1]
        # Open old json
        try:
            with open(file_name_old, "r") as f:
                json_file_old = json.load(f)
        except Exception as e:
            print(
                "ERROR: Exception occured when trying to open json {}, reason {}".format(
                    file_name_old, e
                )
            )
            sys.exit(1)
        compare = True
    file_name_new = args.json_file_new
    # Get file name of new json
    json_file_name_new = file_name_new.split("/")[-1]
    # Open new json
    try:
        with open(file_name_new, "r") as f:
            json_file_new = json.load(f)
    except Exception as e:
        print(
            "ERROR: Exception occured when trying to open json {}, reason {}".format(
                file_name_old, e
            )
        )
        sys.exit(1)
    # Check if new file has "dataset" as field
    if not json_file_new.get("dataset"):
        print(
            "INFO: JSON file {} does not contain field 'dataset'".format(file_name_new)
        )
        sys.exit(0)
    # Check if have to compare to old file or if it is a new file
    if compare:
        compare_with_old_file(json_file_old, json_file_new, file_name_new)
    else:
        for dataset in json_file_new["dataset"]:
            check_dataset(dataset, file_name_new)
