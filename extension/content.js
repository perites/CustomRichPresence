// TODO Add logs ?
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
};


console.log('start sending 1th time')
let intervalId = setInterval(() => {
    sendData(getInfoFromPage(), "update")
}, 5000);
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
        console.log('start sending')
        sendData(getInfoFromPage(), "update");
        
        intervalId = setInterval(() => {
            sendData(getInfoFromPage(), "update")
        }, 5000);
    } else {
        console.log("need to CLEAR")
        clearInterval(intervalId);
        sendData("-", "clear");
    }
});

window.addEventListener('beforeunload', () => {
    sendData("-", "clear")
})