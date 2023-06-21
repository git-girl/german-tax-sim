"""
Handles parsing parsing an XML File and writing that to python using cupy. 
Entrypoint is transpile(xml_file_path)
"""

import sys
import re
import xml.etree.ElementTree as ET
import xml_utils as xu

from java.math import BigDecimal

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
    # xu.print_uniq_types(tree.getroot())
    # print_uniq_tags(root)
    # print_xml_structure(root)

    # This should support multiple constants blocks
    py_imports = "import numpy as np\n"
    py_consts = transpile_constants(xu.find_uniq_tag('CONSTANTS', tree))
    py_main = transpile_main(xu.find_uniq_tag('MAIN', tree))
    py_internals = transpile_internals(xu.find_uniq_tag('INTERNALS', tree))
    py_methods = transpile_methods(tree.findall('.//' + 'METHOD'))
    print(py_methods)

    python_code = [
            py_imports,
            py_consts,
            py_internals,
            py_main,
            py_methods
            ]
    return '\n'.join(python_code)
    # TODO: check_all_methods_present()


def adpot_inputs(inputs_root):
    """Adopts the input variables and their dtypes to be the main entry parameters"""


def transpile_main(main_root):
    """
    Transpile the main function, this has some different rules then other bits
    Methods are supposed to be lower_snake_case()
    """
    main_method = [
            "\n # main\n"
            ]

    for element in main_root:
        if element.tag == 'EXECUTE':
            method_name = element.attrib.get('method', '').lower()
            main_method.append(method_name + "()")

        # WARNING: eval tags arent assigned types explicitly pray
        # every value referenced is treated as a float and creation
        # must be as a float. Sorry
        elif element.tag == 'EVAL':
            xml_exec_code = element.attrib.get('exec', '')
            if not check_right_side_for_string(xml_exec_code):
                main_method.append(xml_exec_code)
            else:
                main_method.append(transpile_eval_exec(xml_exec_code))

    return '\n'.join(main_method)

# TODO: testcases
# <EVAL exec="KVSATZAN = (KVZ.divide(bd).divide(ZAHL100)).add(BigDecimal.valueOf(0.07))"/>
def transpile_eval_exec(xml_exec_code):
    """
    Takes the xml.attrib exec value and transpiles that code 
    to python numpy code
    """
    parts = xml_exec_code.split("=", 1)
    varname = parts[0]
    raw_right_side = parts[1]

    value = strip(raw_right_side, dtype='float64')

    transpiled_right =  "np.float64(" + value + ")"

    return varname + " = " + transpiled_right


def check_right_side_for_string(py_code):
    """
    If the right side of a python code bit isnt purely spaces and numbers
    return True. 
    Otherwise False.
    """
    pattern = r'=\s*\d+\s*$'
    match = re.search(pattern, py_code)
    if match:
        return False

    return True

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
    """
    Takes xml_value and dtype, returns actual numpy variable 

    parses: 
        BigDecimal.THISVALUE
        BigDecimal.valueOf(THISVALUE)
        BigDecimal(THISVALUE)
    returning: 
        THISVALUE ready for insert into np.float64(THISVALUE)
    """

    if dtype == 'float64':

        # 1st -> the thing in the () after BigDecimal.<space>
        # 2nd -> the thing in the () after BigDecimal
        # 3rd -> anything after BigDecimal.
        regex_patterns = [
                r"BigDecimal\.valueOf\s+\((.*?)\)",
                r"BigDecimal\.valueOf\((.*?)\)",
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
                        "ZERO": "0",
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

def transpile_methods(method_elements):
    """
    Entry point for parsing all METHOD blocks into pythong code
    """
    python_code = []

    for method_element in method_elements:

        python_code.append(recurse_method_definition(method_element))

    return '\n'.join(python_code)

def recurse_method_definition(element, indent=""):
    python_code = []

    python_code.append(indent + transpile_element(element))
    for child in element:

        # NOTE: the issue with then and stuff like this is 
        # proabably that im not doing anything on the 
        # closing block like /THEN  -> grep with //THEN
        if child.tag == "THEN":
            child_indent = indent
        else:
            child_indent = indent + "    "

        transpiled_element = recurse_method_definition(child, child_indent)

        if child.tag == "THEN":
            python_code.append(indent + "THEN")

        python_code.append(transpiled_element)

    # python_code.append(close_element(element.tag))

    return '\n'.join(python_code)

def close_element(element_tag):
    """
    Closes the element. returning the formated string.
    You could make this generic but then the generated code 
    would look less nice.
    """
    if element_tag == 'EVAL':
        return ""
    if element_tag == 'EXEC':
        return ""

    return "\n"

def transpile_element(element):
    """Calls the appropriate transpile Method on the element"""

    element_tag = element.tag
    if element_tag == 'METHOD':
        method_name = element.attrib.get('name').lower()
        return "def " + method_name + "():"

    if element_tag == 'EXEC':
        method_name = element.attrib.get('method', '').lower()
        return method_name + "()"

    # EVAL is the big point -> implement regexes for all method definitions etc.
    if element_tag == 'EVAL':
        xml_exec_code = element.attrib.get('exec', '')
        print(xml_exec_code)
        if not check_right_side_for_string(xml_exec_code):
            return xml_exec_code

        return transpile_eval_exec(xml_exec_code)
    if element_tag == 'IF':
        expression = element.attrib.get('expr')
        return "if " + expression + ":"

    if element_tag == 'THEN':
        return ""

    if element_tag == 'ELSE':
        return "else: "

    raise ValueError( "Tag Element " + element.tag + " couldn't be matched by transpile_elements")

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
    type_present = xu.check_for_attrib('type', xml_element)
    value_present = xu.check_for_attrib('value', xml_element)

    if not check_for_value_attr:
        value_present = True

    if not (type_present and value_present):
        raise ValueError(
                """
                xml_var_to_right_side_expr got variable that didnt have type and value attribute
                """
                )
