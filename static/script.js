function hideAllSections() {
  document.getElementById('calculate-overall-section').style.display = 'none';
  document.getElementById('simulate-leagues-section').style.display = 'none';
  document.getElementById('lookup-player-section').style.display = 'none';
  const loginForm = document.getElementById('login-form');
  if (loginForm) loginForm.remove();
  clearResults();
}

function clearResults() {
  document.getElementById('overall-result').textContent = '';
  document.getElementById('results').innerHTML = '';
  document.getElementById('player-overall-result').textContent = '';
}

function showCalculateOverall() {
  hideAllSections();
  document.getElementById('calculate-overall-section').style.display = 'block';
}

function showSimulateLeagues() {
  hideAllSections();
  document.getElementById('simulate-leagues-section').style.display = 'block';
}

function showLookupPlayer() {
  hideAllSections();
  document.getElementById('lookup-player-section').style.display = 'block';
  loadPlayers();
}

function showLoginForm() {
  hideAllSections();
  clearResults();
  const container = document.querySelector('.container');
  const existingForm = document.getElementById('login-form');
  if (existingForm) existingForm.remove();

  const form = document.createElement('div');
  form.id = 'login-form';
  form.innerHTML = `
    <h2>Login</h2>
    <input type="text" id="login-username" placeholder="Username" />
    <button onclick="loginUser()">Login</button>
    <p id="login-message"></p>
    <hr />
    <h3>Register</h3>
    <input type="text" id="register-username" placeholder="New Username" />
    <button onclick="registerUser()">Register</button>
    <p id="register-message"></p>
  `;
  container.appendChild(form);
}

async function loginUser() {
  const username = document.getElementById('login-username').value.trim();
  const msg = document.getElementById('login-message');
  if (!username) {
    msg.textContent = 'Please enter a username.';
    return;
  }

  try {
    const res = await fetch('/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username })
    });

    const data = await res.json();
    if (res.ok) {
      msg.style.color = 'green';
      msg.textContent = `Logged in! Balance: ${data.balance}`;
      setTimeout(() => {
        window.location.href = '/place_bets';
      }, 1000);
    } else {
      msg.style.color = 'red';
      msg.textContent = data.error || 'Login failed';
    }
  } catch {
    msg.style.color = 'red';
    msg.textContent = 'Error during login.';
  }
}

async function registerUser() {
  const username = document.getElementById('register-username').value.trim();
  const msg = document.getElementById('register-message');
  if (!username) {
    msg.textContent = 'Please enter a username.';
    return;
  }

  try {
    const res = await fetch('/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username })
    });

    const data = await res.json();
    if (res.ok) {
      msg.style.color = 'green';
      msg.textContent = 'User registered! You can now log in.';
    } else {
      msg.style.color = 'red';
      msg.textContent = data.error || 'Registration failed';
    }
  } catch {
    msg.style.color = 'red';
    msg.textContent = 'Error during registration.';
  }
}

async function calculateOverall() {
  const score_impact = parseInt(document.getElementById('score_impact').value);
  const risk_factor = parseInt(document.getElementById('risk_factor').value);
  const activity = parseInt(document.getElementById('activity').value);

  try {
    const res = await fetch('/calculate_overall', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ score_impact, risk_factor, activity })
    });

    const data = await res.json();
    if (res.ok) {
      document.getElementById('overall-result').textContent = `Overall Rating: ${data.overall}`;
    } else {
      document.getElementById('overall-result').textContent = data.error || 'Error calculating overall';
    }
  } catch {
    document.getElementById('overall-result').textContent = 'Error calculating overall.';
  }
}

async function simulate() {
  const league = document.getElementById('league').value;
  const results = document.getElementById('results');
  results.innerHTML = '<p>Loading simulation...</p>';

  try {
    const res = await fetch('/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ league })
    });

    if (!res.ok) throw new Error(`Server error: ${res.statusText}`);
    const data = await res.json();

    const formatRecord = (teamRecord, league) => {
      const wins = teamRecord[1];
      const totalGames = league === 'SLOG' ? 3 : 4;
      const losses = totalGames - wins;
      return `${wins}-${losses}`;
    };

    const playoffsHTML = league === 'SLOG'
      ? data.playoffs.semis.map(m => `<li>${m.round}: ${m.teams[0]} vs ${m.teams[1]}</li>`).join('')
      : Object.entries(data.playoffs.semis).map(([round, teams]) => `<li>${round}: ${teams[0]} vs ${teams[1]}</li>`).join('');

    const finalMatch = data.playoffs.final.join(' vs ');
    const standingsHTML = data.standings.map(t => `<li>${t[0]}: ${formatRecord(t, league)}</li>`).join('');
    const draftHTML = data.lottery.map(team => `<li>${team}</li>`).join('');

    results.innerHTML = `
      <h2>Standings</h2>
      <ul>${standingsHTML}</ul>
      <h2>Playoffs</h2>
      <ul>${playoffsHTML}</ul>
      <p><strong>Final:</strong> ${finalMatch}</p>
      <p><strong>Champion:</strong> ${data.playoffs.champion}</p>
      <h2>Draft</h2>
      <ol>${draftHTML}</ol>
    `;
  } catch (err) {
    results.innerHTML = `<p style="color: red;">${err.message}</p>`;
  }
}

async function loadPlayers() {
  const select = document.getElementById('player-select');
  select.innerHTML = '<option value="">Loading players...</option>';

  try {
    const res = await fetch('/players');
    const data = await res.json();
    select.innerHTML = '<option value="">Select a player</option>';
    data.players.forEach(player => {
      const option = document.createElement('option');
      option.value = player;
      option.textContent = player;
      select.appendChild(option);
    });
  } catch (err) {
    console.error('Error loading players:', err);
    select.innerHTML = '<option value="">Error loading players</option>';
  }
}

async function lookupPlayerOverall() {
  const select = document.getElementById('player-select');
  const player = select.value;

  const result = document.getElementById('player-overall-result');
  if (!player) {
    result.textContent = 'Please select a player.';
    return;
  }

  try {
    const res = await fetch('/player_overall', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player })
    });

    const data = await res.json();
    if (data.error) {
      result.textContent = 'Error: ' + data.error;
    } else {
      result.textContent = `${player}'s overall: ${data.overall}`;
    }
  } catch (err) {
    console.error('Failed to fetch player overall:', err);
    result.textContent = 'Error fetching data.';
  }
}
