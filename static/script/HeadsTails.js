"use strict";

var timeLeft = 5;
var flipLockout = 0;
var flipStarted = 0;

const heads = "Heads";
const tails = "Tails";

var playerChoice = "coin";
var outcome = "coin";

var myUsername = "";

socket.emit("getUsername_or_deleteLobby", ["username", "amogus", "amogus2"])
socket.on("username_in_js", (data) => {
    myUsername = data["username"];
})

const AUGH = new Audio('static/sounds/AUUGH.mp3');
const drumRoll = new Audio('static/sounds/DrumRoll.mp3');
const womp = new Audio('static/sounds/womp.mp3');

window.onbeforeunload = function () { // emits a message when window is closed
    socket.emit("closing");
}

// Sets players choice to heads
function headsFunction(info) {// testing headsFunction(socket.socket) in headstail.html, didnt really work
    if (flipStarted === 0) {
        // socket.emit("player", {data: socket.id, "choice": "heads"});
        document.getElementById("choice").innerHTML = "You chose: Heads";
        playerChoice = heads;
        socket.emit("heads");
        socket.emit("check_for_other_user_input");
    } else {
        return;
    }
}


// Sets players choice to tails
function tailsFunction(info) { // testing tailsFunction(socket.roomid) in headstail.html, didnt really work
    if (flipStarted === 0) {
        // socket.emit("player", {data: socket.id, "choice": "tails"});
        document.getElementById("choice").innerHTML = "You chose: Tails";
        playerChoice = tails;
        socket.emit("tails");
        socket.emit("check_for_other_user_input");
    } else {
    }
}


// Helper function for setting color of coin
function randomColor() {
    return Math.floor(Math.random() * 255);
}


// Checks win condition
function checkWinner() {
    if (playerChoice === outcome) {
        document.getElementById("outcome").innerHTML = "You have: WON :D";
        AUGH.play();
    } else {
        document.getElementById("outcome").innerHTML = "You have: LOST >:( BOO YOU SUCK!";
        womp.play();
    }
}

function readyCheck(room_id) {
    socket.emit("getHTMLPage", {"game": "getGame", "room": room_id});
}

socket.on("returned_html", function (data) {
    document.getElementById("gameContainer").innerHTML = data["data"];
});


socket.on("player_ready", function (data) {
    document.getElementById("playerStatus").innerHTML = data["data"];

});

socket.on('render_message', function (data) {
    console.log("data");
    console.log(data);
    $('#messages').append($('<p>').text(data));
});

socket.on("username", function (data) {
    const username = data['username'];
    console.log(data);
    console.log(username);
    message_to_render(username);
});

function sendMessage() {
    console.log("hello");
    socket.emit("getUsername_or_deleteLobby", ["username"]);
}

function message_to_render(username) {
    console.log(username)
    const message = document.getElementById("message_box");
    const messageData = username + ":" + message.value;
    console.log("message data");
    console.log(messageData);
    socket.emit("chat_message", messageData);
}

function initiate_disconnection(roomid) {
    socket.emit("getUsername_or_deleteLobby", ["", roomid]);
}


socket.on("remove_players", (data) => {
    console.log(data);
    if (document.querySelector("#playerStatus")){
        document.getElementById("playerStatus").remove();
        document.getElementById("gameContainer").innerHTML = data["data"];
    } else {
        document.getElementById("wrap_game").remove();
        document.getElementById("case_disconnection").innerHTML = data[data];
    }
});


//document.getElementById("coinValue").innerHTML = "Heads";
//document.getElementById("coinValue").innerHTML = "Tails";

socket.on("start_game", function (data) {
    const userName1 = data["player1"];
    const userName2 = data["player2"];
    console.log(flipLockout);
    if (flipLockout < 1){
        if (userName1 != myUsername){
            document.getElementById("opponentChoice").innerHTML = "Opponent chose: " + data[userName1];
        }
        else{
            document.getElementById("opponentChoice").innerHTML = "Opponent chose: " + data[userName2];
        };

        flipLockout += 1;
        console.log("game has started");
        outcome = data["server_flip"];
        drumRoll.play();
        var iterations = 24;
        // interval to build some suspense so we don't have to watch something extremely static
        var suspense = setInterval(function () {
            var x = Math.random();
            document.getElementById("coinValue").style = "color: rgba(" + randomColor() + "," + randomColor() + "," + randomColor() + ");";
            // if x is greater or less than .5 set the values respectively
            if (x < .5) {
                document.getElementById("coinValue").innerHTML = "Heads";
            } else {
                document.getElementById("coinValue").innerHTML = "Tails";
            };
            iterations -= 1;
            if (iterations < 0) {
                clearInterval(suspense);
            };
        }, 150);

        // Checks win condition after 2 seconds
        setTimeout(function () {
            document.getElementById("coinValue").innerHTML = outcome;
            checkWinner();
        }, 4300);
    };
});

function joinRoom(room_id) {
    socket.emit("join", room_id);
    socket.emit("wait_to_start_game", room_id);
}
