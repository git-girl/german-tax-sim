import xml.etree.ElementTree as ET
import sys
# import xml

def transpile(xml_file_path): 
    """Entry point into the transpiling part, takes in a file path writes to a file in ./.generated"""
    print(xml_file_path)

    check_file(xml_file_path)

    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    main_elements = tree.findall('.//MAIN') 
    if len(main_elements) == 1:
        main_xml_tag = main_elements[0]
    else: 
        sys.exit("ERROR: Expected exactly one <MAIN> tag.")
    # print_tags(root)
    # print_uniq_attrs(root)
    # print_uniq_tags(root)
    # print_xml_structure(root)
    py_main = transpile_main(main_xml_tag)
    return py_main
    # TODO: transpile_methods() 
    # TODO: check_all_methods_present()

def transpile_main(xml_main_tag):
    python_code = []

    for element in xml_main_tag:
            if element.tag == 'EXECUTE':
                method = element.attrib.get('method', '').lower()
                python_code.append(f"{method}()")
            elif element.tag == 'EVAL':
                exec_code = element.attrib.get('exec', '').lower()
                python_code.append(exec_code)
    
    return '\n'.join(python_code)

def check_file(xml_file_path): 
    # TODO: verify xml integrity
    print("")

def print_tags(element):
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
    unique_tags = set()

    # Iterate over the elements in the tree
    for element in root.iter():
        # Add the tag of each element to the set of unique tags
        unique_tags.add(element.tag)

    # Print the list of unique tags
    print(list(unique_tags))

def print_xml_structure(element, level=0):
    # Print the current element's tag with proper indentation
    print('  ' * level + element.tag)

    # Recursively print the child elements up to the second level
    if level < 2:
        for child in element:
            print_xml_structure(child, level + 1)


