const slug = JSON.parse(document.getElementById('room-slug').textContent);
const username = JSON.parse(document.getElementById('username').textContent);
const messages = document.getElementById('messages');
const form = document.getElementById('message-form');
const input = document.getElementById('message-input');
const status = document.getElementById('connection-status');
const error = document.getElementById('error-message');
const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
const socket = new WebSocket(`${protocol}://${window.location.host}/ws/chat/${slug}/`);


function scrollToLatest() {
  messages.scrollTop = messages.scrollHeight;
}

function addMessage(data) {
  document.getElementById('empty-state')?.remove();
  const article = document.createElement('article');
  article.className = 'message';
  const meta = document.createElement('div');
  meta.className = 'message-meta';
  const sender = document.createElement('strong');
  sender.textContent = data.username;
  const time = document.createElement('time');
  time.textContent = new Date(data.timestamp).toLocaleString();
  meta.append(sender, time);
  const text = document.createElement('p');
  text.textContent = data.message;
  article.append(meta, text);
  messages.appendChild(article);
  scrollToLatest();
}

socket.addEventListener('open', () => {
  status.textContent = 'Connected';
  status.className = 'status connected';
  input.focus();
});
socket.addEventListener('close', () => {
  status.textContent = 'Disconnected';
  status.className = 'status disconnected';
});
socket.addEventListener('error', () => {
  status.textContent = 'Connection error';
  status.className = 'status disconnected';
});
socket.addEventListener('message', (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'message') addMessage(data);
  if (data.type === 'error') error.textContent = data.message;
});
form.addEventListener('submit', (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message || socket.readyState !== WebSocket.OPEN) return;
  socket.send(JSON.stringify({username, message}));
  input.value = '';
  error.textContent = '';
});
scrollToLatest();
