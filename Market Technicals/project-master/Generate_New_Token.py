import requests
import warnings


def new_token():
    warnings.filterwarnings("ignore")

    client_id = "65B13E97-3F1C-4B4B-A6A2-6DE31237780B"
    username = "webapi-kelag"
    password = "letnom2017"

    url = "https://api.montelnews.com/gettoken"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    data = {
        "grant_type": "password",
        "client_Id": client_id,
        "username": username,
        "password": password,
    }

    # Make the POST request to get the token
    response = requests.post(url, headers=headers, data=data, verify=False)

    token_data = response.json()
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response to extract the access token
        token = response.json().get("access_token")
        # print(f"Token: {token}")
        # Save the token to a file
        with open(
            "C:/Users/Z_LAME/Desktop/Crawler/Market Technicals/project-master/access_token.txt",
            "w",
        ) as file:
            file.write(token)
    else:
        print(f"Failed to generate token. Status code: {response.status_code}")
        print(f"Response: {response.text}")


new_token()
