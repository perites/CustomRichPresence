// TODO check tab every - , if active and  window.intervalId === null , start sending

let OldActiveTabId = null;

chrome.tabs.onActivated.addListener(function (activeInfo) {

    if (OldActiveTabId === null) {
        console.log("NULL")
        OldActiveTabId = activeInfo.tabId;
    }

    chrome.scripting.executeScript({
            target: {tabId: OldActiveTabId},
            function: () => {
                clear_info()
                clearInterval(window.intervalId)
                window.intervalId = null;
            }
        }, (result1) => {
            if (chrome.runtime.lastError) {
                console.error(`Script injection failed: ${chrome.runtime.lastError.message}`);
            }
            OldActiveTabId = activeInfo.tabId;


            setTimeout(() => {
                chrome.scripting.executeScript({
                    target: {tabId: OldActiveTabId},
                    function: () => {
                        if (window.intervalId === null) {
                            send_info()
                            window.intervalId = setInterval(() => {
                                send_info()
                            }, 5000)
                        }
                    }
                })
            }, 900)
        }
    );


});

