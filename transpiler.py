"""
Handles parsing parsing an XML File and writing that to python using cupy. 
Entrypoint is transpile(xml_file_path)
"""

import xml.etree.ElementTree as ET
import sys
# import xml

def transpile(xml_file_path):
    """
    Entry point into the transpiling part, 
    takes in a file path writes to a file in ./.generated
    """
    print(xml_file_path)

    # check_file(xml_file_path)

    tree = ET.parse(xml_file_path)

    # root = tree.getroot()
    # print_tags(root)
    # print_uniq_attrs(root)
    # print_uniq_tags(root)
    # print_xml_structure(root)

    # This should support multiple constants blocks
    py_consts = transpile_constants(find_uniq_tag('CONSTANTS', tree))
    py_main = transpile_main(find_uniq_tag('MAIN', tree))

    return py_consts + py_main
    # TODO: transpile_methods() 
    # TODO: check_all_methods_present()

def find_uniq_tag(tag_name, tree):
    """
    Finds uniq tag within tree. Raises error if none found or not unique.

    Args:
        tag_name (str): the Tag name to search for.
        tree (xml.etree.ElementTree): The tree to search through.

    Returns:
        xml.etree.ElementTree.Element
    """
    tag_elements = tree.findall('.//' + tag_name)
    if len(tag_elements) == 1:
        uniq_tag = tag_elements[0]
        return uniq_tag

    sys.exit("ERROR: Expected exactly one <",tag_name,"> tag. Found: ", len(tag_elements))

def transpile_main(main_root):
    """Transpile the main function, this has some different rules then other bits"""
    python_code = []

    for element in main_root:
        if element.tag == 'EXECUTE':
            method = element.attrib.get('method', '').lower()
            python_code.append(f"{method}()")
        elif element.tag == 'EVAL':
            exec_code = element.attrib.get('exec', '').lower()
            python_code.append(exec_code)

    return '\n'.join(python_code)

# def transpile_variables(variables_root):
    # find the Inputs tag
    # find the outputs standard
    # find the outputs DBA
    # find the internals
    # print("TODO")

def transpile_constants(constants_root):
    return "a = 3"


# def check_file(xml_file_path):
    # TODO: verify xml integrity

def print_tags(element):
    """Takes in single element and prints its child tags"""
    print(element.tag)  # Print the tag of the current element
    for child in element:
        print_tags(child)  # Recursively print tags of child elements

# in the format there are the attibutes
#['value',
# 'versionNummer',
# 'method',
# 'regex_transform',
# 'version',
# 'name',
# 'regex_test',
# 'exec',
# 'expr',
# 'type',
# 'default']
def print_uniq_attrs(root):
    """Prints the Set of children attributes, takes in element, returns nothing"""
    unique_attributes = set()

    # Iterate over the elements in the tree
    for element in root.iter():
        # Collect the attributes of each element
        attributes = element.attrib
        # Add the attributes to the set of unique attributes
        unique_attributes.update(attributes.keys())

    # Print the list of unique attributes
    print(list(unique_attributes))

def print_uniq_tags(root):
    """Prints the Set of children tags, takes in element, returns nothing"""
    unique_tags = set()

    # Iterate over the elements in the tree
    for element in root.iter():
        # Add the tag of each element to the set of unique tags
        unique_tags.add(element.tag)

    # Print the list of unique tags
    print(list(unique_tags))

def print_xml_structure(element, level=0):
    """
    Util: Print the xml structure 2 levels deep. 
    Takes in element and level to start at. Returns nothing
    """
    # Print the current element's tag with proper indentation
    print('  ' * level + element.tag)

    # Recursively print the child elements up to the second level
    if level < 2:
        for child in element:
            print_xml_structure(child, level + 1)
