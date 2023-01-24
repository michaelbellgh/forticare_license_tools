from csv import DictWriter
import requests

import credentials


def get_oauth_token(api_username: str, api_password: str, client_id: str = "assetmanagement", base_url: str = "https://customerapiauth.fortinet.com/api/v1/oauth/token/") -> dict:
    body = {"username": api_username,
      "password": api_password,
      "client_id": "assetmanagement",
      "grant_type": "password"}
    
    response = requests.post(base_url, json=body).json()
    return response
    

def get_device_list(oauth_token: str, serial_num_filter: str = "F", base_url: str ="https://support.fortinet.com/ES/api/registration/v3/products/list") -> dict:
    response = requests.post(base_url, headers={"Authorization":  "Bearer " + oauth_token}, json={"serialNumber": serial_num_filter})
    return response.json()


#def write



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


token = get_oauth_token(credentials.username, credentials.password)["access_token"]
data = get_device_list(token)
write_assets_to_csv("output.csv", data)
