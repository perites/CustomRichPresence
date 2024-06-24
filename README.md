# Rich Presence Activity Manager (RPAC)

A tool for managing Rich Presence (RP) according to data from various applications

## How It Works

Different applications (such as a Chrome extension, PyCharm plugin, etc.) gather data and send it via the TCP protocol
to a server. There are two main methods for communication:

- `update`: For updating information in Rich Presence (RP)
- `clear`: For clearing RP

The data follows this path from the server to be shown in RP:

1. **Custom Activity**
    - Process data directly from application
    - You have complete freedom to process this data since you are writing a CustomActivity
    - Sends processed data to RPAC
2. **RichPresenceActivityManager (RPAC)**
    - Manages data from various activities.
    - Prioritizes activities and queues them if necessary.
    - Handles the delay between the clear command and the actual clearing of RP.
    - Sends information to the RP apps controller.
3. **RP Apps Controller**
    - Integrates with multiples discord`s apps.
    - Changes the RP displayed in Discord.

## Features

- **Automatic Rich Presence Updates**: Automatically updates RP based on activity data.
- **Flexible Data Input**: Can receive activity data from any source via the TCP protocol.
- **Custom Activities**: Supports custom activities and data processing.
- **Multiple Apps Support**: Different activities can correspond to different apps (e.g., "Playing watching" for
  activity1, "Playing coding" for activity2).

![img.png](assets/watching.png)![img.png](assets/coding.png)

- **Activity Priorities**: Prevents RP from changing to a lower priority activity while a higher priority is active.
- **Activity Queue**: Queues lower priority activities, automatically switching to them when higher priority tasks are
  completed.
- **Automated Start Time Management**: Each activity includes a customizable start time manager, which makes displaying
  start times in RP straightforward and convenient.

![img.png](assets/time.png)

- **Clear Delay**: Ensures RP is not immediately cleared after a `clear` command, allowing for potential updates to
  another activity rather than clearing RP completely.

# Applications that Send Data

## Chrome Extension

This extension collects necessary data from websites and sends it
to [`native_messages_proxy.py`](https://github.com/perites/CustomRichPresence/blob/master/chrome-extension/native_messages_proxy.py)
using Chrome Native Messages.
The [`native_messages_proxy.py`](https://github.com/perites/CustomRichPresence/blob/master/chrome-extension/native_messages_proxy.py)
script then forwards the data to the main server via the TCP protocol.

The extension gathers information from the following websites:

- [animejoy.ru](http://animejoy.ru/)

## To-Do List

- Develop a plugin for PyCharm.
- Create a graphical interface for manual RP management.
- Expand the Chrome extension to support YouTube.