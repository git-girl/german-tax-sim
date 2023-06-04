import uuid
import transpiler

def main():
    """
    Entry Point for the entire Tax Sim Module 

    Requires the XML File Path, 
    a Dataframe matching all variables from the BMF API,
    a dict of options
    """

    # TODO: shouldnt this be in __init.py__ if it is the entry point entry point?
    # def main(xml_file_path: str, df: pd.DataFrame, options: Dict):

    code = transpiler.transpile("xml-codes/Lohnsteuer2020.xml.xhtml")
    # NOTE: this back and forth to file serves as a means to save the transpiled code
    filepath = write_code_to_file(code)
    exec_file(filepath)

# TODO: Use a template file that structures the code a bit maybe
# and handles imports and stuff like that
def write_code_to_file(code):
    """
    Writes string to a file with uuid4() name in ./generated and returns the filepath
    """
    filepath = '.generated/' + str(uuid.uuid4()) + '.py'
    with open(filepath, 'w') as file:
        file.write(code)

    return filepath

def exec_file(filepath):
    """Run file."""
    with open(filepath) as file:
        code = file.read()
    # exec(code)

main()
