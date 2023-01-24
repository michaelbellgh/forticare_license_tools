
# forti_license_parser

  

A tool to extract licenses from Fortinet PDF's (Sourced from 2021) and export details to a CSV

  

## Getting started

  

Received a bunch of emails from your distributor with hundreds of unsorted license PDFs you need to activate?

Use this tool to sort them into a usable CSV format!

  

## Usage

  1. Install PyMuPDF by running:
 

    pip install pymupdf

  3. Put all the license PDF's in the same folder as the tool
  4. Run the tool with no arguments:
 



    python3 forti_license_parser.py
3. A file called 'output.csv' will be created in the same directory

### Example:

| contract     | coverage        | model         | description       | purchase_order | qty | sku                   | license_type         |
|--------------|-----------------|---------------|-------------------|----------------|-----|-----------------------|----------------------|
| 0001AB123456 | 1 Year coverage | FortiGate 60F | SD-WAN Monitoring | 1234567890     | 1   | FC-10-0060F-288-02-12 | Standard Entitlement |

## Requirements

 - PyMuPDF
 - Python3 (>= 3.4)

## Limitations
There may be some issues installing PyMuPDF on some machines with Python version 3.6 and over. 
To work around, use Python 3.6 OR upgrade pip OR use a virtual env, remove 'fitz' package and reinstall
OR use an earlier version of PyMuPDF

## Tested License SKU's

- FC-10-0060F-288-02-12
- FC-10-F211E-247-02-36
- FC-10-0060F-950-02-36
- FC-10-S124F-247-02-36
- FC-10-F431F-247-02-36
- FC-10-0060F-247-02-36
- FC-10-F200F-211-02-12
- FC-10-F18HF-247-02-36
- FC-10-F200F-288-02-12
- FC-10-F200F-112-02-12
- FC-10-F200F-950-02-36
- FC-10-F200F-108-02-12
- FC-10-F200F-100-02-12
- FC-10-F18HF-211-02-12
- FC4-10-M3004-248-02-3
- FC3-10-LV0VM-149-02-3
- FC3-10-LV0VM-248-02-3
- FAZ-VM-GB25
- FMG-VM-1000-UG
- FC-10-P431F-247-02-12
- FC-10-S12FP-247-02-12
- FC-10-S10EF-247-02-12
- FC-10-0060F-179-02-12
- FC-10-F100F-950-02-12
- FC-10-F100F-188-02-12
- FC-10-0060F-950-02-12
- FC-10-0060F-188-02-12
- FC-10-W248E-247-02-12
- FC-10-S148P-247-02-12
- FC-10-F100F-288-02-12
- FC-10-P433F-247-02-12
- FC-15-CLDPS-219-02-12
- FC-10-F100F-179-02-12
- FC-10-WMSC1-190-02-12
- FC2-10-FNAC1-213-01-12
- FC-10-90AP1-639-02-12
- FC-10-NCVCA-248-02-12
- FNC-CA-VM
- FC-10-0060F-179-02-02
- FC-10-0060F-464-02-02
- FC-10-F18HF-179-02-02
- FC-10-F18HF-464-02-02
