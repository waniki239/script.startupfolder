from __future__ import annotations

import xml.etree.ElementTree as ET

import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
import sys

ADDON = xbmcaddon.Addon()

LOG_PREFIX = "[Startup Folder]"


def log(
    message: str,
    level: int = xbmc.LOGINFO,
) -> None:
    """Write a message to the Kodi log."""
    xbmc.log(f"{LOG_PREFIX} {message}", level)


def get_favourites() -> list[tuple[str, str]]:
    """Return all favourites."""

    favourites = xbmcvfs.translatePath("special://profile/favourites.xml")

    if not xbmcvfs.exists(favourites):
        log("favourites.xml not found.", xbmc.LOGWARNING)
        return []

    try:
        root = ET.parse(favourites).getroot()
    except ET.ParseError:
        log("Failed to parse favourites.xml.", xbmc.LOGERROR)
        return []

    result: list[tuple[str, str]] = []

    for favourite in root.findall("favourite"):
        name = favourite.attrib.get("name")
        command = favourite.text

        if not name or not command:
            continue

        result.append((name, command))

    return result


def get_favorite_command() -> str | None:
    """Return the command for the configured favourite."""

    favorite_name = ADDON.getSetting("favorite_name").strip()

    log(f"favorite_name = '{favorite_name}'")

    if not favorite_name:
        log("No favourite configured.", xbmc.LOGWARNING)
        return None

    log(f"Looking for favourite '{favorite_name}'.")

    for name, command in get_favourites():
        if name == favorite_name:
            log("Favourite found.")
            return command

    log(
        f"Favourite '{favorite_name}' not found.",
        xbmc.LOGWARNING,
    )

    return None


def select_favourite() -> None:
    """Show the favourite selection dialog."""

    favourites = get_favourites()

    if not favourites:
        xbmcgui.Dialog().notification(
            "Startup Folder",
            "No favourites found.",
            xbmcgui.NOTIFICATION_ERROR,
        )
        return

    names = [name for name, _ in favourites]

    index = xbmcgui.Dialog().select(
        "Select Favourite",
        names,
    )

    if index < 0:
        return

    name, _ = favourites[index]

    log(f"Selected: {name}")

    ADDON.setSettingString(
        "favorite_name",
        name,
    )

    log(f"Saved: '{ADDON.getSetting('favorite_name')}'")


def main() -> None:
    """Entry point."""

    if len(sys.argv) > 1 and sys.argv[1] == "select":
        select_favourite()
        return

    log("Service started.")

    monitor = xbmc.Monitor()

    if monitor.waitForAbort(0.5):
        return

    command = get_favorite_command()

    if not command:
        return

    log(f"Executing: {command}")

    xbmc.executebuiltin(command)


if __name__ == "__main__":
    main()
