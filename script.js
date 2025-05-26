let csvData = [];

function showCalculator() {
  document.getElementById("calculator").style.display = "block";
}

function loadCSV() {
  Papa.parse("gaming_league_overall.csv", {
    download: true,
    header: true,
    complete: function(results) {
      csvData = results.data;
    }
  });
}

function calculateOverall() {
  const score = parseInt(document.getElementById("scoreInput").value);
  const risk = parseInt(document.getElementById("riskInput").value);
  const activity = parseInt(document.getElementById("activityInput").value);

  if (![score, risk, activity].every(v => v >= 1 && v <= 10)) {
    document.getElementById("output").innerText = "Please enter numbers between 1 and 10.";
    return;
  }

  const match = csvData.find(row =>
    parseInt(row.ScoreImpact) === score &&
    parseInt(row.RiskFactor) === risk &&
    parseInt(row.Activity) === activity
  );

  if (match) {
    document.getElementById("output").innerText = `Your Overall Rating: ${match.Overall}`;
  } else {
    document.getElementById("output").innerText = "Combination not found.";
  }
}

loadCSV();
