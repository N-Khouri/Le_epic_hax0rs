"use strict";
const X = 1;
const O = 2;
const empty = 0;

const gameStatus = document.querySelector(".gameStatus");
const tiles = Array.from(document.querySelectorAll(".tile"));
console.log(tiles)
//if a game is going on currently
let currentGame = true;

//X always plays first
let currentTurn = X;

//temporarily storing the game in array 
let gamestate = ["", "", "", "", "", "", "", "", ""];

//conditions to check if the player has won the game
const combinations = [
    [0,1,2], //rows 
    [3,4,5],
    [6,7,8],
    [0,4,8], //diagonals
    [2,4,6],
    [0,3,6], //columns
    [1,4,7],
    [2,5,8]
];

const PlayerTurn = () => ` ${currentTurn}'s turn`;
const winMessage = () => ` Player ${currentTurn} has won the game!`;
const drawMessage = () => `The game is a draw!`;
gameStatus.innerHTML = PlayerTurn();

tiles.forEach((tile,index) => {
    tile.addEventListener('click', () => useraction(tile, index));
});

//function to find which cell the player placed symbol on
function cellPlayed(clickedcell, cellIndex){
    gamestate[cellIndex] = currentTurn;
    clickedcell.innerHTML = currentTurn;
}

//switches the players turn
function switchPlayerTurn(){
    currentTurn = currentTurn == X ? O : X;
    gameStatus.innerHTML = PlayerTurn();
}

//checks the condition of the game after every turn
function checkResult(){
    let Win = false;
    for (let i =0; i<8 ; i++){
        const condition = combinations[i];
        let a = gamestate[condition[0]];
        let b = gamestate[condition[1]];
        let c = gamestate[condition[2]];
        if (a == "" || b == "" || c == ""){
            continue;
        }

        if ((a == b) && (b == c)){
            Win = true;
            break;
        }
    }

    // to check if the round is won
    if(Win){
        //display draw win message
        currentGame = false;
        return;
    }

    //to check if the round is draw
    let Draw = !gamestate.includes("");
    if(Draw){
        // display draw message
        currentGame = false;
        return;
    }

    switchPlayerTurn();
}


//function to get the coordinate of the cell player just played, NEED CHRIS'S HELP FOR HTML ELEMENT
function cellClicked(event){
    const clickedcell = event.target;

    const cellIndex = parseInt(clickedcell.getAttribute('coordinate'));

    if(gamestate[cellIndex] !== "" || !currentGame){
        return;
    }

    cellPlayed(clickedcell, cellIndex);
    checkResult();
}


//reset the game to original stuff
function RestartGame(){
    currentGame = true;
    currentTurn = X;

    //reset the game data structure to empty
    //gamestate = ["", "", "", "", "", "", "", "", ""];
    
    gameStatus.innerHTML = PlayerTurn();

    //resets the values of html elements to empty
    document.querySelectorAll('.div').forEach(cell => cell.innerHTML = "");

}

//adding listeners for when the players play the game, to listen for "click" and check each condition
document.querySelectorAll('.div').forEach(cell => cell.addEventListener('click', cellClicked));
//document.querySelector('restartGame').addEventListener('click', RestartGame);


// //ask chris what this do
// function initializeHTML(){
//     for (let i = 0; i <= 8; i++){
//         const divElement = document.createElement('div');
//         divElement.id = "grid"+String(i);
//         divElement.setAttribute("coordinate", i)
//         divElement.innerHTML += "hello";
//         document.body.appendChild(divElement);
//     }
// }

