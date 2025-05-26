function showSection(sectionId) {
  document.getElementById('calculate').style.display = 'none';
  document.getElementById('simulate').style.display = 'none';
  document.getElementById(sectionId).style.display = 'block';
}

window.onload = () => {
  showSection('simulate');
}

async function calculateOverall() {
  const scoreImpact = parseInt(document.getElementById('scoreImpact').value);
  const riskFactor = parseInt(document.getElementById('riskFactor').value);
  const activityLevel = parseInt(document.getElementById('activityLevel').value);

  if (
    isNaN(scoreImpact) || scoreImpact < 1 || scoreImpact > 10 ||
    isNaN(riskFactor) || riskFactor < 1 || riskFactor > 10 ||
    isNaN(activityLevel) || activityLevel < 1 || activityLevel > 10
  ) {
    alert("Please enter valid numbers between 1 and 10 for all fields.");
    return;
  }

  const response = await fetch('/calculate_overall', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ score_impact: scoreImpact, risk_factor: riskFactor, activity: activityLevel })
  });

  const data = await response.json();
  const resultDiv = document.getElementById('overallResult');

  if (response.ok) {
    resultDiv.textContent = `Overall Rating: ${data.overall}`;
  } else {
    resultDiv.textContent = data.error || "Error calculating overall.";
  }
}

async function simulate() {
  const league = document.getElementById("league").value;

  const response = await fetch('/simulate', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ league })
  });

  const data = await response.json();

  const results = document.getElementById("results");
  results.innerHTML = `
    <h2>Standings</h2>
    <ul>${data.standings.map(t => `<li>${t[0]}: ${t[1]}–${t[2]}</li>`).join("")}</ul>

    <h2>Playoffs</h2>
    <p>Semifinals: ${data.playoffs.semis[0][0]} vs ${data.playoffs.semis[0][1]} and ${data.playoffs.semis[1][0]} vs ${data.playoffs.semis[1][1]}</p>
    <p>Final: ${data.playoffs.final[0]} vs ${data.playoffs.final[1]}</p>
    <p>Champion: <strong>${data.playoffs.champion}</strong></p>

    <h2>Draft Lottery</h2>
    <ol>${data.lottery.map(team => `<li>${team}</li>`).join("")}</ol>
  `;
}
