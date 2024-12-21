const sendDataToCRP = (info, method, activity) => {
    const data = {"info": info, "method": method, "activity_name": activity}

    port.postMessage(data);
    console.log("Data sent to Native Message Host | Data :", data)


}

const port = chrome.runtime.connectNative('com.nativemessaging.customrichpresence');
console.log("Connected to Native Messaging Host | port : ", port)

port.onDisconnect.addListener(() => {
    console.warn('Native Messaging Host disconnected');
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log("Received message from ", sender, " | Message : ", message)

    switch (message.action) {
        case 'sendDataToCRP':
            sendDataToCRP(message['info']['page_info'], message['info']['method'], message.activity)
            break;

        case "getCookie": {
            (async () => {
                const cookie = await chrome.cookies.get({url: message['info']['url'], name: message['info']['name']})
                console.log(cookie.value)
                sendResponse({cookie: cookie.value});
            })();

            return true;
        }
    }
});
