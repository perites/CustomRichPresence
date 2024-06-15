let oldActiveAJTabId = null;
setInterval(() => {
        chrome.tabs.query({active: true, currentWindow: true}, function (tabs) {
            if (oldActiveAJTabId !== null && oldActiveAJTabId !== tabs[0].id) {
                chrome.scripting.executeScript({
                    target: {tabId: oldActiveAJTabId},
                    function: () => {
                        clear_info()
                        window.oldData = null;
                    }
                }, () => {
                    oldActiveAJTabId = null;
                })
            }

            if ((tabs[0].url).startsWith("https://animejoy.ru/")) {
                chrome.scripting.executeScript({
                    target: {tabId: tabs[0].id},
                    function: () => {
                        send_info()
                    }
                })
                oldActiveAJTabId = tabs[0].id;
            }

        });
    }
    , 5000)
