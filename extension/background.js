const sendData = (info, method) => {
    const data = {"data": info, "method": method}

    if (methodsToCheck.includes(method) && JSON.stringify(oldData) === JSON.stringify(data)) {
        console.log("Data was not sent, identical to old.")
        return
    }

    port.postMessage(data);
    console.log("Data sent to Native Message Host | Data :", data)

    oldData = data;
}

let oldData = "";
const methodsToCheck = ["update"]
const port = chrome.runtime.connectNative('com.nativemessaging.customrichpresence');
console.log("Connected to Native Messaging Host | port : ", port)

port.onDisconnect.addListener(() => {
    console.warn('Native Messaging Host disconnected');
});

chrome.runtime.onMessage.addListener(async (message) => {
    if (message.action === "sendData") {
        console.log("Received data from content.js, proceed | Info :", message.info, "| Method :", message.method)
        await sendData(message.info, message.method)
    }
});
