"""
Handles parsing parsing an XML File and writing that to python using cupy. 
Entrypoint is transpile(xml_file_path)
"""

import sys
import re
import xml.etree.ElementTree as ET

TYPE_DICT = {
        'double': 'np.float64()',
        'BigDecimal': 'np.float64()',
        'int': 'np.int16()'
        }

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
    # print_uniq_types(tree.getroot())
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
    """Takes a single constants root element and transpiles its children to variables"""

    for xml_element in constants_root:
        if xml_element.tag == 'CONSTANT':
            xml_var_to_np(xml_element)
        else:
            raise ValueError("Child in CONSTANTS node was not of tag type CONSTANT")

    return "TODO"

def xml_var_to_np(xml_element):
    """Takes in xml element with attrib type and value and transforms it into a numpy value"""
    check_xml_var(xml_element)
    xml_dtype = xml_element.attrib.get('type').rstrip()
    array_flag, dtype = translate_type(xml_dtype)
    # NOTE: xml_value might be a table value so
    # translate type must handle tables
    print(array_flag, dtype)

    xml_value = xml_element.attrib.get('value')

    if array_flag:
        xml_table_arr = re.search(r"\{(.*?)\}", xml_value)
        xml_values = xml_table_arr.group(1).split(",")
        for xml_value in xml_values:
            value = strip(xml_value, dtype)
    elif not array_flag:
        value = strip(xml_value, dtype)
    print(value)

    # if not array_flag:
        # assign dtype.new(value)

# TODO: these testcases:
# BigDecimal.THISVALUE
# BigDecimal.valueOf(THISVALUE)
# BigDecimal(THISVALUE)
def strip(xml_value, dtype):
    """Takes xml_value and dtype, returns actual numpy variable"""

    if dtype == 'np.float64()':
        regex_patterns = [
                r"BigDecimal\.(\w+)",
                r"BigDecimal\.valueOf\((\w+)\)",
                r"BigDecimal\((\w+)\)"
                ]

        for regex in regex_patterns:
            re_res = re.search(regex, xml_value)
            if re_res:
                value = re_res.group(1)
                return value

        # if no match:
        raise TypeError(
                "Got float64 dtype, but value was not matched by regex value was: "
                , xml_value)

    # if other dtype
    raise TypeError("strip got an unsupported type")



def translate_type(xml_dtype):
    """
    Returns Array 
        1. element array_flag 
        2. element dtype

    Handles and checks xml type attribs and maps them to type.
    if no valid dtype errors out.
    """

    array_flag = False
    if "[]" in xml_dtype:
        if xml_dtype.endswith("[]"):
            array_flag = True

            xml_dtype = xml_dtype.replace("[]", "")
            dtype = TYPE_DICT[xml_dtype]
        else:
            raise ValueError("Error: Substring '[]' is not at the end of the string.")
    else:
        dtype = TYPE_DICT[xml_dtype]

    if dtype is None:
        raise ValueError("XML attributes datatype: ", xml_dtype, " is not contained in TYPE_DICT.")

    return [array_flag, dtype]


def check_xml_var(xml_element):
    """based on type and value present acts as a failsafe for parsing xml variables"""
    type_present = check_for_attrib('type', xml_element)
    value_present = check_for_attrib('value', xml_element)
    if not (type_present and value_present):
        sys.exit("ERROR: xml_var_to_np got variable that didnt have type and value attribute")

def check_for_attrib(attrib, xml_element):
    """takes a string for an attrib key and returns true if its found"""
    attrib_value = xml_element.attrib.get(attrib)
    if attrib_value is not None:
        return True

    return False


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
