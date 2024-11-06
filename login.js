const loginPopup = document.getElementById('loginPopup');
const loginButton = document.getElementById('loginButton');
const closeButton = document.getElementById('closeButton');

loginButton.addEventListener('click', function() {
  loginPopup.style.display = 'block';
});

closeButton.addEventListener('click', function() {
  loginPopup.style.display = 'none';
});

// idk whats going on lol help pls