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
# fmt: off
config = {
    "version"    : "0.4.4",
    "programm"   : "wpplugin",
    "description": "Retrives plugin links from the WordPress repository",
    "copyright"  : "(c) Bego Mario Garde, 2023",
    "url"        : "https://api.wordpress.org/plugins/info/1.2/",
    "params"     : {
        "action"         : "query_plugins",
        "request[search]": "",
    },
    "timeout"  : 20,
    "pluginurl": "https://de.wordpress.org/plugins/",
}
# fmt: on


def main():
    """Run script. See comments below."""
    pluginname = validate_arguments()
    wp_request = request_plugins(pluginname)
    selected_plugin_number = let_user_select(wp_request)
    link = render_link(wp_request, selected_plugin_number)

    # copy link to clipboard and print output
    try:
        pyperclip.copy(link)
        print(f"Copied to your clipboard:\n{link}")
    except pyperclip.PyperclipException:
        print(f"Copy:\n\n{link}\n")


def validate_arguments() -> str:
    """Validate script arguments"""
    parser = argparse.ArgumentParser(
        prog=config["programm"],
        description=config["description"],
        epilog=config["copyright"],
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {config['version']}"
    )
    parser.add_argument(
        "plugin_name",
        type=str,
        action="store",
        help="Name of the plugin to search for in the WordPress plugin repository.",
    )
    args = parser.parse_args()
    return args.plugin_name.lower()


def request_plugins(search_term: str) -> dict:
    """Request plugins from WordPress API using search term.

    Args:
        search_term (str): The plugin you are searching for.

    Returns:
        dict: Dictionary with plugin names and slugs.
    """
    params = dict(config["params"])
    params["request[search]"] = search_term

    try:
        response = requests.get(config["url"], params=params, timeout=config["timeout"])
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")
        sys.exit(1)

    return response.json()


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
        prompt = get_user_prompt(passes)
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


def get_user_prompt(passes):
    """Returns instructions for user based on number of passes."""
    if passes < 3:
        return "Enter plugin number or press enter for first match. Enter [n] for next 10 plugins, enter [q] to abort.\n\n"
    else:
        return "Enter plugin number or press enter for first match. Enter [q] to abort.\n\n"


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


def render_link(plugins: dict, selected_index: int) -> str:
    """Render link to plugin page using plugin list and selection as index.

    Args:
        plugins (dict): List of plugins.
        selected_index (int): Index of selected plugin.

    Returns:
        str: Rendered link to plugin page.
    """
    selected_plugin = plugins["plugins"][selected_index]
    slug = selected_plugin["slug"]
    name = html.unescape(selected_plugin["name"])
    plugin_url = config["pluginurl"]

    return f'<a href="{plugin_url}{slug}/">{name}</a>'


if __name__ == "__main__":
    main()
