"""Modrinth Mod Downloader
This script allows users to search for and download mods from the Modrinth API, through a convenient command-line interface.
It provides functionality to search for mods, select a specific version, and download the mod files to a specified directory.
"""

import os
import sys
from pathlib import Path
from typing import List

import httpx


def clear_console():
    """Clear the console screen."""
    os.system("cls" if os.name == "nt" else "clear")


def help():
    """Print the logo of the application."""
    print("""
███╗░░░███╗░█████╗░██████╗░██████╗░██╗███╗░░██╗████████╗██╗░░██╗  ███╗░░░███╗░█████╗░██████╗░
████╗░████║██╔══██╗██╔══██╗██╔══██╗██║████╗░██║╚══██╔══╝██║░░██║  ████╗░████║██╔══██╗██╔══██╗
██╔████╔██║██║░░██║██║░░██║██████╔╝██║██╔██╗██║░░░██║░░░███████║  ██╔████╔██║██║░░██║██║░░██║
██║╚██╔╝██║██║░░██║██║░░██║██╔══██╗██║██║╚████║░░░██║░░░██╔══██║  ██║╚██╔╝██║██║░░██║██║░░██║
██║░╚═╝░██║╚█████╔╝██████╔╝██║░░██║██║██║░╚███║░░░██║░░░██║░░██║  ██║░╚═╝░██║╚█████╔╝██████╔╝
╚═╝░░░░░╚═╝░╚════╝░╚═════╝░╚═╝░░╚═╝╚═╝╚═╝░░╚══╝░░░╚═╝░░░╚═╝░░╚═╝  ╚═╝░░░░░╚═╝░╚════╝░╚═════╝░

██████╗░░█████╗░░██╗░░░░░░░██╗███╗░░██╗██╗░░░░░░█████╗░░█████╗░██████╗░███████╗██████╗░
██╔══██╗██╔══██╗░██║░░██╗░░██║████╗░██║██║░░░░░██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗
██║░░██║██║░░██║░╚██╗████╗██╔╝██╔██╗██║██║░░░░░██║░░██║███████║██║░░██║█████╗░░██████╔╝
██║░░██║██║░░██║░░████╔═████║░██║╚████║██║░░░░░██║░░██║██╔══██║██║░░██║██╔══╝░░██╔══██╗
██████╔╝╚█████╔╝░░╚██╔╝░╚██╔╝░██║░╚███║███████╗╚█████╔╝██║░░██║██████╔╝███████╗██║░░██║
╚═════╝░░╚════╝░░░░╚═╝░░░╚═╝░░╚═╝░░╚══╝╚══════╝░╚════╝░╚═╝░░╚═╝╚═════╝░╚══════╝╚═╝░░╚═╝""")  # via https://fsymbols.com/generators/carty/

    print(
        sys.modules[__name__].__doc__
    )  # See https://stackoverflow.com/questions/990422/how-to-get-a-reference-to-current-modules-attributes-in-python for how this works
    print("You can exit the program at any time by entering 'q' when prompted.\n")
    print("Usage:")
    print("1. Search for a mod by name.")
    print("2. Select the mod you want to download from the search results.")
    print("3. Select the Minecraft version you want to download for.")
    print("4. Select the mod version you want to download.")
    print("5. Select the file you want to download.")
    print(
        "6. The mod will be downloaded to the 'python-modrinth-mod-downloader/downloads' directory in your home folder.\n"
    )
    print(
        "Note: This program is not affiliated with Modrinth in any way. It is a simple command-line interface for downloading mods via the Modrinth API.\n"
    )


def prompt_user(prompt: str) -> str:
    """Prompt the user for input and return the response.
    Args:
        prompt (str): The prompt to display to the user.

    Returns:
        str: The user's response.
    """
    response = input(prompt).strip()
    if response.lower() == "q":
        print("Exiting...")
        exit()
    return response


def search_interface() -> bool:
    """Prompt the user for a search term and let them select a mod to download.
    Returns:
        bool: True if the search and download were succesful, False otherwise.
    """
    clear_console()
    while True:
        search_term = prompt_user("Enter the name of the mod you want to search for: ")
        if search_term == "":
            print("No search term provided. Please provide a search term.")
            continue
        print("Searching...")
        break

    # Perform the search using the search term, ensure search term is URL encoded
    request = httpx.get(
        "https://api.modrinth.com/v2/search", params={"query": search_term}
    )
    try:
        request.raise_for_status()
    except httpx.HTTPStatusError as e:
        print(f"Search failed: {e.response.status_code} - {e.response.text}")
        return False

    request_json = request.json()
    if len(request_json["hits"]) == 0:  # No results found
        print("No results found.")
        return False

    # Cap hits at 10 - this is no longer necessary, as the user now chooses the mod to download using a more compact interface.
    # request_json["hits"] = request_json["hits"][:10]

    print(f"Showing {len(request_json['hits'])} results.\n")

    mod_choice = 0
    if len(request_json["hits"]) > 1:
        print("Select which mod you want to download:\n")
        for i, item in enumerate(request_json["hits"]):
            print(f"{i + 1}: {item['title']} by {item['author']}")
        mod_choice = (
            int(prompt_user("Enter the number of the mod you want to download: ")) - 1
        )

    item = request_json["hits"][mod_choice]
    project_id = item["project_id"]
    project_slug = item["slug"]
    game_versions = item["versions"]

    download(game_versions, project_id, project_slug)


# User version selection function
def download(versions: List[str], project_id: str, project_slug: str) -> bool:
    """Download a mod given a list of versions, a project ID, and a project slug.
    Args:
        versions (List[str]): A list of versions to download.
        project_id (str): The ID of the project.
        project_slug (str): The slug of the project.

    Returns:
        bool: True if the download was successful, False otherwise.
    """
    # Invert list
    versions.reverse()

    pretty_versions_dict = {}
    for version in versions:
        base_version = ".".join(version.split(".")[:2])
        if base_version in pretty_versions_dict:
            pretty_versions_dict[base_version].append(version)
        else:
            pretty_versions_dict[base_version] = [version]

    print("Supported MC versions:")
    for base_version, sub_versions in pretty_versions_dict.items():
        print(f"{base_version}:\n- {', '.join(sub_versions)}")

    # Run until we get a valid response
    while True:
        user_version = str(
            prompt_user(
                "\nWhat version would you like to download for? (leave blank for latest): "
            )
        ).strip()
        if user_version == "":
            user_version = versions[0]

        if user_version not in versions:
            print(
                f"Version {user_version} not supported. Supported versions are: {', '.join(versions)}"
            )
            continue

        clear_console()
        print(f"Downloading for {user_version}...")

        mod_versions_request = httpx.get(
            f"https://api.modrinth.com/v2/project/{project_id}/version",
            params={
                "game_versions": [
                    user_version,
                ]
            },
        )

        try:
            mod_versions_request.raise_for_status()
        except httpx.HTTPStatusError as e:
            print(f"Search failed: {e.response.status_code} - {e.response.text}")
            return False

        mod_versions_list: List[dict] = mod_versions_request.json()

        mod_versions_list = [
            version
            for version in mod_versions_list
            if user_version in version["game_versions"]
        ]

        if len(mod_versions_list) == 0:
            print(f"No versions found for {user_version}. Please try again.\n")
            continue

        print(f"Multiple versions found for {user_version}. Please select one:\n")
        mod_versions_list = sorted(
            mod_versions_list, key=lambda x: sorted(x["loaders"])[0]
        )

        for i, version in enumerate(mod_versions_list):
            print(f"{i + 1}: {version['name']}")
        while True:
            version_selection = prompt_user(
                "Enter the number of the version you want to download (or blank for the first one): "
            )
            try:
                if version_selection == "":
                    version_selection = 0
                    break
                version_selection = int(version_selection) - 1
                if version_selection < 0 or version_selection >= len(mod_versions_list):
                    raise ValueError
                break
            except ValueError:
                print("Invalid input. Please enter a number.")

        version = mod_versions_list[version_selection]

        if len(version["files"]) == 0:
            print(f"No files found for {user_version}. Please try again.\n")
            continue

        file_selection = 0
        print(f"Multiple files found for {user_version}. Please select one:\n")
        for i, file in enumerate(version["files"]):
            print(f"{i + 1}: {file['filename']}")
        while True:
            file_selection = prompt_user(
                "Enter the number of the file you want to download: "
            )
            try:
                file_selection = int(file_selection) - 1
                if file_selection < 0 or file_selection >= len(version["files"]):
                    raise ValueError
                break
            except ValueError:
                print("Invalid input. Please enter a number.")

        file = version["files"][file_selection]
        file_download = file["url"]
        file_name = file["filename"]

        downloads_directory = (
            Path.home() / "python-modrinth-mod-downloader" / "downloads"
        )

        os.makedirs(downloads_directory / project_slug, exist_ok=True)

        with open(downloads_directory / project_slug / file_name, "wb") as output_file:
            output_file.write(httpx.get(file_download).content)

        print(
            f"Successfully downloaded mod to {downloads_directory / project_slug / file_name}."
        )

        break


# Run the program
if __name__ == "__main__":
    while True:
        search_interface()
