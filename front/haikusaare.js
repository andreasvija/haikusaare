const inspirations = ['talu', 'mees', 'perenaine', 'kala', 'mets', 'hobune', 'aeg', 'leib', 'linn', 'kool', 'maja', 'laps'];
function setRandomInsp() {
    document.getElementById("insp").value = inspirations[Math.floor(Math.random() * inspirations.length)];
}

function sendHaikuRequests() {

    let insp = document.getElementById("insp").value;
    if (insp.length > 200) {
        insp = "";
    }
    insp = insp.trim();

    document.querySelectorAll("#haikus .haiku").forEach(function (haiku) {

        for (let i = 0; i < 3; i++) {
            const haikuLines = haiku.querySelectorAll("p");
            let placeholder = "_____";
            if (i === 1) placeholder += "__";
            haikuLines[i].innerHTML = placeholder;
        }

        const request = new XMLHttpRequest();
        request.onreadystatechange = getHaikuResponseHandler(haiku);
        request.open("GET", "/haikusaare/haiku?insp=" + insp, true);
        request.send();
    });
}

function getHaikuResponseHandler(haiku) {
    return function () {
        if (this.readyState === 4) {
            if (this.status === 200) {

                const lines = this.responseText.split("\n");
                const haikuLines = haiku.querySelectorAll("p");

                for (let j = 0; j < 3; j++) {
                    haikuLines[j].innerHTML = lines[j];
                }

            }
        }
    };
}

function getSoundRequestSender(haiku) {
    return function () {
        let text = "";
        haiku.querySelectorAll("p").forEach(function (p) {
            text += p.innerHTML + ". "
        });

        const request = new XMLHttpRequest();
        request.onreadystatechange = soundResponseHandler;
        request.open("GET", "/haikusaare/sound?text=" + text, true);
        request.send();
    }
}

function soundResponseHandler () {
    if (this.readyState === 4) {
        if (this.status === 200) {
            // play this.response
        }
    }
}

window.addEventListener("DOMContentLoaded", function() {
    setRandomInsp();
    document.getElementById("insp_button").addEventListener("click", setRandomInsp);
    document.getElementById("haiku_button").addEventListener("click", sendHaikuRequests);

    document.querySelectorAll("#haikus .haiku").forEach(function (haiku) {
        haiku.querySelector("img").addEventListener("click", getSoundRequestSender(haiku))
    });
}, false);
