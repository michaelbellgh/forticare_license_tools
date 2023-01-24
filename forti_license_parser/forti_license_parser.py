"""
Author: Michael Bell
extract_licenses.py - Reads license codes and metadata from Fortinet license PDF's (2021)
"""
import csv, fitz, re, glob
#fitz is pymupdf - a pdf reading pythonlib
#Need to install pymupdf - pip install pymupdf

def get_pdf_object(filename: str):
    doc = fitz.open(filename)
    return doc


def extract_fmg_faz_license_dict(fulltext):
    """
    Extracts licenses from a FortiNAC registration license.
    """
    if 'VM upgrade license' in fulltext:
        reg_code = re.search("([A-Z\d]{5}-){4}[A-Z\d]{5}", fulltext).group()
        purchase_order = re.search("(?<=Sales Order)[\s\:]+(\d+)", fulltext, re.DOTALL).groups()[-1]
        sku = re.search("(?<=" + purchase_order + ")[\s]+(.+)", fulltext).group().strip()
        ext_sku = re.search("(?<=" + sku + ")[\s]+(.+)", fulltext).groups()[-1]
        desc = re.search("(?<=" + ext_sku + ")[\s]+(.+)", fulltext).groups()[-1]
    else:
        reg_code = re.search("(?<=Contract Registration Code)[\s\:]+([\dA-Z]+)", fulltext).groups()[-1]
        purchase_order = re.search("(?<=Purchase Order Number)[\s\:]+(\d+)", fulltext, re.DOTALL).groups()[-1]
        table_lines = re.search("(?<=" + reg_code + ")(\s+.+)*", fulltext).group().splitlines()
        table_lines = [x for x in table_lines if x != ""]
        qty = table_lines[4]
        sku = table_lines[5]
        desc = " ".join(table_lines[6:])
        
    
    model = re.search("(Forti(Analyzer|Manager) VM)", fulltext).group()


    return {"contract": reg_code, "model" : model, "description": desc, "purchase_order": purchase_order, "qty": "1", "sku": sku, "license_type" : "VM Upgrade"}

def extract_fortinac_server_cert(fulltext):
    """
    Extracts licenses from a FortiNAC registration license.
    """
    reg_code = re.search("([A-Z\d]{5}-){4}[A-Z\d]{5}", fulltext).group()
    purchase_order = re.search("(?<=Sales Order)[\s\:]+(\d+)", fulltext, re.DOTALL).groups()[-1]
    sku = re.search("(?<=" + purchase_order + ")[\s]+(.+)", fulltext).groups()[-1]
    ext_sku = re.search("(?<=" + sku + ")[\s]+(.+)", fulltext).groups()[-1]
    desc = re.search("(?<=" + ext_sku + ")[\s]+(.+)", fulltext).groups()[-1]
    model = "FortiNAC"


    return {"contract": reg_code, "model" : model, "description": desc, "purchase_order": purchase_order, "qty": "1", "sku": sku, "license_type" : "VM Upgrade"}


def extract_special_license_dict(fulltext):
    """
    Extracts licenses from a VM/Cloud entitlements
    """
    reg_code = re.search("(?<=Contract Registration Code)[\s\:]+([a-zA-Z0-9]+)", fulltext).groups()[-1]
    purchase_order = re.search("(?<=Purchase Order Number)[\s\:]+([0-9]+)", fulltext, re.DOTALL).groups()[-1]

    table_lines = re.search("(?<=" + reg_code + ")(\s+.+)*", fulltext).group().splitlines()
    table_lines = [x for x in table_lines if x != ""]
    qty = table_lines[4]
    sku = table_lines[5]
    desc = " ".join(table_lines[6:])
    
    model = ""
    if "FortiManager VM" in desc:
        model = "FortiManager VM"
    elif "FortiAnalyzer VM" in desc:
        model = "FortiAnalyzer VM"
    elif "FortiCloud FAP management" in desc:
        model = "FortiCloud FAP Management"
    elif "FortiNAC VM FortiNAC" in desc:
        model = "FortiNAC VM"
    elif "FortiNAC Control and Application VM Server Certificate":
        model = "FortiNAC"
    else:
        model = desc

    return {"contract": reg_code, "model" : model, "description": desc, "purchase_order": purchase_order, "qty": qty, "sku": sku, "license_type" : "VM Upgrade"}

def extract_forti_nac_license_dict(fulltext):
    """
    Extracts licenses from a FortiNAC registration license.
    """
    reg_code = re.search("(?<=Contract Registration Code)[\s\:]+([a-zA-Z0-9]+)", fulltext).groups()[-1]
    purchase_order = re.search("(?<=Purchase Order Number)[\s\:]+([0-9]+)", fulltext, re.DOTALL).groups()[-1]

    table_lines = re.search("(?<=" + reg_code + ")(\s+.+){8}", fulltext).group().splitlines()
    table_lines = [x for x in table_lines if x != ""]
    qty = table_lines[4]
    sku = table_lines[5]
    desc = table_lines[6]
    units = table_lines[7].split(":")[-1]

    return {"contract": reg_code, "model" : desc, "description": desc, "purchase_order": purchase_order, "qty": qty, "sku": sku, "license_type" : "VM Upgrade"}



def extract_license_dict(pdf_object):
    """
    Extracts license information using regex, and outputs a dictionary.
    Tested with 2500+ licenses, with the following SKU's:
    FC-10-0060F-288-02-12
    FC-10-F211E-247-02-36
    FC-10-0060F-950-02-36
    FC-10-S124F-247-02-36
    FC-10-F431F-247-02-36
    FC-10-0060F-247-02-36
    FC-10-F200F-211-02-12
    FC-10-F18HF-247-02-36
    FC-10-F200F-288-02-12
    FC-10-F200F-112-02-12
    FC-10-F200F-950-02-36
    FC-10-F200F-108-02-12
    FC-10-F200F-100-02-12
    FC-10-F18HF-211-02-12
    FC4-10-M3004-248-02-3
    FC3-10-LV0VM-149-02-3
    FC3-10-LV0VM-248-02-3
    FAZ-VM-GB25
    FMG-VM-1000-UG
    FC-10-P431F-247-02-12
    FC-10-S12FP-247-02-12
    FC-10-S10EF-247-02-12
    FC-10-0060F-179-02-12
    FC-10-F100F-950-02-12
    FC-10-F100F-188-02-12
    FC-10-0060F-950-02-12
    FC-10-0060F-188-02-12
    FC-10-W248E-247-02-12
    FC-10-S148P-247-02-12
    FC-10-F100F-288-02-12
    FC-10-P433F-247-02-12
    FC-15-CLDPS-219-02-12
    FC-10-F100F-179-02-12
    FC-10-WMSC1-190-02-12
    FC2-10-FNAC1-213-01-12
    FC-10-90AP1-639-02-12
    FC-10-NCVCA-248-02-12
    FNC-CA-VM
    FC-10-0060F-179-02-02
    FC-10-0060F-464-02-02
    """
    fulltext = ""
    for page in pdf_object:
        fulltext += page.get_text()
    #Uses positive lookbehinds to semi-confirm our regex is grabbing the right codes.

    if "FortiNAC Control and Application VM Server Certificate" in fulltext:
        return extract_fortinac_server_cert(fulltext)

    if any(x in fulltext for x in ("FortiManager VM", "FortiAnalyzer VM")):
        return extract_fmg_faz_license_dict(fulltext)
    
    if any(x in fulltext for x in ("FortiManager VM", "FortiAnalyzer VM", "FortiCloud FAP management", "FortiNAC VM FortiNAC")):
        return extract_special_license_dict(fulltext)

    contract_code = re.search("(?<=Contract Registration Code\n\:\n)[A-Z0-9]{12}", fulltext).group(0)
    coverage_line = re.search("((?P<unit>\d+)[ ]?(?P<unittype>(Year|Day|Month))(s)? coverage) for (.+)", fulltext)
    coverage = coverage_line.group("unit") + " " + coverage_line.group("unittype") + "s"
    model = re.search("((?P<unit>\d+)[ ]?(Year|Day|Month)(s)?\scoverage for (?P<model>.+)\s(include:))", fulltext).group('model')
    cgroup_text = "(?<=" + coverage_line.group(0) + ")([\s\r\n]+)(.+)$"
    #
    if re.search("^(include:\n)", fulltext):
        cgroup_text = cgroup_text = "(?<=" + coverage_line.group(0) + " include:)([\s\r\n]+)(.+)$"
        desc_text = re.search(cgroup_text, fulltext, re.DOTALL).group(0).strip()
    else:
        desc_text = re.search(cgroup_text, fulltext, re.DOTALL)
        desc_text = desc_text.groups()[-1].strip()
    purchase_order = re.search("(?<=Purchase Order Number\n:\n).+", fulltext).group(0)
    qty = re.search("(?<=Qty\nPart Number\nDescription\n)\d+", fulltext).group(0)
    sku = re.search("[A-Za-z0-9\-]{21}", fulltext).group(0)
    
    return {"contract" : contract_code, "coverage" : coverage, "model" : model, "description" : desc_text, "purchase_order" : purchase_order, "qty" : qty, "sku" : sku, "license_type": "Standard Entitlement"}

    

def extract_all_licenses(pdf_files, output_csv):
    field_names = ["contract", "coverage", "model", "description", "purchase_order", "qty", "sku", "license_type"]
    output = csv.DictWriter(open(output_csv, "w", newline=""), fieldnames=field_names)
    output.writeheader()
    for pdf in pdf_files:
        license = extract_license_dict(get_pdf_object(pdf))
        output.writerow(license)

#Reads all PDF's in current directory
extract_all_licenses(glob.glob("*.pdf"), "output.csv")