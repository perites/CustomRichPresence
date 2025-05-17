document.getElementById('sendButton').addEventListener('click', () => {
    const activity = document.getElementById('activity').value;
    const method = document.getElementById('method').value;
    const dataToSend = {
        action: "sendDataToCRP",
        info: {page_info: "-",method: method},
        activity: activity
    }
    chrome.runtime.sendMessage(dataToSend)
});
