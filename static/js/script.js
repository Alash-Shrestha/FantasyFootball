document.addEventListener("DOMContentLoaded", function () {
  const playerList = document.getElementById("player-list");
  const footballField = document.getElementById("football-field");
  const playersList = document.getElementById("players-list");
  const submitBtn = document.getElementById("submitBtn");
  const addPlayerBtns = document.querySelectorAll(".add-player-btn");
  const searchInput = document.getElementById("searchInput");

  const selectedPlayers = {};
  let availablePositions = [1, 2, 3, 4, 5];

  addPlayerBtns.forEach((btn) => {
    btn.addEventListener("click", function () {
      const selectedPlayer = btn.parentNode.textContent.trim();

      if (Object.keys(selectedPlayers).length >= 5) {
        alert("You can only select up to 5 players.");
        return;
      }

      if (selectedPlayers[selectedPlayer]) {
        alert("You have already selected this player.");
        return;
      }

      const nextPosition = availablePositions.shift();

      selectedPlayers[selectedPlayer] = nextPosition;

      footballField.innerHTML = "";
      Object.keys(selectedPlayers).forEach((playerName) => {
        const playerElement = createPlayerElement(
          playerName,
          selectedPlayers[playerName]
        );
        footballField.appendChild(playerElement);
      });
    });
  });

  submitBtn.addEventListener("click", function () {
    alert("Selected Players: " + JSON.stringify(selectedPlayers));
  });

  searchInput.addEventListener("input", function () {
    const searchText = searchInput.value.toLowerCase();
    const allPlayers = Array.from(playersList.children);

    allPlayers.forEach((player) => {
      const playerName = player.textContent.toLowerCase();
      if (playerName.includes(searchText)) {
        player.style.display = "flex";
      } else {
        player.style.display = "none";
      }
    });
  });

  function createPlayerElement(name, position) {
    const playerElement = document.createElement("div");
    playerElement.className = "player";

    // Get the initials of the first and last names
    const initials = name
      .split(" ")
      .map((part) => part.charAt(0).toUpperCase())
      .join("");

    playerElement.textContent = initials;

    // Create a div for the full name below the circle
    const fullNameDiv = document.createElement("div");
    fullNameDiv.textContent = name.slice(0, -1);
    fullNameDiv.className = "full-name";
    playerElement.appendChild(fullNameDiv);

    const deleteBtn = document.createElement("button");
    deleteBtn.className = "delete-btn";
    deleteBtn.innerHTML = "x";
    deleteBtn.addEventListener("click", function () {
      footballField.removeChild(playerElement);

      const deletedPosition = selectedPlayers[name];
      if (deletedPosition) {
        availablePositions.push(deletedPosition);
      }

      delete selectedPlayers[name];
    });

    playerElement.appendChild(deleteBtn);

    // Add the player element to the field
    footballField.appendChild(playerElement);

    switch (position) {
      case 1:
        playerElement.style.left = "50%";
        playerElement.style.top = "10px";
        break;
      case 2:
        playerElement.style.left = "25%";
        playerElement.style.top = "30%";
        break;
      case 3:
        playerElement.style.left = "75%";
        playerElement.style.top = "30%";
        break;
      case 4:
        playerElement.style.left = "50%";
        playerElement.style.top = "60%";
        break;
      case 5:
        playerElement.style.left = "50%";
        playerElement.style.top = "80%";
        break;
    }

    return playerElement;
  }
});
