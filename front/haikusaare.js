const inspirations = ["talu", "mees", "perenaine", "kala", "mets", "hobune", "aeg"];
function setRandomInsp() {
    const insp = inspirations[Math.floor(Math.random() * inspirations.length)];
    document.getElementById("insp").value = insp;
};

function sendHaikuRequest() {
    var insp = document.getElementById("insp").value;
    if (insp.length > 200) {
        insp = "";
    }
    insp = insp.trim();

    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState == 4) {
            if (this.status == 200) {
                const lines = this.responseText.split("\n");
                document.getElementById("haiku1").innerHTML = lines[0];
                document.getElementById("haiku2").innerHTML = lines[1];
                document.getElementById("haiku3").innerHTML = lines[2];
            }
            else {
                console.log("status", this.status, "insp", insp)
            }
        }
    };
    request.open("GET", "/haikusaare/haiku?insp="+insp, true);
    request.send();
};

window.addEventListener("DOMContentLoaded", function() {
    setRandomInsp();
    document.getElementById("insp_button").addEventListener("click", setRandomInsp);
    document.getElementById("haiku_button").addEventListener("click", sendHaikuRequest);
}, false);