# EARLY DEV: German Tax Simulation Tool 

> The PAP Documentation goes back until 2007 so until there there should be XML files

> DANGER NOTE: note that the Format of the XML TABLES for example TAB1 on the Versorgungsbezuege starts at index1 for the first 
> 5 years (so in 2020 the first 5 years are)
- this just means that if you are modifying the table you will need to include a BigDecimal.valueOf(0.0) at index 1


 

## DevNotes

- TODO: write something on installing cuda for your cuda version i think that is an issue in adoption 

> Important: is it good that i differentiate between transpiling different blocks? 
- My worry is that I'm introducing a lot of very specific things and that with minor changes 
  like another CONSTANTS block or something like that that I will make everything error prone 
  down the line

- There can be only 1 MAIN tag and that is required. Other 1st level tags should 
  be supported with theoretically infinite occurrences.

XML Structure: 
- PAP 
  - VARIABLES 
    - INPUTS 
    - OUTPUTS  type STANDARD 
      - OUTPUT 
      - ... 
    - OUTPUTS  type DBA 
      - OUTPUT 
      - ... 
    - INTERNALS  
      - INTERNAL 
      - ... 
  - CONSTANTS 
    - CONSTANT
    - ... 
  - METHODS 
    - MAIN 
    - METHOD 
    - ... 

XML Tag Attrib List: 
['value',
 'versionNummer',
 'method',
 'regex_transform',
 'version',
 'name',
 'regex_test',
 'exec',
 'expr',
 'type',
 'default']

## Plan 

I have already published a (similar tool)[https://github.com/git-girl/bmf-taxcalculator-csv].  
That one is based on a single row tax calculator by @mgoltzsche , but isn't performant at all.

- I think I want to program this with GPU usage in mind and run the calculations in parallel. 
- This means design patterns can't be applied as all calculations should stay on the gpu rather 
  then dropping in and out. 

## Design 

- [ ] **XML to Python 'Transpiler'**
> 'Transpile' the XML to python using the cupy library 

_this transpiled code then gets executed_

- [ ] IO Interface that has params like the XML File the Data etc. 
> There should be some easy to use interface to the whole thing with options etc.

**Points to consider** 
- Methods that aren't standard in the BMF XML Files should be considered 
  - However no need to go overboard here, can also have opt to keep transpiled 
    python file and then people could change that if they want to add a logarithm 
    or something like that

## Why and what for? 

This is made with scientific purposes in mind. To the best of my knowledge there 
aren't any institutes publishing their simulation models for anyone to use. 
This creates bad barriers for research.

## Usage 

this is a TODO but it must include 

find a set of all xml files here: 

they arent included because i added a license and these files arent by me

