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

    if (league === 'SLOG') {
      if (
        typeof data.standings !== 'object' ||
        !Array.isArray(data.standings.Canada) ||
        !Array.isArray(data.standings.USA) ||
        typeof data.playoffs.semis !== 'object' ||
        !Array.isArray(data.playoffs.final) ||
        data.playoffs.final.length !== 3 ||
        !data.playoffs.champion
      ) {
        throw new Error('Incomplete simulation data received for SLOG.');
      }
      results.innerHTML = `
        <h2>Canada Conference Standings</h2>
        <ul>
          ${data.standings.Canada.map(t => `<li>${t[0]}: ${t[1]}W</li>`).join('')}
        </ul>
        <h2>USA Conference Standings</h2>
        <ul>
          ${data.standings.USA.map(t => `<li>${t[0]}: ${t[1]}W</li>`).join('')}
        </ul>
        <h2>Playoffs</h2>
        <ul>
          ${Object.entries(data.playoffs.semis).map(([round, teams]) => `<li>${round}: ${teams[0]} vs ${teams[1]}</li>`).join('')}
        </ul>
        <p><strong>Final:</strong> ${data.playoffs.final.join(' vs ')}</p>
        <p><strong>Champion:</strong> ${data.playoffs.champion}</p>
        <h2>Draft Lottery</h2>
        <ol>${data.lottery.map(team => `<li>${team}</li>`).join('')}</ol>
      `;
    } else {
      if (
        !Array.isArray(data.standings) ||
        typeof data.playoffs.semis !== 'object' ||
        !Array.isArray(data.playoffs.final) ||
        data.playoffs.final.length !== 2 ||
        !data.playoffs.champion
      ) {
        throw new Error('Incomplete simulation data received.');
      }
      results.innerHTML = `
        <h2>Standings</h2>
        <ul>
          ${data.standings.map(t => `<li>${t[0]}: ${t[1]}W</li>`).join('')}
        </ul>
        <h2>Playoffs</h2>
        <ul>
          ${Object.entries(data.playoffs.semis).map(([round, teams]) => `<li>${round}: ${teams[0]} vs ${teams[1]}</li>`).join('')}
        </ul>
        <p><strong>Final:</strong> ${data.playoffs.final.join(' vs ')}</p>
        <p><strong>Champion:</strong> ${data.playoffs.champion}</p>
        <h2>Draft Lottery</h2>
        <ol>${data.lottery.map(team => `<li>${team}</li>`).join('')}</ol>
      `;
    }
  } catch (error) {
    results.innerHTML = `<p style="color: red;">${error.message}</p>`;
  }
}

function loadPlayers() {}
