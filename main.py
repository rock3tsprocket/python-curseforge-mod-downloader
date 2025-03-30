import httpx
from urllib import parse
import os


# User input function
def user_input():
    search_term = input("Enter a search term (q to exit): ")

    if search_term.lower() == "q":
        print("Exiting...")
        exit()
    else:
        user_selection(search_term)


# User mod selection function
def user_selection(search_term: str):
    print("Searching...")

    # Perform the search using the search term, ensure search term is URL encoded
    request = httpx.get(
        f"https://api.modrinth.com/v2/search?query={parse.quote_plus(search_term)}"
    )
    request.raise_for_status()

    request_json = request.json()
    if len(request_json["hits"]) == 0:  # No results found
        print("No results found.")
    else:
        # Cap hits at 10
        request_json["hits"] = request_json["hits"][:10]
        print(f"Showing {len(request_json['hits'])} results.\n")

        for i, item in enumerate(request_json["hits"]):
            print(f"Result {i + 1}:")
            print(f"Title: {item['title']}")
            print(f"By: {item['author']}")
            print(f"Description: {item['description']}")

            # Run until we get a valid response
            while True:
                is_this_it = input("Is this the one you want? (y/n/s/q): ").lower()

                if is_this_it == "y":  # Yes
                    os.system(
                        "cls" if os.name == "nt" else "clear"
                    )  # Cross platform clear
                    print(f"You have selected {item['title']}.")

                    project_request = httpx.get(
                        f"https://api.modrinth.com/v2/project/{item['project_id']}"
                    )
                    project_request.raise_for_status()

                    project_json = project_request.json()
                    user_version(project_json["game_versions"])
                elif is_this_it == "n":  # No
                    os.system(
                        "cls" if os.name == "nt" else "clear"
                    )  # Cross platform clear
                    break
                elif is_this_it == "s":  # Search again
                    break
                elif is_this_it == "q":  # Quit
                    print("Exiting...")
                    exit()
                else:  # Invalid input
                    print("Invalid input. Please enter y, n, s, or q.")

            # Stop going through results if user input is search again
            if is_this_it == "s":
                os.system("cls" if os.name == "nt" else "clear")  # Cross platform clear
                break

        # Only show please try again if user input doesn't equal search again
        if is_this_it != "s":
            print("Please try again.\n")


# User version selection function
def user_version(versions: list):
    # Invert list
    versions.reverse()

    # Run until we get a valid response
    while True:
        print(f"Supported MC versions: {', '.join(versions)}")
        user_version = str(input("\nWhat version would you like to download for? "))

        if user_version in versions:
            os.system("cls" if os.name == "nt" else "clear")  # Cross platform clear
            print(f"Downloading for {user_version}...")

            # This is where you would handle downloading, for now we will just exit
            exit()
        else:
            print("\nVersion not supported. Please try again.\n")


# Run the program
if __name__ == "__main__":
    while True:
        user_input()
