//TODO manual current episode
//TODO application ID setting
// TODO button to clear status
function find_title_name() {
    const title_name = document.getElementsByClassName('romanji')[0].textContent;
    return title_name
}

function get_current_episode() {
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
}

function get_mal_anime_id() {
    const links = document.getElementsByClassName('ansdb');
    for (let link of links) {
        if (link.href.startsWith("https://myanimelist.net/anime/")) {
            const mal_title_id = link.href.split("/")[4]
            return mal_title_id
        }
    }
}


function get_info_from_page() {
    const page_info = {
        "title_name": find_title_name(),
        "current_episode": get_current_episode(),
        "mal_title_id": get_mal_anime_id()
    };
    return page_info
}

function send_info() {
    const page_info = get_info_from_page()
    const data = {"data": page_info, "method": "update"}

    const options = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    };

    const url = 'http://127.0.0.1:5000/receiveinfo';
    fetch(url, options)
        .then(response => response.json())
        .catch(error => console.error('Error:', error));
}

function clear_info() {
    const data = {"data": "-", "method": "clear"}

    const options = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    };

    const url = 'http://127.0.0.1:5000/receiveinfo';
    fetch(url, options)
        .then(response => response.json())
        .catch(error => console.error('Error:', error));
}



