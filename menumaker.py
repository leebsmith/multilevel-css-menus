#!/usr/bin/python3

import sys
import json
import click
from json.decoder import JSONDecodeError

indent = 0

# Leaves MUST contain 'text' and 'href' keys.
# Leaves MAY contain 'id' and / or 'class_list' keys.
# 'id', 'text', and 'href' must be strings. 'class_list' must be list
# Returns None if the node IS a leaf
def isLeaf(node):

    types = {
        "id" : str,
        "href" : str,
        "class_list": list,
        "text": str,
    }

    if not isinstance(node, dict):
        return (f'{node} isn\'t a dict.')

    keyset = node.keys()

    # Insure all keys that are present are allowed
    for key in keyset:
        if not key in types.keys():
            return (f'Key "{key}" isn\'t allowed in {node}.')

    # Insure that all required keys are present
    for key in {'text', 'href'}:
        if not key in keyset:
            return (f'Required key "{key}" not found in {node}.')

    # Insure values are correct type
    for keys in keyset:
        if not isinstance(node[key], types[key]):
            return (f'{key} must be a/an {types[key]} in {node}.')

    return None

# Parents MUST contain 'text' and 'nodes' keys.
# Parents MAY contain 'id' and / or 'class_list' keys.
# 'text' and 'id' must be str and 'nodes' and 'class_list' must be lists
# Returns None if the node is a parent
def isParent(node):

    types = {
        "text": str,
        "nodes": list,
        "id": str,
        "class_list": list
    }

    keyset = node.keys()

    # Insure all keys that are present are allowed
    for key in keyset:
        if not key in types.keys():
            return (f'Key "{key}" isn\'t allowed in {node}.')

    # Insure that all required keys are present
    for key in {'text', 'nodes'}:
        if not key in keyset:
            return (f'Required key "{key}" not found in {node}.')

    # Insure values are correct type
    for keys in keyset:
        if not isinstance(node[key], types[key]):
            return (f'{key} must be a/an {types[key]} in {node}.')

    return None

# Guarantees that the JSON structure consists
# of only valid leaves and parents
def validJSON(json):

    leafMsg = isLeaf(json)
    parentMsg = isParent(json)

    # Impossible case. Node is a leaf and a parent
    if (leafMsg == None and parentMsg == None):
        print("Internal error.")
        return False

    # Error case: node is not a leaf and node is not a parent
    if (leafMsg != None and parentMsg != None):
        print(f'Attempting to parse as a leaf: {leafMsg}')
        print(f'Attempting to parse as a parent: {parentMsg}')
        return False

    # Normal case: leafMsg == None OR parentMsg == None

    # Leaf?
    if leafMsg == None:
        return True

    # Parent!
    else:
        for node in json['nodes']:
            if not validJSON(node):
                return False

        return True

def makeMenu(json):
    global indent

    def makeAnchor(txt, class_list, idstr=None, href=None):
       
        classes = class_list and " ".join(class_list)
        cls = f' class="{classes}"' if classes else ''
        href = f' href="{href}"' if href else ''
        idstr = f' id="{idstr}"' if idstr else ''
        html = f'<a{cls}{idstr}{href}>{txt}</a>'
        return html
    
    # Leaf?
    if isLeaf(json) == None:
        indent += 1
        # id string and class_list possible
        cls_list = None if 'class_list' not in json.keys() else \
            json['class_list']
        idstr = None if 'id' not in json.keys() else \
            json['id']
        printWithIndent(makeAnchor(json['text'],
            cls_list,
            idstr,
            json['href']))
        indent -= 1

    # Parent!
    else:
        arrowClass = [] if indent < 3 else \
            (['downarrow'] if indent == 3 else  ['rightarrow'])
        
        # id string and class_list possible
        cls_list = [] if 'class_list' not in json.keys() else \
            json['class_list']

        classes = arrowClass + cls_list

        idstr = None if 'id' not in json.keys() else \
            json['id']
        printWithIndent(makeAnchor(json['text'],classes, idstr))
        printWithIndent('<ul>')
        indent += 1

        for node in json['nodes']:
            printWithIndent('<li>')
            indent += 1
            
            makeMenu(node)
            
            indent -= 1
            printWithIndent('</li>')

        indent -= 1
        printWithIndent('</ul>')
        

def printWithIndent(str):
    global indent
    leadingTabs = "\t" * indent;
    print(f'{leadingTabs}{str}')

def wrapWithNav(json):
    global indent
    printWithIndent("<nav id='nav'>")
    indent += 1

    makeMenu(json)

    indent -= 1
    printWithIndent("</nav>")

@click.command()
@click.argument('filename', type=click.Path(exists=True, dir_okay=False))
def printMenu(filename):

    try:    
        with open(filename) as f:
            data = json.load(f)
    
    except JSONDecodeError as e:
        print(e)
        sys.exit(1)

    except TypeError as e:
        print(e)
        sys.exit(1)

    if not validJSON(data):
        print('Not a valid JSON menu.')
        sys.exit(1)

    wrapWithNav(data)

printMenu()
