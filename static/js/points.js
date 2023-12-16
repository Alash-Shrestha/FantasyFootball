document.addEventListener("DOMContentLoaded", function () {
  var players = document.querySelectorAll(".player");

  players.forEach(function (player) {
    var playerNameElement = player.querySelector(".player-fullname");
    var playerAvatarElement = player.querySelector(".player-avatar");

    var initials = playerNameElement.textContent
      .trim()
      .split(" ")
      .map((word) => word[0])
      .join("");

    playerAvatarElement.textContent = initials;
  });
});
