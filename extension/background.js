const sendData = (info, method) => {
    const data = JSON.stringify({"data": info, "method": method})

    const methodsToCheck = ["update"]
    if (methodsToCheck.includes(method) && oldData === data) {
        return
    }
    const options = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: data
    };

    const url = 'http://127.0.0.1:5000/receiveinfo';

    fetch(url, options).catch((er) => console.log(er))

    oldData = data;

}

let oldData = "";

chrome.runtime.onMessage.addListener(async (message) => {
    // console.log("MESSAGE !", message)
    if (message.action === "sendData") {

        // console.log("need to send")
        await sendData(message.info, message.method)
        // console.log("data send")
    }
});
