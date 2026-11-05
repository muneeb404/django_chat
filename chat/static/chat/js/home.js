const usernameInput = document.getElementById('username-input');

usernameInput.addEventListener('input', () => {
  document.getElementById('create-username').value = usernameInput.value;
  document.querySelectorAll('.join-username').forEach((field) => {
    field.value = usernameInput.value;
  });
});
