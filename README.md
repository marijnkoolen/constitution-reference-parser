# constitution-reference-parser
Python implementation to extract internal references in national constitutions

This is part of the Legal Structures project, a Digging Into Data Challenge 2013 funded research project to study references structures in civil codes and constitutions across countries to map families of legal traditions.

The constitutions for this project are derived from the [Constitute Project](https://www.constituteproject.org/).

The reference parser runs in two steps:

1. parsing the HTML files to extract the logical structure of constitutions and producing JSON output
2. parsing the text units in the JSON files to extract and resolve references and producing CSV output of section identifiers, resolved references and unresolved references.

To run the parser:

> python parse_constitution_html.py HTML-dir -structure-dir

> python analyse_constitution_refs.py +structure-dir -identifier-dir -reference-dir -missing-references-dir

