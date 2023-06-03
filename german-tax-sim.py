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

    transpiler.transpile("xml-codes/Lohnsteuer2020.xml.xhtml")

main()
