"use strict";

var timeLeft = 5;
var flipLockout = 0;
var flipStarted = 0;

const heads = "Heads";
const tails = "Tails";

var playerChoice = "coin";
var outcome = "coin";

const AUGH = new Audio('static/sounds/AUUGH.mp3');
const drumRoll = new Audio('static/sounds/DrumRoll.mp3');
const womp = new Audio('static/sounds/womp.mp3');

window.onbeforeunload = function(){ // emits a message when window is closed
    socket.emit("closing")
}

// Sets players choice to heads
function headsFunction(info){// testing headsFunction(socket.socket) in headstail.html, didnt really work
    if (flipStarted === 0){
    // socket.emit("player", {data: socket.id, "choice": "heads"});
    document.getElementById("choice").innerHTML = "You chose: Heads";
    playerChoice = heads;
    socket.emit("heads")
    socket.emit("check_for_other_user_input")

    // startFlipTimer();
    }
    else{return;}
}


// Sets players choice to tails
function tailsFunction(info){ // testing tailsFunction(socket.roomid) in headstail.html, didnt really work
    if (flipStarted === 0){
    // socket.emit("player", {data: socket.id, "choice": "tails"});
    document.getElementById("choice").innerHTML = "You chose: Tails";
    playerChoice = tails;
    socket.emit("tails")
    socket.emit("check_for_other_user_input")


    
    }
    else{}
}

// Starts countdown for both players
function startFlipTimer(){
    if (flipLockout === 0){
    var timer = setInterval(function(){
        document.getElementById('timerNumber').innerHTML= "Timer:"+timeLeft;
        document.getElementById('timer').value -= .01;
        timeLeft-= .01;
        if(timeLeft<0){
            clearInterval(timer);
            document.getElementById('timer').value = 5;
            timeLeft = 5;
        }
    }, 10);
    // Flips coin after 7.8 seconds
    flipLockout = 1;
    setTimeout(flipCoin, 5000);
    }
    else{}
}

// Helper function for setting color of coin
function randomColor(){
    return Math.floor(Math.random() * 255);
}

// Actual flipping of coin
function flipCoin(){
    flipStarted = 1;
    drumRoll.play();
    var iterations = 24;
    // interval to build some suspense so we don't have to watch something extremely static
    var suspense = setInterval(function(){
        var x = Math.random();
        document.getElementById("coinValue").style="color: rgba("+randomColor()+","+randomColor()+","+randomColor()+");";
        // if x is greater or less than .5 set the values respectively
        if(x < .5){
            document.getElementById("coinValue").innerHTML = "Heads";
            outcome = heads;
        }
        else{
            document.getElementById("coinValue").innerHTML = "Tails";
            outcome = tails;
            }
        iterations-= 1;
        if(iterations<0){
            clearInterval(suspense);
        }
    }, 150);

    // Checks win condition after 2 seconds
    setTimeout(function(){
        checkWinner();
    }, 4500);
}

// Checks win condition
function checkWinner(){
    if (playerChoice === outcome){
        document.getElementById("outcome").innerHTML = "You have: WON :D";
        AUGH.play();
    }
    else{
        document.getElementById("outcome").innerHTML = "You have: LOST >:( BOO YOU SUCK!";
        womp.play();
    }
}

function readyCheck(){
    socket.emit("getHTMLPage", "getGame")
    socket.on("returned_html",  function(data) {
        console.log(data);
        document.getElementById("gameContainer").innerHTML = data["data"];
        document.getElementById("playerStatus").parentNode.removeChild(document.getElementById("playerStatus"));
        document.getElementById("ready").parentNode.removeChild(document.getElementById("ready"));
    });
}

socket.on("player_ready", function(data){
    document.getElementById("playerStatus").innerHTML = data["data"];

});

socket.on('render_message',function(data){
    console.log("data");
    console.log(data);
    $('#messages').append($('<p>').text(data));
});

socket.on("username", function(data){
    const username = data['username'];
    console.log(data);
    console.log(username);
    message_to_render(username);
});

function sendMessage() {
    console.log("hello");
    socket.emit("getUsername", ["username"]);
}
function message_to_render(username){
    console.log(username)
    const message = document.getElementById("message_box");
    const messageData = username+":"+message.value;
    console.log("message data");
    console.log(messageData);
    socket.emit("chat_message", messageData);
}

function initiate_disconnection(roomid){
    socket.emit("getUsername", ["", roomid]);
}


socket.on("remove_players", (data) => {
    console.log(data);
    document.getElementById("game_ground").parentNode.removeChild(document.getElementById("game_ground"));
    document.getElementById("diconnected_game").innerHTML = data[data];
});


//document.getElementById("coinValue").innerHTML = "Heads";
//document.getElementById("coinValue").innerHTML = "Tails";

socket.on("start_game", function(data){
    startFlipTimer();  
})