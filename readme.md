# WPplugin

A simple python script to query for the URL of a WordPress plugin, if you only know the name.

## Usage

`python3 wpplugin.py "Hello"`

shows a list of the first ten plugins found for the search term in the WordPress plugin directory. You can either select one of the plugins by entering the **number**, display the **n**ext ten hits or **q**uit the script.
If you selected a plugin, the complete link will be copied to the clipboard and additionally displayed in the terminal window.

The plugin uses the WordPress API, documentation can be found at <https://codex.wordpress.org/WordPress.org_API#Plugins>.

## License

MIT License
(c) 2023 Bego Mario Garde <pixolin@pixolin.de>
