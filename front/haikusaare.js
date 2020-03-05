const inspirations = ['talu', 'mees', 'perenaine', 'kala', 'mets', 'hobune', 'aeg', 'leib', 'linn', 'kool', 'maja', 'laps'];
function setRandomInsp() {
    document.getElementById("insp").value = inspirations[Math.floor(Math.random() * inspirations.length)];
}

function sendHaikuRequests() {

    for (let i = 1; i < 4; i++) {
        for (let j = 1; j < 4; j++) {
            const id = "haiku" + i.toString() + "line" + j.toString();
            document.getElementById(id).innerHTML = "_____";
            if (j === 2) document.getElementById(id).innerHTML += "__";
        }
    }

    let insp = document.getElementById("insp").value;
    if (insp.length > 200) {
        insp = "";
    }
    insp = insp.trim();

    for (let i = 1; i < 4; i++) {
        const request = new XMLHttpRequest();

        request.onreadystatechange = function () {
            if (this.readyState === 4) {
                if (this.status === 200) {

                    const lines = this.responseText.split("\n");
                    for (let j = 1; j < 4; j++) {
                        document.getElementById("haiku" + i.toString() + "line" + j.toString()).innerHTML = lines[j-1];
                    }

                }
                else {
                    console.log("status", this.status, "insp", insp)
                }
            }
        };
        request.open("GET", "/haikusaare/haiku?insp="+insp, true);
        request.send();
    }
}

window.addEventListener("DOMContentLoaded", function() {
    setRandomInsp();
    document.getElementById("insp_button").addEventListener("click", setRandomInsp);
    document.getElementById("haiku_button").addEventListener("click", sendHaikuRequests);
}, false);