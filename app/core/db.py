from typing import Optional, Tuple, Any
from models import Transaction, User
import json
import requests

def add_transaction(transaction: Transaction) -> Optional[str]:
    """Generate POST API Request to ResDB"""

    query = f"""
    mutation {{
        postTransaction(data: {{
            operation: "CREATE"
            amount: {transaction.amount},
            signerPublicKey: "{transaction.sender}",
            signerPrivateKey: "{transaction.sender_private_key}",
            recipientPublicKey: "{transaction.receiver}",
            asset: \"\"\"{json.dumps(transaction.asset)}\"\"\"
        }}) {{
                id
            }}
        }}
    """
    
    update_balances(transaction)

    response = requests.post(url = "http://localhost:8000/graphql", json = {"query": query}) 
    print("response status code: ", response.status_code)
    if response.status_code == 200: 
        print("response : ",response.content)
        return None
    else:
        return str(response)
    
def add_user(user: User) -> Tuple[Optional[str], Optional[str]]:
    """Generate POST API Request to ResDB"""

    asset = {
        "data": {
            "method": "create_user",
            "id": user.id,
            "username": user.username,
            "password": user.password,
            "timestamp": str(user.signup_ts),
            "name": user.name,
            "public_key": user.public_key,
            "private_key": user.private_key,
            "friends": user.friends,
            "balances": user.balances
        }
    }

    # Serialize the asset dictionary to a JSON-formatted string
    asset_json = json.dumps(asset)
    print(asset_json)
    print("*************************************************************")
    # Construct the GraphQL mutation query
    query = f"""
    mutation {{
        postTransaction(data: {{
            operation: "CREATE",
            amount: 1,
            signerPublicKey: "{user.public_key}",
            signerPrivateKey: "{user.private_key}",
            recipientPublicKey: "{user.public_key}",
            asset: \"\"\"{json.dumps(asset)}\"\"\",
        }}) {{
            id
        }}
    }}
    """

    response = requests.post(url = "http://localhost:8000/graphql", json = {"query": query}) 
    print("response status code: ", response.status_code)
    if response.status_code == 200: 
        print("response : ",response.content)
        res = json.loads(response.content)
        return (res["data"]["postTransaction"]["id"], None)
    else:
        return (None, str(response))

def update_balances(transaction: Transaction) -> Optional[str]:
    query = f"""
    query {{
        getFilteredTransactions(filter: {{
            ownerPublicKey: "{transaction.sender}",
            recipientPublicKey: "{transaction.sender}"
        }}) {{
            id
            asset
        }}
    }}
    """

    response = requests.post(url = "http://localhost:8000/graphql", json = {"query": query}) 
    print("response status code: ", response.status_code)
    if response.status_code == 200:
        print("response : ",response.content)
        id = response.json()['data']['getFilteredTransactions'][0]['id']
        asset = response.json()['data']['getFilteredTransactions'][0]['asset']
        
        updated = False
        for bal in asset['data']['balances']:
            if bal['username'] == transaction.asset['data']['username']:
                bal['balance'] += transaction.asset['data']['balance']
                updated = True

        if not updated:
            asset['data']['balances'].append({
                "username": transaction.asset['data']['username'],
                "balance": transaction.asset['data']['balance']
            })
        
        query = f"""
        mutation {{
            updateTransaction(data: {{
                id: {id},
                operation: "",
                amount: {transaction.amount},
                signerPublicKey: "{transaction.sender}",
                signerPrivateKey: "{transaction.sender_private_key}",
                recipientPublicKey: "{transaction.sender}",
                asset: \"\"\"{json.dumps(asset)}\"\"\",
            }}) {{
                id
            }}
        }}
        """

        response = requests.post(url = "http://localhost:8000/graphql", json = {"query": query}) 
        print("response status code: ", response.status_code)
        if response.status_code == 200: 
            print("response : ",response.content)
            return None
        else:
            return str(response)
        
def get_user_details(id: str) -> Any:
    # print("Block id in db py",id)
    try:
        print("inside get user sqlite")
        query = f"""
        query {{
            getTransaction(id: "{id}") {{
                id
                asset
            }}
        }}
        """
        # print("after query")
        response = requests.post(url = "http://localhost:8000/graphql", json = {"query": query})
        # print("after response", response.content) 
        if response.status_code == 200:
            outer_dict = json.loads(response.content)
            # print("*******************Res******************")
            # print(response.content)
            asset_str = outer_dict['data']['getTransaction']['asset'].replace("'", '"')
            asset_dict = json.loads(asset_str)
            # print("***********This is what you want it to be like***********")
            # print(asset_dict)
            return asset_dict['data']
        else:
            return (None, str(response.status_code))
    except:
        return "Error in get_user_detail"

# def add_friend(id: str, friend: str) -> Any:
#     # Get user details
#     try:
#         user_asset = get_user_details(id)
        
        
#         # Update friends list
#         friends_list = user_asset['friends']
#         friends_list.append(friend)
#         print("Friend list",friends_list)
#         # Construct query
#         user_asset['friends']=friends_list
#         # print("Asset",user_asset)
#         print("*****************This is what we actually have***************")
#         asset_we_put={"data":user_asset}
#         print(asset_we_put)
#         query = f"""
#         mutation {{
#             updateTransaction(data: {{
#                 id: "{id}",
#                 operation: "",
#                 amount: 1,
#                 signerPublicKey: {user_asset['public_key']},
#                 signerPrivateKey: {user_asset['private_key']},
#                 recipientPublicKey: {user_asset['public_key']},
#                 asset: {asset_we_put},
#             }}) {{
#                 id
#                 asset
#             }}
#         }}
#         """
        
#         response = requests.post(url="http://localhost:8000/graphql", json={"query": query})
#         print(response)
#         print("Response code", response.status_code)
#         if response.status_code == 200:
#             print("response: ", response.content)
#             return response.content
#         else:
#             return response.content
#     except:
#         return "Hellow Bossie"

def add_friend(id: str, friend: str) -> Any:
    try:
        user_asset = get_user_details(id)
        
        # Update friends list
        friends_list = user_asset['friends']
        friends_list.append(friend)
        print("Friend list", friends_list)
        
        # Update asset
        user_asset['friends'] = friends_list
        asset_we_put = {"data": user_asset}
        
        # Convert asset to JSON string and escape it properly
        asset_json = json.dumps(asset_we_put)
        # print("id in add friend",id)
        query = f"""
        mutation {{
            updateTransaction(data: {{
                id: "{id}"
                operation: ""
                amount: 1,
                signerPublicKey: "{user_asset['public_key']}",
                signerPrivateKey: "{user_asset['private_key']}",
                recipientPublicKey: "{user_asset['public_key']}",
                asset: \"\"\"{asset_json}\"\"\"
            }}) {{
                id
                asset
            }}
        }}
        """
        
        response = requests.post(url="http://localhost:8000/graphql", json={"query": query})
        # print(response)
        # print("Response code", response.status_code)
        if response.status_code == 200:
            # print("response: ", response.content)
            dict = json.loads(response.content)
            new_id=dict['data']['updateTransaction']['id']
            print("New id",new_id)
            print(dict)
            return response.content
        else:
            return response.content
    except Exception as e:
        print("Error:", e)  # Better error handling
        return f"Error occurred: {str(e)}"