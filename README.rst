pdfforms
=========

pdfforms is a small utility for populating fillable pdf forms from a csv
data source.  It was created with the intent of filling US tax forms using
tax data prepared with a spreadsheet, but should be equally applicable to
other forms.

Features
---------

* Assigns numeric id for each field
* Generates test pdf showing ids of text fields
* Merges csv data into final filled pdf
* Can process multiple pdfs at a time

Requirements
------------

pdfforms requires Python 3.5 or higher and `pdftk`_, which does all the real work.

.. _pdftk: https://www.pdflabs.com/tools/pdftk-the-pdf-toolkit/

Installation
-------------

To install: ``pip install pdfforms``

Use
---

Let's say you have a spreadsheet with your tax calculations.  You want to
populate your tax forms with the data from the spreadsheet.  pdfforms
allows you to do so with the following steps:

#. First pdfforms must inspect the forms to be filled.  pdfforms will
   extract a list of fields in each of the specified documents.  Each field
   is assigned a numeric id, and test documents are generated with filled
   forms, showing the id of each text field::

    $ pdfforms inspect f1040*.pdf
    f1040sse.pdf
    f1040sce.pdf
    f1040.pdf


   The filled test pdfs are stored by default in the ``test/`` subdirectory.

#. Browse the test pdf files and add the field numbers of the fields you
   need to fill to your spreadsheet.  pdfforms only reads the first and
   third columns of the datafile.  The first column should contain the name
   of the pdf file with the form to fill and the field numbers.  The third
   column should contain the data to be written into the field.  The rest
   of the sheet is ignored, so you can use it for notes, calculations, etc.

   Below is an example spreadsheet for a (fictional) 2016
   tax return.

   .. csv-table::

        f1040.pdf,Form 1040,,2016,
        3,First Name and initial,John Q,,
        4,Last Name,Public,,
        5,SSN,321546789,321-54-6789,
        6,Spouse's Name,Susie,,
        7,Spouse's Last Name,Public,,
        8,SSN,132458697,132-45-8697,
        9,Address,5776 Winding Ln,,
        11,,"Springfield, MA",,
        18,Filing status,MJ,,
        24,Exemption - self,1,,
        25,Exemption - spouse,1,,
        27,Dependent name,Timothy Public,,
        28,Dependent ssn,531248680,531-24-8680,
        29,Dependent relationship,Son,,
        30,Dependent under 17,1,,
        31,Dependent name,Abigail Public,,
        32,Dependent ssn,428775031,428-77-5031,
        33,Dependent relationship,Daughter,,
        34,Dependent under 17,1,,
        45,Line 6a,2,,
        46,Line 6c,2,,
        49,Line 6d,4,,
        50,Line 7,"60,000",salaries,
        52,Line 8a,124,taxable interest,
        64,Line 12,"15,000",business income,
        92,Line 22,"75,124",total income,
        102,Line 27,"1,060",half SE tax,
        121,Line 36,"1,060",,
        123,Line 37,"74,064",Adjusted Gross Income,
        125,Line 38,"74,064",,
        133,Line 40,"12,600",Standard Deduction,
        135,Line 41,"61,464",,
        137,Line 42,"16,200",Exemptions,"$ 4,050"
        139,Line 43,"45,264",Taxable income,
        145,Line 44,"4,528",Tax,
        151,Line 47,"4,528",,
        161,Line 52,"2,000",Child Tax Credit,
        171,Line 55,"2,000",Total Credits,
        173,Line 56,"2,528",,
        175,Line 57,"2,119",Self-employment tax,
        196,Line 63,"4,647",Total Tax,
        198,Line 64,"8,688",Tax withheld,
        225,Line 74,"8,688",Total Payments,
        227,Line 75,"4,041",Amount you overpaid,
        230,Line 76a,"4,041",Amount you want refunded,
        232,Line 76b,123654789,Routing Number,
        234,Line 76c,Savings,Account Type,
        235,Line 76d,135724,Account Number,
        247,Occupation,Salesman,,
        248,Daytime phone number,413-555-1212,,
        249,Spouse's Occupation,Artist,,
        ,,,,
        f1040sce.pdf,Schedule C-EZ,,,
        0,Name,Susie Public,,
        1,SSN,132-45-8697,,
        9,Line F,2,No,
        2,Line A,Artist,Principle business or profession,
        3,Line B,711510,Business Code,
        13,Line 1,"22,000",gross receipts,
        15,Line 2,"7,000",total expenses,
        17,Line 3,"15,000",net profit,
        ,,,,
        f1040sse.pdf,Form SE - Section A Short Schedule SE,,,
        0,Name,Susie Public,,
        1,SSN,132-45-8697,,
        6,Line 2,"15,000",,
        8,Line 3,"15,000",92.35%,
        10,Line 4,"13,853",15.30%,
        12,Line 5,"2,119",50.00%,
        14,Line 6,"1,060",,

   The test pdfs do not show field numbers for checkboxes.  Currently the
   only way to fill checkboxes is to examine the ``fields.json`` file and
   find the field number and allowed values of the checkbox.

#. Once the file name and field numbers have been added to your spreadsheet,
   save the spreadsheet as a csv file and fill the forms::

        $ pdfforms fill mydata.csv
        f1040sse.pdf
        f1040sce.pdf
        f1040.pdf

   The final, populated pdf files are saved by default to the ``filled/``
   subdirectory.
