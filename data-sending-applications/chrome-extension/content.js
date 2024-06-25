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
        "title_name": titleName,
        "current_episode": getCurrentEpisode(),
        "mal_title_id": MALTitleID
    }
};

const sendData = (info, method, activity) => {
    const dataToSend = {
        action: "sendData",
        info: info,
        method: method,
        activity: activity
    }

    if (JSON.stringify(dataOld) === JSON.stringify(dataToSend)) {
        console.log("Data was not sent, identical to old")
        return
    }

    chrome.runtime.sendMessage(dataToSend)
    console.log("Sent data to background.js | Info :", info, "| Method :", method, "| Activity_DONT_NEED ", activity)
    dataOld = dataToSend

};

const sendDataUpdate = () => {
    sendData(getInfoFromPage(), "update", "WatchingAnimeJoy");
}

const sendDataClear = () => {
    sendData(getInfoFromPage(), "clear", "WatchingAnimeJoy");

}


console.log('Start sending 1th time')

let titleName = "";
let MALTitleID = "";
setTimeout(() => {
    titleName = findTitleName();
    MALTitleID = getMALTitleId();
}, 500)


let dataOld = "";


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