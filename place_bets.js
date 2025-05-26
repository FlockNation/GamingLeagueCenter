document.addEventListener('DOMContentLoaded', () => {
  const loginSection = document.getElementById('login-section');
  const bettingSection = document.getElementById('betting-section');
  const authMessage = document.getElementById('auth-message');
  const balanceP = document.getElementById('balance');
  const betResultP = document.getElementById('bet-result');

  const usernameInput = document.getElementById('username');
  const gameInput = document.getElementById('game');
  const teamInput = document.getElementById('team');
  const betAmountInput = document.getElementById('bet-amount');

  const registerBtn = document.getElementById('register-btn');
  const loginBtn = document.getElementById('login-btn');
  const logoutBtn = document.getElementById('logout-btn');
  const placeBetBtn = document.getElementById('place-bet-btn');

  checkLoginStatus();

  registerBtn.onclick = async () => {
    const username = usernameInput.value.trim();
    if (!username) {
      authMessage.textContent = 'Please enter a username.';
      return;
    }
    try {
      const res = await fetch('/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ username })
      });
      const data = await res.json();
      authMessage.textContent = data.message || 'Registered.';
      if (res.ok) {
        showBettingSection();
      }
    } catch {
      authMessage.textContent = 'Registration failed.';
    }
  };

  loginBtn.onclick = async () => {
    const username = usernameInput.value.trim();
    if (!username) {
      authMessage.textContent = 'Please enter a username.';
      return;
    }
    try {
      const res = await fetch('/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ username })
      });
      const data = await res.json();
      authMessage.textContent = data.message || 'Logged in.';
      if (res.ok) {
        showBettingSection();
      }
    } catch {
      authMessage.textContent = 'Login failed.';
    }
  };

  logoutBtn.onclick = async () => {
    try {
      const res = await fetch('/logout', { method: 'POST' });
      const data = await res.json();
      authMessage.textContent = data.message || 'Logged out.';
      showLoginSection();
    } catch {
      authMessage.textContent = 'Logout failed.';
    }
  };

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
        headers: {'Content-Type': 'application/json'},
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
        showBettingSection(data.balance);
      } else {
        showLoginSection();
      }
    } catch {
      showLoginSection();
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

  function showLoginSection() {
    loginSection.style.display = 'block';
    bettingSection.style.display = 'none';
    authMessage.textContent = '';
    betResultP.textContent = '';
    usernameInput.value = '';
    gameInput.value = '';
    teamInput.value = '';
    betAmountInput.value = '';
    balanceP.textContent = 'Balance: 0 Coins';
  }

  function showBettingSection(balance) {
    loginSection.style.display = 'none';
    bettingSection.style.display = 'block';
    betResultP.textContent = '';
    updateBalance();
  }
});
