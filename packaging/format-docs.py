#!/usr/bin/env python3
# Copyright 2007-2022 The OpenRA Developers (see AUTHORS)
# This file is part of OpenRA, which is free software. It is made
# available to you under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version. For more
# information, see COPYING.

import io
import sys
import json
from collections import OrderedDict

def format_type_name(typeName, isKnownType):
    name = typeName
    if name.endswith("Info"):
        name = name[0:-4]

    return f'[`{name}`](#{name.lower()})' if isKnownType else f'`{name}`'

def is_known_type(typeName, types):
    name = typeName
    if name.endswith("Info"):
        name = name[0:-4]

    result = [t for t in types if name == t["Name"]]
    return len(result) > 0

def format_docs(version, collectionName, types):
    typesByNamespace = OrderedDict()
    for currentType in types:
        if currentType["Namespace"] in typesByNamespace:
            typesByNamespace[currentType["Namespace"]].append(currentType)
        else:
            typesByNamespace[currentType["Namespace"]] = [currentType]

    explanation = ""
    if collectionName == "TraitInfos":
        explanation = "all traits with their properties and their default values plus developer commentary"
    elif collectionName == "WeaponTypes":
        explanation = "a template for weapon definitions and the types it can use (warheads and projectiles) with default values and developer commentary"
    elif collectionName == "SequenceTypes":
        explanation = "all sequence types with their properties and their default values plus developer commentary"

    print(f"This documentation is aimed at modders and has been automatically generated for version `{version}` of OpenRA. " +
				"Please do not edit it directly, but instead add new `[Desc(\"String\")]` tags to the source code.\n")

    print(f"Listed below are {explanation}.")

    for namespace in typesByNamespace:
        print(f'\n## {namespace}')

        for currentType in typesByNamespace[namespace]:
            print(f'\n### {currentType["Name"]}')

            if currentType["Description"]:
                print(f'**{currentType["Description"]}**')

            if "InheritedTypes" in currentType and currentType["InheritedTypes"]:
                inheritedTypes = [t for t in currentType["InheritedTypes"] if t not in ['TraitInfo', 'Warhead']] # Remove blacklisted types.
                if inheritedTypes:
                    print("###### Inherits from: " + ", ".join([format_type_name(x, is_known_type(x, types)) for x in inheritedTypes]) + '.')

            if "RequiresTraits" in currentType and currentType["RequiresTraits"]:
                print("###### Requires trait(s): " + ", ".join([format_type_name(x, is_known_type(x, types)) for x in currentType["RequiresTraits"]]) + '.')

            if len(currentType["Properties"]) > 0:
                print()
                print(f'| Property | Default Value | Type | Description |')
                print(f'| -------- | ------------- | ---- | ----------- |')

                for prop in currentType["Properties"]:
                    if "OtherAttributes" in prop:
                        attributes = []
                        for attribute in prop["OtherAttributes"]:
                            attributes.append(attribute["Name"])

                        defaultValue = ''
                        if prop["DefaultValue"]:
                            defaultValue = prop["DefaultValue"]
                        elif 'Require' in attributes:
                            defaultValue = '*(required)*'

                        print(f'| {prop["PropertyName"]} | {defaultValue} | {prop["UserFriendlyType"]} | {prop["Description"]} |')
                    else:
                        print(f'| {prop["PropertyName"]} | {prop["DefaultValue"]} | {prop["UserFriendlyType"]} | {prop["Description"]} |')

if __name__ == "__main__":
    input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8-sig')
    jsonInfo = json.load(input_stream)

    keys = list(jsonInfo)
    if len(keys) == 2 and keys[0] == 'Version':
        format_docs(jsonInfo[keys[0]], keys[1], jsonInfo[keys[1]])
