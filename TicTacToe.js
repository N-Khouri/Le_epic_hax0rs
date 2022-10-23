const X = 1;
const O = 2;
const empty = 0;

const gameStatus = document.querySelector(".gameStatus")
const gameBoard = document.getElementById("board");
const winningMessage = document.getElementById("winMessage");
const DisplayMessage = document.getElementById("DisplayMessage");

//X always plays first
let currentTurn = X;
const PlayerTurn = () => ` ${currentTurn}'s turn`;

gameStatus.innerHTML = PlayerTurn();

//conditions to check if the player has won the game
const combinations = [
    [0,1,2], //rows across
    [3,4,5],
    [6,7,8],
    [0,4,8], //diagonals
    [2,4,6],
    [0,3,6],
    [1,4,7],
    [2,5,8]
]

function grid(gridSize){
    this.size = gridSize;
    this.gridCells = [];
    this.initialize();
}


function initializeHTML(){
    for (let i = 0; i <= 8; i++){
        const divElement = document.createElement('div');
        divElement.id = "grid"+String(i);
        divElement.setAttribute("coordinate", i)
        divElement.innerHTML += "hello";
        document.body.appendChild(divElement);
    }
}

//switches the players turn
function switchPlayerTurn(){
    O_turn = !O_turn;
}

