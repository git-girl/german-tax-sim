import xml.etree.ElementTree as ET
import sys

def check_for_attrib(attrib, xml_element):
    """takes a string for an attrib key and returns true if its found"""
    attrib_value = xml_element.attrib.get(attrib)
    if attrib_value is not None:
        return True

    return False

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
def print_tags(element):
    """Takes in single element and prints its child tags"""
    print(element.tag)  # Print the tag of the current element
    for child in element:
        print_tags(child)  # Recursively print tags of child elements

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

def print_uniq_types(element):
    """Prints the Set of children's type attributes, takes in element, returns nothing"""
    unique_types = set()
    for child in element.iter():
        var_type = child.attrib.get('type')
        if var_type is not None:
            unique_types.add(var_type)

    print(unique_types)

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
