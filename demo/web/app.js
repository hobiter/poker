(() => {
  const $ = id => document.getElementById(id);
  const serverUrlEl = $('serverUrl');
  const roomIdEl = $('roomId');
  const playerIdEl = $('playerId');
  const displayNameEl = $('displayName');
  const messagesEl = $('messages');

  let ws = null;

  function append(msg) {
    if (!msg) return;
    if (typeof msg !== 'string') msg = JSON.stringify(msg, null, 2);
    if (messagesEl.textContent === '(no messages yet)') messagesEl.textContent = '';
    messagesEl.textContent += msg + '\n\n';
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function base() {
    return serverUrlEl.value.replace(/\/+$/, '');
  }

  async function createRoom() {
    const payload = {
      seat_count: 6,
      game_type: 'no-limit',
      blinds: { small: 5, big: 10 },
      starting_stack: 2000,
      name: 'Browser Demo Room'
    };
    const res = await fetch(base() + '/rooms', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
    });
    const j = await res.json();
    roomIdEl.value = j.roomId;
    append({ action: 'create_room', resp: j });
  }

  async function joinRoom() {
    const roomId = roomIdEl.value.trim();
    if (!roomId) return alert('Room ID required');
    const res = await fetch(base() + '/rooms/' + roomId + '/join', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ display_name: displayNameEl.value || 'web' })
    });
    const j = await res.json();
    playerIdEl.value = j.playerId;
    append({ action: 'join_room', resp: j });
  }

  function wsUrlFor(roomId, playerId) {
    const b = base();
    const wsBase = b.replace(/^https:/, 'wss:').replace(/^http:/, 'ws:');
    return wsBase + '/ws/' + encodeURIComponent(roomId) + '/' + encodeURIComponent(playerId);
  }

  function openWebSocket() {
    const roomId = roomIdEl.value.trim();
    const playerId = playerIdEl.value.trim();
    if (!roomId || !playerId) return alert('Room ID and Player ID required');
    const url = wsUrlFor(roomId, playerId);
    append({ action: 'ws_connect', url });
    ws = new WebSocket(url);
    ws.onopen = () => append({ ws: 'open' });
    ws.onclose = () => append({ ws: 'closed' });
    ws.onerror = e => append({ ws: 'error', e: String(e) });
    ws.onmessage = ev => {
      try { append(JSON.parse(ev.data)); } catch (e) { append(ev.data); }
    };
  }

  async function startHand() {
    const roomId = roomIdEl.value.trim();
    if (!roomId) return alert('Room ID required');
    const res = await fetch(base() + '/rooms/' + roomId + '/start_hand', { method: 'POST' });
    append({ action: 'start_hand', resp: await res.json() });
  }

  function sendAction() {
    if (!ws || ws.readyState !== WebSocket.OPEN) return alert('WebSocket not open');
    const msg = { type: 'action:post', payload: { actionType: 'call' } };
    ws.send(JSON.stringify(msg));
    append({ sent: msg });
  }

  async function forceTimeout() {
    const roomId = roomIdEl.value.trim();
    if (!roomId) return alert('Room ID required');
    const res = await fetch(base() + '/rooms/' + roomId + '/force_timeout', { method: 'POST' });
    append({ action: 'force_timeout', resp: await res.json() });
  }

  $('createRoomBtn').addEventListener('click', createRoom);
  $('joinBtn').addEventListener('click', joinRoom);
  $('wsConnectBtn').addEventListener('click', openWebSocket);
  $('startHandBtn').addEventListener('click', startHand);
  $('sendActionBtn').addEventListener('click', sendAction);
  $('forceTimeoutBtn').addEventListener('click', forceTimeout);

  // expose for debugging
  window._pokerDemo = { append };

})();
