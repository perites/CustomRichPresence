class Activity {
    constructor(name) {
        this.oldData = "";
        this.name = name
    }

    sendMessageToBackground = (action, info) => {
        const dataToSend = {
            action: action,
            info: info,
            activity: this.name
        }

        if (JSON.stringify(this.oldData) === JSON.stringify(dataToSend)) {
            console.log("Data was not sent, identical to old")
            return
        }
        console.log("Sending data to background.js : ", dataToSend)
        const response = chrome.runtime.sendMessage(dataToSend)

        this.oldData = dataToSend

        return response
    }

    sendDataToCRP = (page_info, method) => {
        const infoToBG = {
            page_info: page_info,
            method: method
        }
        this.sendMessageToBackground("sendDataToCRP", infoToBG)
    };

    getCookie = async (name, url) => {
        const infoToBG = {
            name: name,
            url: url
        }

        const response = await this.sendMessageToBackground('getCookie', infoToBG)
        return response.cookie
    }

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
            this.sendDataToCRP(this.titleInfo, "update");
        }, 5000);
    }

    stopSending = () => {
        clearInterval(this.updateIntervalId);
        this.sendDataToCRP(this.titleInfo, "clear");
    }
}


class Geoguessr extends Activity {
    constructor() {
        super("Geoguessr");
        this.currentRound = 1
        this.intervalsIds = []
        this.getNCFA_TOKEN().then((cookie) => {
                this.NCFA_TOKEN = cookie
            }
        )
    }

    getNCFA_TOKEN = async () => {
        return await this.getCookie('_ncfa', 'https://www.geoguessr.com/')

    };


    get gameId() {
        const pathname = (window.location.pathname).split("/").reverse().filter(item => item !== "summary");
        return pathname[0]
    }

    get gameMode() {
        const pathname = (window.location.pathname).split("/").reverse().filter(item => item !== "summary");
        return pathname[1]
    }

    getGeoGameInfo = async () => {
        let info = {
            "game_mode": this.gameMode,
        }

        const response = await this.makeGeoAPIRequest()

        let mode_info;
        switch (this.gameMode) {
            case "duels":
                mode_info = {
                    'map_name': response['options']['map']['name'],
                    'rounds_info': [response['currentRoundNumber'], response['options']['maxNumberOfRounds']], // [current, max]
                    'status': response['status']
                }
                break;


            case "game":
                mode_info = {

                    "map_name": response['mapName'],
                    'rounds_info': [response['round'], response['roundCount']],
                    'status': response['state']

                }
                break;

            case "live-challenge":
                mode_info = {
                    'map_name': response['mapName'],
                    'rounds_info': [this.currentRound, response['gameOptions']['roundCount']], // [current, max]
                    'status': response['status'],
                    'additional_info': {'share_link': response['shareLink']}
                }
                break;
        }


        return {...info, ...mode_info}
    }

    startFetchingCurrentRound = () => {
        this.intervalsIds.push(setInterval(() => {
            try {
                const element = document.querySelector('.multiplayer-round-results_headline__OZRyy');
                if (element) {
                    this.currentRound = element.textContent.split(' ')[1]
                }
            } catch (error) {
            }
        }, 2000))

    }

    makeGeoAPIRequest = async () => {
        const gameModesAPIs = {
            "duels": "https://game-server.geoguessr.com/api/duels/",
            "game": "https://www.geoguessr.com/api/v3/games/",
            "live-challenge": "https://game-server.geoguessr.com/api/lobby/"
        }
        const url = gameModesAPIs[this.gameMode] + `${this.gameId}`
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                "Content-Type": "application/json",
                "Cookie": `_ncfa=${this.NCFA_TOKEN}`,
            },
            credentials: "include"
        });
        return await response.json();
    }

    startSending = () => {
        if (this.gameMode === 'live-challenge') {
            this.startFetchingCurrentRound()
        }

        this.intervalsIds.push(setInterval(async () => {
            this.sendDataToCRP(await this.getGeoGameInfo(), "update")
        }, 5000))

    }

    stopSending = () => {
        for (const intervalId of this.intervalsIds) {
            clearInterval(intervalId)
        }
        this.sendDataToCRP({"": ""}, "clear")
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

    window.addEventListener('unload', () => {
        act.stopSending()
    });


})
