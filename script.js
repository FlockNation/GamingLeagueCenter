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
    <ul>${data.standings.map(t => `<li>${t[0]}: ${t[1]} wins</li>`).join("")}</ul>

    <h2>Playoffs</h2>
    <p>Semifinals: ${data.playoffs.semis[0][0]} vs ${data.playoffs.semis[0][1]} and ${data.playoffs.semis[1][0]} vs ${data.playoffs.semis[1][1]}</p>
    <p>Final: ${data.playoffs.final[0]} vs ${data.playoffs.final[1]}</p>
    <p>Champion: <strong>${data.playoffs.champion}</strong></p>

    <h2>Draft Lottery</h2>
    <ol>${data.lottery.map(team => `<li>${team}</li>`).join("")}</ol>
  `;
}
