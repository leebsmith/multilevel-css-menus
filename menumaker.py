#!/usr/bin/python3

import sys
import json
import click
from json.decoder import JSONDecodeError

indent = 0

def isLeaf(node):
    if not isinstance(node, dict):
        return False;

    # Test keys for number and matching content
    if set(node.keys()) != {'text','func'}:
        return False

    # Test keys for type
    keytypes = [
        isinstance(node['text'],str),
        isinstance(node['func'],str)
    ]

    return keytypes == [True, True]

def isParent(node):
    if not isinstance(node, dict):
        return False;

    # Test keys for number and matching content
    if set(node.keys()) != {'text','nodes'}:
        return False

    # Test keys for type
    keytypes = [
        isinstance(node['text'],str),
        isinstance(node['nodes'],list)
    ]

    return keytypes == [True, True]

# Guarantees that the JSON structure consists
# of only valid leaves and parents
def validJSON(json):

    # Must be either a leaf or parent
    if not (isLeaf(json) or isParent(json)):
        return False;

    # Leaf?
    if isLeaf(json):
        return True

    # Parent!
    else:
        for node in json['nodes']:
            if not validJSON(node):
                return False

    return True

def makeMenu(json):
    global indent

    def makeSpan(txt, cls, func):
        
        func = f' data-func="{func}"' if func else ''
        cls = f' class="{cls}"' if cls else ''
        html = f'<span{cls}{func}>{txt}</span>'
        return html
    
    # Leaf?
    if isLeaf(json):
        #printWithIndent('<li>')
        indent += 1
        printWithIndent(makeSpan(json['text'],None,json['func']))
        indent -= 1
        #printWithIndent('</li>')

    # Parent!
    else:
        arrowClass = None if indent < 3 else (
             'downarrow' if indent == 3 else  'rightarrow ')
        
        printWithIndent(makeSpan(json['text'],arrowClass,None))
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
