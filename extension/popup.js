document.getElementById('sendButton').addEventListener('click', () => {
    const priority = document.getElementById('activity').value;
    const method = document.getElementById('method').value;
    const dataToSend = {
        action: "sendData",
        info: priority,
        method: method,
        activity: "WatchingYoutube"
    }
    chrome.runtime.sendMessage(dataToSend)
});
