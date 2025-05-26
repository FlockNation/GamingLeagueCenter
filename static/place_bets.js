document.addEventListener('DOMContentLoaded', () => {
  const bettingSection = document.getElementById('betting-section');
  const balanceP = document.getElementById('balance');
  const betResultP = document.getElementById('bet-result');

  const gameInput = document.getElementById('game');
  const teamInput = document.getElementById('team');
  const betAmountInput = document.getElementById('bet-amount');
  const placeBetBtn = document.getElementById('place-bet-btn');

  checkLoginStatus();

  placeBetBtn.onclick = async () => {
    const game = gameInput.value.trim();
    const team = teamInput.value.trim();
    const amount = parseInt(betAmountInput.value);
    betResultP.textContent = '';

    if (!game || !team || !amount || amount <= 0) {
      betResultP.textContent = 'Please fill in all bet details correctly.';
      return;
    }

    try {
      const res = await fetch('/place_bet', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ game, team, amount })
      });
      const data = await res.json();
      if (res.ok) {
        betResultP.textContent = data.message;
        updateBalance();
      } else {
        betResultP.textContent = data.error || 'Bet failed';
      }
    } catch {
      betResultP.textContent = 'Bet failed due to network error.';
    }
  };

  async function checkLoginStatus() {
    try {
      const res = await fetch('/get_balance');
      const data = await res.json();
      if (res.ok && data.balance !== undefined) {
        bettingSection.style.display = 'block';
        updateBalance();
      } else {
        window.location.href = 'login.html';
      }
    } catch {
      window.location.href = 'login.html';
    }
  }

  async function updateBalance() {
    try {
      const res = await fetch('/get_balance');
      const data = await res.json();
      if (res.ok) {
        balanceP.textContent = `Balance: ${data.balance} Coins`;
      } else {
        balanceP.textContent = 'Balance: N/A';
      }
    } catch {
      balanceP.textContent = 'Balance: N/A';
    }
  }
});
