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

def get_loose_contracts(asset_json: dict, mapping_dict: dict) -> list:
    loose_items = []
    for asset in asset_json["assets"]:
        #For every instance of our mapping dictionary if it matches our current asset model
        for mapping in [v for k,v in  mapping_dict.items() if k == asset["productModel"]]:
            for sku in mapping:
                #Get the currently assigned contracts of type SKU X
                skus_assigned = [x for x in asset["contracts"] if x["sku"] == sku]
                count_of_assigned_sku = len(skus_assigned)
                if count_of_assigned_sku > int(mapping[sku]):
                    #We have more of this SKU assigned than defined in the mapping, so lets add the last N (extras) to loose_items using splicing
                    original_trailer_items = [skus_assigned[-(count_of_assigned_sku - int(mapping[sku]))]]
                    for t_item in original_trailer_items:
                        #We want to append the original SN to the loose contract entry
                        t_item.update({"originalSN": asset["serialNumber"]})
                        loose_items.append(t_item)
    return loose_items

def generate_contract_move_summary(contracts: list, loose_contracts: list, asset_json: dict, mapping_dict: dict) -> list:
    move_transactions = []
    allocated_contracts = []
    for asset in asset_json["assets"]:
        for mapping in [v for k,v in mapping_dict.items() if k == asset["productModel"]]:
            for sku in mapping:
                skus_assigned = [x for x in asset["contracts"] if x["sku"] == sku]
                count_of_assigned_sku = len(skus_assigned)
                if count_of_assigned_sku < int(mapping[sku]):
                    #We dont have enough licenses applied
                    free_contracts = [x for x in loose_contracts if x not in allocated_contracts and x["sku"] == sku]
                    free_contracts_counter = len(free_contracts)
                    for i in range(0, int(mapping[sku]) - count_of_assigned_sku):
                        allocated_contracts.append([free_contracts[i]])
                        free_contracts_counter -= 1
                        move_transactions.append({"fromSN": free_contracts[i]["originalSN"], "contract": free_contracts[i]["contractNumber"], "toSN": asset["serialNumber"]})
                        if free_contracts_counter <= 0:
                            break
    return move_transactions


def main() -> None:
    parser = argparse.ArgumentParser()

    #parser.add_argument("action", choices=["export_assignments", "generate_contract_move"], default="export-assignments")
    parser.add_argument("--account-id", help="The FortiCare account ID")
    parser.add_argument("--api-token", help="The FortiCare account API token")
    subparsers = parser.add_subparsers(dest="action")
    export_parser = subparsers.add_parser("export_assignments")
    export_parser.add_argument("--output-csv", default="output.csv")

    move_parser = subparsers.add_parser("generate_contract_move")
    move_parser.add_argument("input_contracts", help="Input contracts CSV generated by forti_license_parser.py")
    move_parser.add_argument("-m", "--mapping", action="append")


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
        mappings = {}
        for mapping in args.mapping:
            split_arguments = mapping.split(":")
            if len(split_arguments) != 3:
                raise Exception("Invalid mapping argument " + str(mapping))
            if split_arguments[0] not in mappings:
                mappings[split_arguments[0]] = {}
            mappings[split_arguments[0]][split_arguments[1]] = split_arguments[2]

        asset_json = get_device_list(token)
        contracts = get_contract_list(args.input_contracts)
        loose_contracts = get_loose_contracts(asset_json, mappings)
        print(generate_contract_move_summary(contracts, loose_contracts, asset_json, mappings))

        
        
main()
    

