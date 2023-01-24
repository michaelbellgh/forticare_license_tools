from csv import DictWriter
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


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("--output-csv", default="output.csv")
    parser.add_argument("--account-id", help="The FortiCare account ID")
    parser.add_argument("--api-token", help="The FortiCare account API token")

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

    data = get_device_list(token)
    write_assets_to_csv(args.output_csv, data)

main()
    
