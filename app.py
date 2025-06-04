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
      credentials: 'include',
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
  try {
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
  } catch (err) {
    document.getElementById('overall-result').textContent = 'Error calculating overall';
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

    const formatRecord = (teamRecord, league) => {
      const wins = teamRecord[1];
      const totalGames = league === 'SLOG' ? 3 : 4;
      const losses = totalGames - wins;
      return `${wins}-${losses}`;
    };

    if (league === 'SLOG') {
      if (
        typeof data.standings !== 'object' ||
        !Array.isArray(data.standings) ||
        !Array.isArray(data.playoffs.semis) ||
        !Array.isArray(data.playoffs.final) ||
        data.playoffs.final.length !== 3 ||
        !data.playoffs.champion
      ) {
        throw new Error('Incomplete simulation data received for SLOG.');
      }
      results.innerHTML = `
        <h2>Standings</h2>
        <ul>
          ${data.standings.map(t => `<li>${t[0]}: ${formatRecord(t, league)}</li>`).join('')}
        </ul>
        <h2>Playoffs</h2>
        <ul>
          ${data.playoffs.semis.map(match => `<li>${match.round}: ${match.teams[0]} vs ${match.teams[1]}</li>`).join('')}
        </ul>
        <p><strong>Final:</strong> ${data.playoffs.final.join(' vs ')}</p>
        <p><strong>Champion:</strong> ${data.playoffs.champion}</p>
        <h2>Draft</h2>
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
          ${data.standings.map(t => `<li>${t[0]}: ${formatRecord(t, league)}</li>`).join('')}
        </ul>
        <h2>Playoffs</h2>
        <ul>
          ${Object.entries(data.playoffs.semis).map(([round, teams]) => `<li>${round}: ${teams[0]} vs ${teams[1]}</li>`).join('')}
        </ul>
        <p><strong>Final:</strong> ${data.playoffs.final.join(' vs ')}</p>
        <p><strong>Champion:</strong> ${data.playoffs.champion}</p>
        <h2>Draft</h2>
        <ol>${data.lottery.map(team => `<li>${team}</li>`).join('')}</ol>
      `;
    }
  } catch (error) {
    results.innerHTML = `<p style="color: red;">${error.message}</p>`;
  }
}

async function loadPlayers() {
  const select = document.getElementById('player-select');
  select.innerHTML = '<option value="">Loading players...</option>';

  try {
    const res = await fetch('/players');
    const data = await res.json();
    const players = data.players;

    select.innerHTML = '<option value="">Select a player</option>';
    players.forEach(player => {
      const option = document.createElement('option');
      option.value = player;
      option.textContent = player;
      select.appendChild(option);
    });
  } catch (error) {
    console.error('Error loading players:', error);
    select.innerHTML = '<option value="">Error loading players</option>';
  }
}

async function lookupPlayerOverall() {
  const select = document.getElementById('player-select');
  const player = select.value;

  if (!player) {
    document.getElementById('player-overall-result').textContent = 'Please select a player.';
    return;
  }

  try {
    const res = await fetch('/player_overall', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ player })
    });

    const data = await res.json();

    if (data.error) {
      document.getElementById('player-overall-result').textContent = 'Error: ' + data.error;
    } else {
      document.getElementById('player-overall-result').textContent = `${player}'s overall: ${data.overall}`;
    }
  } catch (err) {
    console.error('Failed to fetch player overall:', err);
    document.getElementById('player-overall-result').textContent = 'Error fetching data.';
  }
}


async function placeBet(game, team, amount) {
  try {
    const res = await fetch('/place_bet', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      credentials: 'include',
      body: JSON.stringify({ game, team, amount })
    });
    const data = await res.json();
    if (res.ok) {
      alert(data.message + " New balance: " + data.balance);
      await updateBalanceDisplay();
    } else {
      alert(data.error || 'Bet failed');
    }
  } catch (err) {
    alert('Error placing bet.');
  }
}

async function updateBalanceDisplay() {
  const el = document.getElementById('user-balance');
  if (!el) return;
  try {
    const res = await fetch('/get_balance', {
      method: 'GET',
      credentials: 'include',
    });
    const data = await res.json();
    if (res.ok && data.balance !== undefined) {
      el.textContent = `Balance: ${data.balance}`;
    } else {
      el.textContent = 'Balance: N/A';
    }
  } catch {
    el.textContent = 'Balance: N/A';
  }
}

async function logoutUser() {
  try {
    const res = await fetch('/logout', {
      method: 'POST',
      credentials: 'include'
    });
    if (res.ok) {
      window.location.href = '/';
    }
  } catch {
    alert('Logout failed.');
  }
}
