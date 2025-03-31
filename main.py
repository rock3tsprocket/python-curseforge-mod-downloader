import os
from urllib import parse

import httpx


def clear_console():
    os.system("cls" if os.name == "nt" else "clear")


def user_input():
    search_term = input("Enter a search term (or q to exit): ")

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

    mod_choice = 0
    if len(request_json["hits"]) > 1:
        print("Select which mod you want to download:\n")
        for i, item in enumerate(request_json["hits"]):
            print(f"{i + 1}: {item['title']} by {item['author']}")
        mod_choice = (
            int(input("Enter the number of the mod you want to download: ")) - 1
        )

    item = request_json["hits"][mod_choice]
    project_id = item["project_id"]
    project_slug = item["slug"]
    game_versions = item["versions"]

    download(game_versions, project_id, project_slug)


# User version selection function
def download(versions: list, project_id: str, project_slug: str):
    # Invert list
    versions.reverse()

    # Run until we get a valid response
    while True:
        print(f"Supported MC versions: {', '.join(versions)}")
        user_version = str(
            input(
                "\nWhat version would you like to download for? (leave blank for latest): "
            )
        )
        if user_version == "":
            user_version = versions[0]

        if user_version in versions:
            clear_console()
            print(f"Downloading for {user_version}...")

            versions_request = httpx.get(
                f"https://api.modrinth.com/v2/project/{project_id}/version",
                params={
                    "game_versions": [
                        user_version,
                    ]
                },
            )
            versions_request.raise_for_status()

            versions_json = versions_request.json()

            versions_json = [
                version
                for version in versions_json
                if user_version in version["game_versions"]
            ]

            if len(versions_json) == 0:
                print(f"No versions found for {user_version}. Please try again.\n")
                continue

            if len(versions_json) > 1:
                print(
                    f"Multiple versions found for {user_version}. Please select one:\n"
                )
                for i, version in enumerate(versions_json):
                    print(f"{i + 1}: {version['name']}")
                while True:
                    version_selection = input(
                        "Enter the number of the version you want to download: "
                    )
                    try:
                        version_selection = int(version_selection) - 1
                        if version_selection < 0 or version_selection >= len(
                            versions_json
                        ):
                            raise ValueError
                        break
                    except ValueError:
                        print("Invalid input. Please enter a number.")

            version = versions_json[version_selection]

            if len(version["files"]) == 0:
                print(f"No files found for {user_version}. Please try again.\n")

            file_selection = 0
            if len(version["files"]) > 1:
                print(f"Multiple files found for {user_version}. Please select one:\n")
                for i, file in enumerate(version["files"]):
                    print(f"{i + 1}: {file['filename']}")
                while True:
                    file_selection = input(
                        "Enter the number of the file you want to download: "
                    )
                    try:
                        file_selection = int(file_selection) - 1
                        if file_selection < 0 or file_selection >= len(
                            version["files"]
                        ):
                            raise ValueError
                        break
                    except ValueError:
                        print("Invalid input. Please enter a number.")

            file = version["files"][file_selection]
            file_download = file["url"]
            file_name = file["filename"]

            os.makedirs(f"downloads/{project_slug}", exist_ok=True)

            with open(f"downloads/{project_slug}/{file_name}", "wb") as output_file:
                output_file.write(httpx.get(file_download).content)

            print(
                f"Successfully downloaded mod to downloads/{project_slug}/{file_name}."
            )

            # This is where you would handle downloading, for now we will just exit
            exit()
        else:
            print("\nVersion not supported. Please try again.\n")


# Run the program
if __name__ == "__main__":
    while True:
        user_input()
