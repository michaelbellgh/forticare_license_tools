from csv import DictWriter, DictReader
import requests
import argparse


'''
Credentials will need to specified in a separate Python file in this format:
-----

username = {MY FORTICARE ACCOUNT ID HERE}
password = {MY FORTICARE API TOKEN HERE}

----
You can obtain these credentials by creating a API user account, as described here: https://community.fortinet.com/t5/FortiCloud-Products/Technical-Tip-API-how-to-retrieve-list-of-registered-units-for/ta-p/194760
They can also be specified by the --account-id and --api-token

'''


def get_oauth_token(api_username: str, api_password: str, client_id: str = "assetmanagement", base_url: str = "https://customerapiauth.fortinet.com/api/v1/oauth/token/") -> dict:
    body = {"username": api_username,
      "password": api_password,
      "client_id": client_id,
      "grant_type": "password"}
    
    response = requests.post(base_url, json=body).json()
    return response
    

def get_device_list(oauth_token: str, serial_num_filter: str = "F", base_url: str ="https://support.fortinet.com/ES/api/registration/v3/products/list") -> dict:
    response = requests.post(base_url, headers={"Authorization":  "Bearer " + oauth_token}, json={"serialNumber": serial_num_filter})
    return response.json()


def write_assets_to_csv(output_csv: str, assets_json: dict) -> None:
  headers = ["serialNumber", "registrationDate", "productModel", "contracts", "SKUs", "Entitlements"]
  writer = DictWriter(open(output_csv, "w", newline="",), fieldnames=headers)
  
  writer.writeheader()

  for asset in assets_json["assets"]:
    row = {"serialNumber": asset["serialNumber"], "registrationDate": asset["registrationDate"], "productModel": asset["productModel"]}
    sku_text, entitlement_text, contracts = "","", ""
    if asset["contracts"] is not None:
      sku_text = "\n".join([x["sku"].strip() for x in asset["contracts"]])
      contracts = "\n".join([x["contractNumber"] for x in asset["contracts"]])
    if asset["entitlements"] is not None:
      entitlement_text = "\n".join([x["typeDesc"].strip() for x in asset["entitlements"]])
    row.update({"SKUs": sku_text, "Entitlements": entitlement_text, "contracts": contracts})
    writer.writerow(row)

def get_contract_list(input_csv_filename: str) -> list:
    csv_file = open(input_csv_filename, "r")
    with csv_file:
      return list(DictReader(csv_file))

<<<<<<< HEAD
def get_loose_contracts(asset_json: dict, mapping_dict: dict, equalSkus: dict) -> list:
=======
def get_loose_contracts(asset_json: dict, mapping_dict: dict, equalSkus: dict, contracts: list=None) -> list:
>>>>>>> b50fbc74a609463488b8dd6f6d31c8404337fac0
    loose_items = []
    burnt_contracts = []
    for asset in asset_json["assets"]:
        #For every instance of our mapping dictionary if it matches our current asset model
        for mapping in [v for k,v in  mapping_dict.items() if k == asset["productModel"]]:
            for sku in mapping:
                equal_skus = []
                if sku in equalSkus:
                    equal_skus = equalSkus[sku]
                #Get the currently assigned contracts of type SKU X
<<<<<<< HEAD
                skus_assigned = None
                if asset["contracts"] is not None:
                    skus_assigned = [x for x in asset["contracts"] if (x["sku"] == sku or x["sku"] in equal_skus) and asset["contracts"] is not None]
                count_of_assigned_sku = len(skus_assigned) if skus_assigned is not None else 0
                if count_of_assigned_sku > 3:
                    print("here")
                if count_of_assigned_sku > int(mapping[sku]):
                    #We have more of this SKU assigned than defined in the mapping, so lets add the last N (extras) to loose_items using splicing
                    extra_count = len(skus_assigned) - int(mapping[sku])

                    original_trailer_items = skus_assigned[:int(mapping[sku]) + 1]
=======
                skus_assigned = [x for x in asset["contracts"] if x["sku"] == sku or x["sku"] in equal_skus]
                count_of_assigned_sku = len(skus_assigned)
                if count_of_assigned_sku > int(mapping[sku]):
                    #We have more of this SKU assigned than defined in the mapping, so lets add the last N (extras) to loose_items using splicing
                    original_trailer_items = skus_assigned[:count_of_assigned_sku - int(mapping[sku])]
>>>>>>> b50fbc74a609463488b8dd6f6d31c8404337fac0
                    for t_item in original_trailer_items:
                        if t_item["contractNumber"] in burnt_contracts:
                            continue
                        #We want to append the original SN to the loose contract entry
                        t_item.update({"originalSN": asset["serialNumber"]})
                        loose_items.append(t_item)
                        burnt_contracts.append(t_item["contractNumber"])
<<<<<<< HEAD
    return loose_items

def generate_contract_move_summary(contracts: list, loose_contracts: list, asset_json: dict, mapping_dict: dict, equalSkus: dict) -> list:
=======

    #If a full contract listing is supplied (A CSV with all licenses (used or unused) with headers contract,model,sku headers at minimum)
    if contracts is not None:
        allocated_contracts = []
        for asset in asset_json["assets"]:
            if asset["contracts"] is None:
                continue
            for contract in asset["contracts"]:
                allocated_contracts.append(contract)
        #Add all unassigned but available contracts and add them to our loose contracts
        unassigned_contracts = [x for x in contracts if x["contract"] not in [y["contractNumber"] for y in allocated_contracts]]
        loose_items.extend([{"originalSN": "N/A", "sku": x["sku"], "contractNumber": x["contract"]} for x in unassigned_contracts])
    return loose_items


def generate_contract_move_summary(loose_contracts: list, asset_json: dict, mapping_dict: dict, equalSkus: dict) -> list:
>>>>>>> b50fbc74a609463488b8dd6f6d31c8404337fac0
    move_transactions = []
    allocated_contracts = []

    for asset in asset_json["assets"]:
        if asset["contracts"] is None:
            continue
        for contract in asset["contracts"]:
            allocated_contracts.append(contract)

<<<<<<< HEAD

    unassigned_contracts = [x for x in contracts if x["contract"] not in [y["contractNumber"] for y in allocated_contracts]]
    loose_contracts.extend([{"originalSN": "N/A", "sku": x["sku"], "contractNumber": x["contract"]} for x in unassigned_contracts])
=======
>>>>>>> b50fbc74a609463488b8dd6f6d31c8404337fac0
    reassigned_contracts = []

    for asset in asset_json["assets"]:
        for mapping in [v for k,v in mapping_dict.items() if k == asset["productModel"]]:
            for sku in mapping:
<<<<<<< HEAD
                equal_skus = []
                if sku in equalSkus:
                    equal_skus = equalSkus[sku]
                skus_assigned = None
                if asset["contracts"] is not None:
                    skus_assigned = [x for x in asset["contracts"] if x["sku"] == sku or x["sku"] in equal_skus]
                count_of_assigned_sku = len(skus_assigned) if skus_assigned is not None else 0
                if count_of_assigned_sku < int(mapping[sku]):
                    #We dont have enough licenses applied
                    shortfall_count = int(mapping[sku]) - count_of_assigned_sku
                    eligble_contracts = [x for x in loose_contracts if (x["sku"] in equal_skus or x["sku"] == sku) and x["contractNumber"] not in reassigned_contracts]
                    for i in range (0, shortfall_count):
                        if len(eligble_contracts) > 0:
=======

                #Build our SKU mappings (e.g. two different types of SKUs which give the same entitlement)
                equal_skus = []
                if sku in equalSkus:
                    equal_skus = equalSkus[sku]

                #Get the SKU's assigned to our current asset
                skus_assigned = [x for x in asset["contracts"] if 
                    (x["sku"] == sku or x["sku"] in equal_skus)]
                count_of_assigned_sku = len(skus_assigned)

                if count_of_assigned_sku < int(mapping[sku]):
                    #We dont have enough licenses applied

                    shortfall_count = int(mapping[sku]) - count_of_assigned_sku

                    #Get some eligble contracts that havent already been used
                    eligble_contracts = [x for x in loose_contracts if (x["sku"] in equal_skus or x["sku"] == sku) and x["contractNumber"] not in [z["contractNumber"] for z in reassigned_contracts]]
                    for i in range (0, shortfall_count):
                        if i + 1 > len(eligble_contracts):
                            #Run out of eligble contracts
                            move_transactions.append({"originalSN": "N/A", "toSN": asset["serialNumber"], "sku": selected_contract["sku"], "contractNumber": "NONE AVAILABLE",
                                "model": asset["productModel"]})
                            continue
                        if len(eligble_contracts) > 0:
                            #We have some free contracts, lets add them to move_transactions
>>>>>>> b50fbc74a609463488b8dd6f6d31c8404337fac0
                            selected_contract = eligble_contracts[i]
                            reassigned_contracts.append(selected_contract)
                            eligble_contracts.remove(selected_contract)
                            move_transactions.append({"originalSN": selected_contract["originalSN"], "toSN": asset["serialNumber"], "sku": selected_contract["sku"], "contractNumber": selected_contract["contractNumber"],
                                "model": asset["productModel"]})
<<<<<<< HEAD
                            
=======
                        else:
                            #No eligble contracts at all
                            move_transactions.append({"originalSN": "N/A", "toSN": asset["serialNumber"], "sku": selected_contract["sku"], "contractNumber": "NONE AVAILABLE",
                                "model": asset["productModel"]})
                                
>>>>>>> b50fbc74a609463488b8dd6f6d31c8404337fac0


    return move_transactions


def main() -> None:
    parser = argparse.ArgumentParser()

    #parser.add_argument("action", choices=["export_assignments", "generate_contract_move"], default="export-assignments")
    parser.add_argument("--account-id", help="The FortiCare account ID")
    parser.add_argument("--api-token", help="The FortiCare account API token")
    parser.add_argument("--output-csv", default="output.csv")
    subparsers = parser.add_subparsers(dest="action")
    export_parser = subparsers.add_parser("export_assignments")
    

    move_parser = subparsers.add_parser("generate_contract_move")
    move_parser.add_argument("--input_contracts", help="Input contracts CSV generated by forti_license_parser.py")
    move_parser.add_argument("-m", "--mapping", action="append")
    move_parser.add_argument("-e", "--equal-sku", action="append")
<<<<<<< HEAD
    move_parser.add_argument("--output-filename", default="contract_moves.csv")
=======
>>>>>>> b50fbc74a609463488b8dd6f6d31c8404337fac0


    args = parser.parse_args()

    account_id, api_token = None, None

    if not args.account_id or not args.api_token:
        import credentials
        account_id = credentials.username
        api_token = credentials.password
    else:
        account_id = args.account_id
        api_token = args.api_token

    token = get_oauth_token(account_id, api_token)
    if 'access_token' in token:
        token = token["access_token"]
    else:
        raise Exception("Could not obtain OAuth token\nToken object: " + str(token))

    if args.action == "export_assignments":
        data = get_device_list(token)
        write_assets_to_csv(args.output_csv, data)
    elif args.action == "generate_contract_move":
        #Generate our SKU -> Entitlements mapping
        mappings = {}
        for mapping in args.mapping:
            split_arguments = mapping.split(":")

            if len(split_arguments) != 3:
                raise Exception("Invalid mapping argument " + str(mapping))
            if split_arguments[0] not in mappings:
                mappings[split_arguments[0]] = {}

            mappings[split_arguments[0]][split_arguments[1]] = split_arguments[2]
        
        equal_skus = {}
        #Generate our SKU equivalencies
<<<<<<< HEAD
        for equal in args.equal_sku:
            split_arguments = equal.split(":")

            if len(split_arguments) != 2:
                raise Exception("Invalid SKU equal mapping " + str(equal))
            
            #Create our SKU : [EqualSKU1, EqualSKU2] structure
            if split_arguments[0] not in equal_skus:
                equal_skus[split_arguments[0]] = []
            if split_arguments[1] not in equal_skus[split_arguments[0]]:
                equal_skus[split_arguments[0]].append(split_arguments[1])

            #Do the reverse (EqualSKU1: SKU)
            if split_arguments[1] not in equal_skus:
                equal_skus[split_arguments[1]] = []
            if split_arguments[0] not in equal_skus[split_arguments[1]]:
                equal_skus[split_arguments[1]].append(split_arguments[0])
=======
        if args.equal_sku is not None:
            for equal in args.equal_sku:
                split_arguments = equal.split(":")

                if len(split_arguments) != 2:
                    raise Exception("Invalid SKU equal mapping " + str(equal))
                
                #Create our SKU : [EqualSKU1, EqualSKU2] structure
                if split_arguments[0] not in equal_skus:
                    equal_skus[split_arguments[0]] = []
                if split_arguments[1] not in equal_skus[split_arguments[0]]:
                    equal_skus[split_arguments[0]].append(split_arguments[1])

                #Do the reverse (EqualSKU1: SKU)
                if split_arguments[1] not in equal_skus:
                    equal_skus[split_arguments[1]] = []
                if split_arguments[0] not in equal_skus[split_arguments[1]]:
                    equal_skus[split_arguments[1]].append(split_arguments[0])
>>>>>>> b50fbc74a609463488b8dd6f6d31c8404337fac0

            

        asset_json = get_device_list(token)
<<<<<<< HEAD
        contracts = get_contract_list(args.input_contracts)
        loose_contracts = get_loose_contracts(asset_json, mappings, equal_skus)
        move_summary = generate_contract_move_summary(contracts, loose_contracts, asset_json, mappings, equal_skus)
=======

        contracts = None
        if args.input_contract is not None:
            contracts = get_contract_list(args.input_contracts)
        loose_contracts = get_loose_contracts(asset_json, mappings, equal_skus, contracts)
        move_summary = generate_contract_move_summary(loose_contracts, asset_json, mappings, equal_skus)
>>>>>>> b50fbc74a609463488b8dd6f6d31c8404337fac0

        with open(args.output_filename, "w", newline='') as f:
            writer = DictWriter(f, fieldnames=["originalSN", "model", "contractNumber", "sku", "toSN", "Description"])
            writer.writeheader()
            writer.writerows(move_summary)
        


        
        
main()
    

