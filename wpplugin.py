#!/usr/bin/env python3

"""
wpplugin

Search for a plugin using the WordPress API.
Let user select one of the plugins, render
and copy a link to clipboard. You can use this
e.g. when mentioning a plugin in support forums..

License: MIT
(c) Bego Mario Garde <pixolin@pixolin.de>, 2023
"""

import argparse
import html
import sys

import pyperclip
import requests

# script settings
config = {
    "version": "0.4.0",
    "programm": "wpplugin",
    "description": "Retrives plugin links from the WordPress repository",
    "copyright": "(c) Bego Mario Garde, 2023",
    "url": "https://api.wordpress.org/plugins/info/1.2/",
    "params": {
        "action": "query_plugins",
        "request[search]": "",
    },
    "timeout": 20,
    "pluginurl": "https://de.wordpress.org/plugins/",
}


def main():
    """Run script. See comments below."""
    # has the user correctly passed as plugin name?
    pluginname: str = validate_arguments()

    # search for the plugin using WordPress API
    wp_request: object = request_plugins(pluginname)

    # print a list of search result and let user select
    selected_plugin_number: int = let_user_select(wp_request)

    # render a link from selected plugin data
    link = render_link(wp_request, selected_plugin_number)

    # copy link to clipboard and print output
    try:
        pyperclip.copy(link)
        print(f"Copied to your clipboard:\n{link}")
    except pyperclip.PyperclipException:
        print(f"Copy:\n\n{link}\n")


def validate_arguments() -> str:
    """Validate script arguments"""
    parser: object = argparse.ArgumentParser(
        prog=config["programm"],
        description=config["description"],
        epilog=config["copyright"],
    )
    # parser.add_argument("plugin")
    parser.add_argument(
        "-v", "--version", action="version", version="%(prog)s 0.3.0"
    )
    parser.add_argument(
        "name",
        type=str,
        action="store",
        nargs=1,
        help=(
            "The name of the plugin you want to find in the wp.org plugin"
            " repository."
        ),
    )
    args = parser.parse_args()

    # return the name of the desired plugin
    return args.name[0].lower()


def request_plugins(searchterm: str) -> dict:
    """use searchterm in a query with WordPress API
    see https://codex.wordpress.org/WordPress.org_API

    Args:
        searchterm (str): the plugin you are searching for

    Returns:
        dict: plugin dictionary with names and slugs
    """
    # use config settings as paramaters and assign searchterm
    url = config["url"]
    config["params"]["request[search]"] = searchterm
    params = config["params"]
    timeout = config["timeout"]

    try:
        response = requests.get(url=url, params=params, timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        print("HTTP Error")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("Error Connecting")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("Timeout Error")
        sys.exit(1)
    except requests.exceptions.RequestException:
        print("OOps: Something Else")
        sys.exit(1)

    json_response = response.json()

    return json_response


def let_user_select(pluginlist: dict) -> int:
    """prints list of found plugins and asks user to select one or quit

    Args:
        pluginlist (dict): list of found plugins

    Returns:
        int: index of selected plugin
    """

    howmany: int = len(pluginlist["plugins"])
    print(list_plugins(pluginlist, 0, 10))

    passes = 1
    if howmany < 11:
        passes = 3

    while True:
        prompt = ask_user_prompt(passes=passes)
        user_input = input(prompt).strip()

        passes += 1
        start: int = (passes - 1) * 10
        stop: int = start + 10

        if user_input.isdigit() and 1 <= int(user_input) <= howmany:
            break
        if user_input == "":
            user_input = 1
            break
        if user_input == "n":
            print(list_plugins(pluginlist, start, stop))
            continue
        if user_input == "q":
            print("Script aborted")
            sys.exit(1)
        print("Invalid input, please try again. \n")
        continue

    # user input is now stored in the variable user_input as an integer
    # as index starts with 0, we reduce the number by one
    number = int(user_input) - 1
    return number


def ask_user_prompt(passes):
    """give user instructions according to number of passes

    Args:
        passes (int): number of passes

    Returns:
        str: prompt
    """
    prompt: str = (
        "   Enter plugin number or just press enter for first match.\n"
    )
    if passes < 3:
        prompt += "   Enter [n] for next 10 plugins, enter [q] to abort.\n\n"
    else:
        prompt += "   Enter [q] to abort.\n\n"
    return prompt


def list_plugins(jsonlist: dict, start: int, stop: int) -> str:
    """list plugins, prepended with a number

    Args:
        jsonlist (dict): list of plugins
        start (int): first index in range
        stop (int): last index in range

    Returns:
        str: formatted output
    """
    i = start + 1
    output: str = "\n"
    for plugin in jsonlist["plugins"][start:stop]:
        if len(plugin["name"]) > 60:
            output += f"{i:>2} {html.unescape(plugin['name'][:60])} …\n"
        else:
            output += f"{i:>2} {html.unescape(plugin['name'])}\n"
        i += 1
    return output


def render_link(response_dict: dict, selection: int) -> str:
    """use plugin list and selection as index to render link

    Args:
        response_dict (dict): list of plugins
        selection (int): index of item in list of plugins

    Returns:
        str: rendered link to plugin page
    """
    selected = response_dict["plugins"][selection]
    slug = selected["slug"]
    name = html.unescape(selected["name"])
    url = config["pluginurl"]

    plugin_link = '<a href="' + url + slug + '/"><b>' + name + "</b></a>"
    return plugin_link


if __name__ == "__main__":
    main()
