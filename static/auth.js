document.addEventListener('DOMContentLoaded', () => {
  // Container Elements
  const loginSection = document.getElementById('loginSection');
  const registerSection = document.getElementById('registerSection');
  const goToRegister = document.getElementById('goToRegister');
  const goToLogin = document.getElementById('goToLogin');

  // Form Elements
  const loginForm = document.getElementById('loginForm');
  const registerForm = document.getElementById('registerForm');

  // Toggle to Register View
  if (goToRegister) {
    goToRegister.addEventListener('click', (e) => {
      e.preventDefault();
      loginSection.classList.add('hidden');
      registerSection.classList.remove('hidden');
    });
  }

  // Toggle to Login View
  if (goToLogin) {
    goToLogin.addEventListener('click', (e) => {
      e.preventDefault();
      registerSection.classList.add('hidden');
      loginSection.classList.remove('hidden');
    });
  }

  // Handle User Registration
  if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      const emailInput = document.getElementById('regEmail');
      const passwordInput = document.getElementById('regPassword');
      const usernameInput = document.getElementById('regUsername');
      const btn = document.getElementById('regBtn');

      const email = emailInput ? emailInput.value.trim() : '';
      const password = passwordInput ? passwordInput.value : '';
      const username = usernameInput ? usernameInput.value.trim() : '';

      if (!email || !password) {
        alert('Please provide both an email and password.');
        return;
      }

      btn.innerText = 'Creating Account...';
      btn.disabled = true;

      try {
        const response = await fetch('/api/v1/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password, username })
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || data.message || 'Registration failed.');
        }

        alert('Account created successfully! Please sign in.');
        
        // Switch back to Login view
        registerSection.classList.add('hidden');
        loginSection.classList.remove('hidden');
        registerForm.reset();
      } catch (err) {
        alert(err.message);
      } finally {
        btn.innerText = 'Create Account';
        btn.disabled = false;
      }
    });
  }

  // Handle User Login
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      const identifierInput = document.getElementById('loginUsername') || document.getElementById('loginEmail');
      const passwordInput = document.getElementById('loginPassword');
      const btn = document.getElementById('loginBtn');

      const email = identifierInput ? identifierInput.value.trim() : '';
      const password = passwordInput ? passwordInput.value : '';

      if (!email || !password) {
        alert('Please fill in all login fields.');
        return;
      }

      btn.innerText = 'Signing In...';
      btn.disabled = true;

      try {
        const response = await fetch('/api/v1/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.error || data.message || 'Invalid email or password.');
        }

        // Store JWT token if returned by backend
        if (data.token || data.access_token) {
          localStorage.setItem('token', data.token || data.access_token);
        }

        // Redirect to main explore dashboard
        window.location.href = '/';
      } catch (err) {
        alert(err.message);
      } finally {
        btn.innerText = 'Sign In';
        btn.disabled = false;
      }
    });
  }
});