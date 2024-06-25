const sendData = (info, method, activity) => {
    const data = {"info": info, "method": method, "activity_name": activity}

    port.postMessage(data);
    console.log("Data sent to Native Message Host | Data :", data)


}

const port = chrome.runtime.connectNative('com.nativemessaging.customrichpresence');
console.log("Connected to Native Messaging Host | port : ", port)

port.onDisconnect.addListener(() => {
    console.warn('Native Messaging Host disconnected');
});

chrome.runtime.onMessage.addListener(async (message) => {
    if (message.action === "sendData") {
        console.log("Received data from content.js, proceed | Info :", message.info, "| Method :", "| Activity :", message.activity)
        await sendData(message.info, message.method, message.activity)
    }
});
