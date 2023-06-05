"""
Handles parsing parsing an XML File and writing that to python using cupy. 
Entrypoint is transpile(xml_file_path)
"""

import sys
import re
import xml.etree.ElementTree as ET
import xml_utils

TYPE_DICT = {
        'double': 'float64',
        'BigDecimal': 'float64',
        'int': 'int16'
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
    xml_utils.print_uniq_types(tree.getroot())
    # print_uniq_tags(root)
    # print_xml_structure(root)

    # This should support multiple constants blocks
    py_imports = "import numpy as np\n"
    py_consts = transpile_constants(find_uniq_tag('CONSTANTS', tree))
    py_main = transpile_main(find_uniq_tag('MAIN', tree))
    py_internals = transpile_internals(find_uniq_tag('INTERNALS', tree))

    python_code = [
            py_imports,
            py_consts,
            py_internals,
            py_main
            ]
    return '\n'.join(python_code)
    # TODO: transpile_methods() 
    # TODO: check_all_methods_present()


def adpot_inputs(inputs_root):
    """Adopts the input variables and their dtypes to be the main entry parameters"""

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
    main_method = [
            "\n # main\n"
            ]

    for element in main_root:
        if element.tag == 'EXECUTE':
            method = element.attrib.get('method', '').lower()
            main_method.append(f"{method}()")

        # TODO : there is an issue here and thense need to get parsed properly
        elif element.tag == 'EVAL':
            exec_code = element.attrib.get('exec', '').lower()
            main_method.append(exec_code)

    return '\n'.join(main_method)

def transpile_constants(constants_root):
    """Takes a single constants root element and transpiles its children to variables"""

    constants_defitions = [
            "\n # constants_defitions\n"
            ]

    for xml_element in constants_root:
        if not xml_element.tag == 'CONSTANT':
            raise ValueError("Child in CONSTANTS node was not of tag type CONSTANT")

        right_side = xml_var_to_right_side_expr(xml_element, check_for_value_attr=True)
        left_side = xml_element.attrib.get('name') + " = "

        constants_defitions.append(left_side + right_side)

    return '\n'.join(constants_defitions)

# TODO: test case internal has a table
def transpile_internals(internals_root):
    """
    similar to transpile constants transpiles the internals to numpy vars
    sets all right sides to float64 0.0
    """

    internals_definitions = [
            "\n # internals_definitions\n"
            ]
    for xml_element in internals_root:
        if not xml_element.tag == 'INTERNAL':
            raise ValueError("Child in INTERNAL node was not of tag type INTERNAL")

        xml_dtype = xml_element.attrib.get('type').rstrip()

        if xml_dtype == 'BigDecimal':
            right_side = "np.float64(0.0)"
        elif xml_dtype == 'BigDecimal[]':
            right_side  == "np.array([], dtype=float64"

        left_side = xml_element.attrib.get('name') + " = "

        internals_definitions.append(left_side + right_side)

    return '\n'.join(internals_definitions)

def xml_var_to_right_side_expr(xml_element, check_for_value_attr):
    """
    Takes in xml element with attrib type and value and transforms it into a numpy value,
    The check_for_value_attr flag determines raising error on element has no value attrib
    to assign a float64 value of 0.0 use set_right_side_zero()
    """

    check_xml_var(xml_element, check_for_value_attr=check_for_value_attr)

    xml_dtype = xml_element.attrib.get('type').rstrip()
    array_flag, dtype = translate_type(xml_dtype)

    xml_value = xml_element.attrib.get('value')

    if array_flag:
        # TODO: this 3 lines should use a regular expression and finditer()
        xml_table_arr = re.search(r"\{(.*?)\}", xml_value)
        xml_values = xml_table_arr.group(1).split(",")
        values = []

        # TODO: SET THE VALUES DEPENDING ON check_for_value_attr 

        for xml_value in xml_values:
            values.append(strip(xml_value, dtype))

        values = "[" + ", ".join(values) + "]"

        return "np.array(" + values + ", dtype='" + dtype + "')"

    if not array_flag:
        value = strip(xml_value, dtype)

        return "np." + dtype + "(" + value + ")"

    raise ValueError("Something went wrong with the array flag. True and False where checked")


# TODO: these testcases:
# BigDecimal.THISVALUE
# BigDecimal.valueOf(THISVALUE)
# BigDecimal(THISVALUE)
def strip(xml_value, dtype):
    """Takes xml_value and dtype, returns actual numpy variable"""

    if dtype == 'float64':

        # 1st -> the thing in the () after BigDecimal.<space>
        # 2nd -> the thing in the () after BigDecimal
        # 3rd -> anything after BigDecimal.
        regex_patterns = [
                r"BigDecimal\.valueOf\s+\((.*?)\)",
                r"BigDecimal\((.*?)\)",
                r"BigDecimal\.(.*)"
                ]

        i = 1
        for regex in regex_patterns:
            re_res = re.search(regex, xml_value)
            if re_res:
                value = re_res.group(1)
                if i < len(regex_patterns):
                    return value

                # case 3 BigDecimal.THISVALUE is a String that needs to be cast
                if i == len(regex_patterns):
                    weird_consts = {
                        "ONE": "1",
                        "TWO": "2",
                        "THREE": "3",
                    }

                    if weird_consts[value]:
                        return weird_consts[value]

                    # else weird const not found
                    raise ValueError(
                        """
                        Please dont use BigDecimal.FOUR or stuff like this
                        Only BigDecimal.ONE through THREE are supported.
                        BMF only uses ONE to my knowledge
                        """
                        )

            i += 1

        # if no match
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


def check_xml_var(xml_element, check_for_value_attr):
    """based on type and value present acts as a failsafe for parsing xml variables"""
    type_present = check_for_attrib('type', xml_element)
    value_present = check_for_attrib('value', xml_element)

    if not check_for_value_attr:
        value_present = True

    if not (type_present and value_present):
        raise ValueError(
                """
                xml_var_to_right_side_expr got variable that didnt have type and value attribute
                """
                )

def check_for_attrib(attrib, xml_element):
    """takes a string for an attrib key and returns true if its found"""
    attrib_value = xml_element.attrib.get(attrib)
    if attrib_value is not None:
        return True

    return False
