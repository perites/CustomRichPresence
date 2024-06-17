const findTitleName = () => {
    return document.getElementsByClassName('romanji')[0].textContent
};

const getCurrentEpisode = () => {
    const playlistContainer = document.getElementsByClassName("playlists-videos")[0];
    const listItems = playlistContainer.getElementsByTagName("ul")[0];
    const listArrayRaw = Array.from(listItems.children);
    const listArray = listArrayRaw.filter(item => item.getAttribute("data-file").startsWith("https://video.sibnet.ru/"));

    let current_episode = -1;
    for (let i = 0; i < listArray.length; i++) {
        if (listArray[i].classList.contains("visible") && listArray[i].classList.contains("active")) {
            current_episode = i + 1;
            return current_episode;
        }
    }
};
const getMALTitleId = () => {
    const links = document.getElementsByClassName('ansdb');
    for (let link of links) {
        if (link.href.startsWith("https://myanimelist.net/anime/")) {
            return link.href.split("/")[4]
        }
    }
};


const getInfoFromPage = () => {
    return {
        "title_name": findTitleName(),
        "current_episode": getCurrentEpisode(),
        "mal_title_id": getMALTitleId()
    }
};

const sendData = (info, method) => {
    chrome.runtime.sendMessage({
        action: "sendData",
        info: info,
        method: method
    })
    console.log("Sent data to background.js | Info :", info, "| Method :", method)
};

const sendDataUpdate = () => {
    sendData(getInfoFromPage(), "update");
}

const sendDataClear = () => {
    sendData("-", "clear");
}

console.log('Start sending 1th time')

let updateIntervalId = setInterval(() => {
    sendDataUpdate();
}, 5000);

console.log("Created update interval with id : ", updateIntervalId)

document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
        console.log('Start sending')
        sendDataUpdate();

        updateIntervalId = setInterval(() => {
            sendDataUpdate()
        }, 5000);
        console.log("Created update interval with id :", updateIntervalId)

    } else {
        console.log("Need to clear |", "updateIntervalId :", updateIntervalId)
        clearInterval(updateIntervalId);
        sendDataClear();
    }
});

window.addEventListener('beforeunload', () => {
    sendDataClear();
})