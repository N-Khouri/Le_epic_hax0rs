// Grid, ship placement, missile hit condition, win condition, turn-base functionality

// Grid: 2d array 10x10 populated by 0's and 1's

// Ship placement: Need to keep track of ships within a list of dictionaries and update Grid to correlate to where ships are placed at

// Missile hit condition: When clicking on an enemy grid we need to check if there is a 1 on the enemy grid. If yes, reduce enemies health by 1 and make that grid spot unable to be hit again, and mark spot by an x.
// if no,  update grid with an x and make it unable to be hit again.

// Win condition: If health reaches 0 you lose.

// Turn-base functionality: When user1 takes a turn and he hits then he takes another turn, if he misses then enemy starts his turn.

// Size of ships: 5, 4, 3, 3, 2

// Possible Grid Values = 0: No ship, 1: Ship, 2: Ship hit, 3: Ship miss
/* [
  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]
*/

// Health for user 1 = 18
// Health for user 2 = 18
// Generate unique id for each live match
// Obtain usernames for both users participating in the match
// At game end send POST requests for both users to increase their wins and total games
"use strict";

var grid = Array(10).fill(Array(10).fill(0));
var userHealth = 18;

var shipsOfUser1 = [{ship1: [(,),(,),(,),(,),(,)], ship2: [(,),(,),(,),(,)], ship3: [(,),(,),(,)], ship4: [(,),(,),(,)], ship5: [(,),(,)]}];

function hitCheck(coordinate) {
    let x = coordinate[0];
    let y = coordinate[1];

    let gridSpot = this.grid[x][y];

    if (gridSpot == 3 || gridSpot == 2){
        alert("You've already hit this spot, try a different one! Ya goober")
        // Do not end turn
    }
    else if (gridSpot = 1){
        document.getElementById("healthUser2") --;
        healthUser2 --;
        this.grid[x][y] = 2
        // Do not end turn
    }
    else{
        this.grid[x][y] = 3
        // End turn
    }
}

function winCheck(userHealth){
    if (userHealth <= 0){
        alert("You lost, boo you stink")
    }
    // send information to server.py / Joey, POST request
}