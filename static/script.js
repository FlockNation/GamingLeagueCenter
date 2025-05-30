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
      headers: {'Content-Type': 'application/json'},
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
      headers: {'Content-Type': 'application/json'},
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
  const res = await fetch('/calculate_overall', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ score_impact, risk_factor, activity })
  });
  const data = await res.json();
  if (res.ok) {
    document.getElementById('overall-result').textContent = `Overall Rating: ${data.overall}`;
  } else {
    document.getElementById('overall-result').textContent = data.error || 'Error calculating overall';
  }
}

async function simulate() {
  const results = document.getElementById('results');
  const league = document.getElementById('league').value;
  results.innerHTML = '<p>Loading simulation...</p>';
  try {
    const response = await fetch('/simulate', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ league }),
    });
    if (!response.ok) {
      throw new Error(`Server error: ${response.statusText}`);
    }
    const data = await response.json();
    if (!data.standings || !data.playoffs || !data.lottery) {
      throw new Error('Incomplete simulation data received.');
    }
    const totalGamesPerTeam = data.standings.length - 1;
    results.innerHTML = `
      <h2>Standings</h2>
      <ul>
        ${data.standings.map(t => `<li>${t[0]}: ${t[1]}W - ${totalGamesPerTeam - t[1]}L</li>`).join('')}
      </ul>
      <h2>Playoffs</h2>
      <p>Semifinals: ${data.playoffs.semis[0][0]} vs ${data.playoffs.semis[0][1]} and ${data.playoffs.semis[1][0]} vs ${data.playoffs.semis[1][1]}</p>
      <p>Final: ${data.playoffs.final[0]} vs ${data.playoffs.final[1]}</p>
      <p>Champion: <strong>${data.playoffs.champion}</strong></p>
      <h2>Draft Lottery</h2>
      <ol>${data.lottery.map(team => `<li>${team}</li>`).join('')}</ol>
    `;
  } catch (error) {
    results.innerHTML = `<p style="color:red;">Error: ${error.message}</p>`;
  }
}

async function loadPlayers() {
  const select = document.getElementById('player-select');
  select.innerHTML = '<option value="">Loading players...</option>';
  try {
    const res = await fetch('/players');
    const data = await res.json();
    if (data.players && data.players.length > 0) {
      select.innerHTML = '<option value="">Select a player</option>';
      data.players.forEach(player => {
        const option = document.createElement('option');
        option.value = player;
        option.textContent = player;
        select.appendChild(option);
      });
    } else {
      select.innerHTML = '<option value="">No players found</option>';
    }
  } catch {
    select.innerHTML = '<option value="">Failed to load players</option>';
  }
}

async function lookupPlayerOverall() {
  const select = document.getElementById('player-select');
  const player = select.value;
  const resultP = document.getElementById('player-overall-result');
  if (!player) {
    resultP.textContent = 'Please select a player.';
    return;
  }
  try {
    const res = await fetch('/player_overall', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ player })
    });
    const data = await res.json();
    if (res.ok) {
      resultP.textContent = `Overall rating for ${player}: ${data.overall}`;
    } else {
      resultP.textContent = data.error || 'Player not found';
    }
  } catch {
    resultP.textContent = 'Error fetching player overall rating.';
  }
}
