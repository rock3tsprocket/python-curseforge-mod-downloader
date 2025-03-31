import httpx
from urllib import parse
import os

def clear_console():
    os.system("cls" if os.name == "nt" else "clear")

def user_input():
    search_term = input("Enter a search term (q to exit): ")

    if search_term.lower() == "q":
        print("Exiting...")
        exit()
    else:
        user_selection(search_term)

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
        return
    
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
            search_successful = input("Is this the project you want? (Yes/No/Search again/Quit): ").lower()
            clear_console()
            match search_successful:
                case "y":
                    print(f"You have selected {item['title']}.")
    
                    project_request = httpx.get(
                        f"https://api.modrinth.com/v2/project/{item['project_id']}"
                    )
                    project_request.raise_for_status()
    
                    project_json = project_request.json()
                    download(project_json["game_versions"], item['project_id'])
                case "n" | "s": break
                case "q":
                    print("Exiting...")
                    exit()
                case _:
                    print("Invalid input. Please enter y, n, s, or q.")

        # Stop going through results if user input is search again
        if search_successful == "s":
            clear_console()
            break

    # Only show please try again if user input doesn't equal search again
    if search_successful != "s":
        print("Please try again.\n")


# User version selection function
def download(versions: list, project_id: str):
    # Invert list
    versions.reverse()

    # Run until we get a valid response
    while True:
        print(f"Supported MC versions: {', '.join(versions)}")
        user_version = str(input("\nWhat version would you like to download for? "))

        if user_version in versions:
            clear_console()
            print(f"Downloading for {user_version}...")

            versions_request = httpx.get(f"https://api.modrinth.com/v2/project/{item['project_id']}/version", params={'game_versions': [user_version,]})
            versions_request.raise_for_status()

            version_id = versions_request.json()[0]['id']

            file = https.get(f"https://api.modrinth.com/v2/version/{version_id}").json()['files'][0]
            file_download = file['url']
            file_name = file['name']

            with open(file_name, 'wb') as output_file:
                output_file.write(https.get(file_download).content)

            print(f"Successfully downloaded mod to {file_name}.") 
            
            # This is where you would handle downloading, for now we will just exit
            exit()
        else:
            print("\nVersion not supported. Please try again.\n")


# Run the program
if __name__ == "__main__":
    while True:
        user_input()
