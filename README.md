# CustomRichPresence

In this project, a Chrome extension communicates with a local Python script to send information about the webpage the user is currently viewing. The Python script then updates the Rich Presence (RP) status in the local Discord application.

Gathers information from: animejoy.ru

## Technologies Used

### Extension:
- JavaScript
- Chrome Extension API

### Local Python Script Libraries:
- Flask to create a server that communicates with the extension
- Pypresence to change RP
- Mal-api to get information about anime titles
