let OldActiveTabId = null;

chrome.tabs.onActivated.addListener(function (activeInfo) {
    if (OldActiveTabId !== null) {
        chrome.scripting.executeScript({
                target: {tabId: OldActiveTabId},
                function: () => {
                    console.log("Need to clear")
                    clear_info()
                    clearInterval(window.intervalId);
                    window.intervalId = null;
                }
            }, (results) => {
                if (chrome.runtime.lastError) {
                    console.error(`Script injection failed: ${chrome.runtime.lastError.message}`);
                }
            }
        );
    }


    OldActiveTabId = activeInfo.tabId;
    setTimeout(() => {
        chrome.scripting.executeScript({
            target: {tabId: activeInfo.tabId},
            function: () => {
                send_info()
                window.intervalId = setInterval(() => {
                    send_info()
                }, 5000)

            }
        });
    }, 1000)
});

