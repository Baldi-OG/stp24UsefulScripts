import time

import requests

# Constants
base_url = "https://stpellar.uniks.de/api/v1"
login_ep = "/auth/login"
games_ep = "/games"
base_header = {
    "accept": "application/json",
    "Content-Type": "application/json"
}
auth_header = {}

# Base variables
auth_token = ""
user_id = ""
user_name = ""


# Api calls


def login(_username, _password):
    """
    This functions logs the user into the server.

    :param _username:
    :param _password:
    """
    global auth_token, user_id, username, auth_header           # This is probably horrible style, but I am lazy
    url = base_url + login_ep
    data = {
        "name": _username,
        "password": _password
    }
    try:
        response = requests.post(url=url, headers=base_header, json=data)
        response.raise_for_status()
        rsp_json = response.json()

        auth_token = rsp_json['accessToken']
        user_id = rsp_json['_id']
        username = rsp_json['name']
        auth_header = {
            "accept": "application/json",
            "Authorization": f"Bearer {auth_token}"

        }

        print("\n\n\n\n")
        print(f"Welcome {username}!\n")
    except requests.exceptions.HTTPError as http_err:
        print(f"Http error occurred {http_err}")
    except Exception as err:
        print(f"An error occurred {err}")


def cleanup_games():
    """
    This will automatically clean up all games created by the user.
    Could take a little but of time, since there is a rate limit.
    """
    all_games = []
    my_games = []
    url = base_url + games_ep

    try:
        response = requests.get(url=url, headers=auth_header)
        response.raise_for_status()

        all_games = response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"Http error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")

    for game in all_games:
        if game['owner'] == user_id:
            my_games.append(game)

    for game in my_games:

        url = base_url + games_ep + f"/{game['_id']}"

        try:
            response = requests.delete(url=url, headers=auth_header)
            response.raise_for_status()

            print(f"Deleted {game['name']}")
        except requests.exceptions.HTTPError as http_err:
            print(f"Http error {http_err.response.status_code} occurred")
            print("Waiting 5 seconds (rate limit)")
            time.sleep(5)
        except Exception as err:
            print(f"An error occurred: {err}")

        # Trying not to get fucked by rate limit
        time.sleep(1)

    print("Execution finished!")


if __name__ == '__main__':

    while auth_token == "":
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        login(username, password)

    print("What would you like to do?")
    print("1. Cleanup games (Removes all games created by you)")
    print("More scripts coming soon! (maybe)")

    while True:
        selection = input(">")

        match selection:

            case "0":
                exit(0)
            case "1":
                cleanup_games()
            case _:
                print("\n\n\n\n\n")
                print("Please enter a correct number")
                print("What would you like to do?")
                print("0. Exit")
                print("1. Cleanup games (Removes all games created by you)")
