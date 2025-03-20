import requests

with open("access_token.txt", "r") as f:
    token = f.read().strip()


def get_ohlc():

    # Prompt user for input variables
    symbolkey = input("Enter symbol key: ")
    fields_input = input("Enter fields (comma-separated): ")
    fields = fields_input.split(",")
    from_date = input("Enter from date (YYYY-MM-DD): ")
    to_date = input("Enter to date (YYYY-MM-DD): ")
    sort = input("Enter sort order: ")
    insertElementsWhenDataMissing = input(
        "Insert elements when data missing (Never/Always): "
    )
    continuous = input("Enter continuous (true/false): ")

    headers = {"Authorization": f"Bearer {token}", "AcceptEncoding": "deflate"}

    # Construct the fields part of the URL
    fields_str = "".join([f"&fields={field.strip()}" for field in fields])

    # Construct the full URL
    url = (
        f"https://api.montelnews.com/derivatives/ohlc/get?"
        f"symbolKey={symbolkey}"
        f"{fields_str}"
        f"&fromDate={from_date}"
        f"&toDate={to_date}"
        f"&sortType={sort}"
        f"&insertElementsWhenDataMissing={insertElementsWhenDataMissing}"
        f"&continuous={continuous}"
    )

    response = requests.get(url, headers=headers, verify=False)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        user_input = input("Please provide further instructions: ")
        return user_input
