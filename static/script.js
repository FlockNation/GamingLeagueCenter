function hideAllSections() {
  document.getElementById('calculate-overall-section').style.display = 'none';
  document.getElementById('simulate-leagues-section').style.display = 'none';
  document.getElementById('lookup-player-section').style.display = 'none';
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
  const league = document.getElementById('league').value;

  const response = await fetch('/simulate', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ league })
  });

  const data = await response.json();
  const totalGamesPerTeam = data.standings.length - 1;

  const results = document.getElementById('results');
  results.innerHTML = `
    <h2>Standings</h2>
    <ul>${data.standings.map(t => `<li>${t[0]}: ${t[1]}W - ${totalGamesPerTeam - t[1]}L</li>`).join('')}</ul>

    <h2>Playoffs</h2>
    <p>Semifinals: ${data.playoffs.semis[0][0]} vs ${data.playoffs.semis[0][1]} and ${data.playoffs.semis[1][0]} vs ${data.playoffs.semis[1][1]}</p>
    <p>Final: ${data.playoffs.final[0]} vs ${data.playoffs.final[1]}</p>
    <p>Champion: <strong>${data.playoffs.champion}</strong></p>

    <h2>Draft Lottery</h2>
    <ol>${data.lottery.map(team => `<li>${team}</li>`).join('')}</ol>
  `;
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
