<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Login</title>
</head>
<body>
  <h1>Login</h1>
  <form id="login-form">
    <input type="text" id="username" placeholder="Enter username" required />
    <button type="submit">Login</button>
  </form>
  <p id="message"></p>

  <script>
    const form = document.getElementById('login-form');
    const messageP = document.getElementById('message');

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const username = document.getElementById('username').value.trim();

      if (!username) {
        messageP.textContent = 'Please enter a username.';
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
          window.location.href = '/place_bets';
        } else {
          messageP.textContent = data.error || 'Login failed';
        }
      } catch (err) {
        messageP.textContent = 'Error connecting to server.';
      }
    });
  </script>
</body>
</html>
