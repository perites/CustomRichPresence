class Activity {
    constructor(name) {
        this.oldData = "";
        this.name = name
    }

    sendData = (info, method) => {
        const dataToSend = {
            action: "sendData",
            info: info,
            method: method,
            activity: this.name
        }

        if (JSON.stringify(this.oldData) === JSON.stringify(dataToSend)) {
            console.log("Data was not sent, identical to old")
            return
        }

        chrome.runtime.sendMessage(dataToSend)
        console.log("Sent data to background.js | Info :", info, "| Method :", method, "| Activity : ", this.name)
        this.oldData = dataToSend

    };

    startSending = () => {
        console.error("startSending was not implemented")
    }

    stopSending = () => {
        console.error("stopSending was not implemented")
    }
}

class WatchingAnimeJoy extends Activity {
    constructor() {
        super("WatchingAnimeJoy")
        this.titleName = this.findTitleName();
        this.MALTitleID = this.getMALTitleId();

        this.updateIntervalId = NaN;

    }

    get currentEpisode() {
        const playlistContainer = document.getElementsByClassName("playlists-videos")[0];
        const listItems = playlistContainer.getElementsByTagName("ul")[0];
        const listArrayRaw = Array.from(listItems.children);
        const listArray = listArrayRaw.filter(item => item.getAttribute("data-file").startsWith("https://iv.sibnet.ru/"));

        let current_episode = -1;
        for (let i = 0; i < listArray.length; i++) {
            if (listArray[i].classList.contains("visible") && listArray[i].classList.contains("active")) {
                current_episode = i + 1;
                return current_episode;
            }
        }
    }

    get titleInfo() {
        return {
            "title_name": this.titleName,
            "current_episode": this.currentEpisode,
            "mal_title_id": this.MALTitleID
        };
    }

    findTitleName = () => {
        return document.getElementsByClassName('romanji')[0].textContent
    };

    getMALTitleId = () => {
        const links = document.getElementsByClassName('ansdb');
        for (let link of links) {
            if (link.href.startsWith("https://myanimelist.net/anime/")) {
                return link.href.split("/")[4]
            }
        }
    };


    startSending = () => {
        this.updateIntervalId = setInterval(() => {
            this.sendData(this.titleInfo, "update");
        }, 5000);
    }

    stopSending = () => {
        this.sendData(this.titleInfo, "clear");
        clearInterval(this.updateIntervalId);
    }
}


class Geoguessr extends Activity {
    constructor() {
        super("Geoguessr");
    }

    startSending = () => {
        this.sendData({"status": "started"}, "update")
    }

    stopSending = () => {
        this.sendData({"status": "finished"}, "clear")
    }
}

window.addEventListener("load", () => {
    const hostName = (window.location.hostname).split(".").reverse()[1]
    let act;
    switch (hostName) {

        case "animejoy":
            act = new WatchingAnimeJoy();
            break;
        case 'geoguessr':
            act = new Geoguessr();
            break;

        default:
            return
    }

    act.startSending();

    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible') {
            act.startSending()

        } else {
            act.stopSending()
        }
    });


})
