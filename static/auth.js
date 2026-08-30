document.addEventListener('DOMContentLoaded', () => {
  const loginSection = document.getElementById('loginSection');
  const registerSection = document.getElementById('registerSection');
  const goToRegister = document.getElementById('goToRegister');
  const goToLogin = document.getElementById('goToLogin');

  const loginForm = document.getElementById('loginForm');
  const registerForm = document.getElementById('registerForm');

  // Reusable Toast Notification Generator
  function showToast(message, type = 'success') {
    let container = document.querySelector('.toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const icon = type === 'success' ? '✓' : '!';
    toast.innerHTML = `
      <span class="toast-icon">${icon}</span>
      <span class="toast-msg">${message}</span>
    `;

    container.appendChild(toast);

    // Auto dismiss after 3.5 seconds
    setTimeout(() => {
      toast.classList.add('toast-hide');
      setTimeout(() => toast.remove(), 260);
    }, 3500);
  }

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
        showToast('Please provide both an email and password.', 'error');
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

        showToast('Account created successfully! Please sign in.', 'success');
        
        // Smooth switch back to Login view
        setTimeout(() => {
          registerSection.classList.add('hidden');
          loginSection.classList.remove('hidden');
          registerForm.reset();
        }, 1200);
      } catch (err) {
        showToast(err.message, 'error');
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
        showToast('Please enter your credentials.', 'error');
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

        if (data.token || data.access_token) {
          localStorage.setItem('token', data.token || data.access_token);
        }

        showToast('Signed in successfully! Redirecting...', 'success');

        setTimeout(() => {
          window.location.href = '/dashboard';
        }, 900);
      } catch (err) {
        showToast(err.message, 'error');
      } finally {
        btn.innerText = 'Sign In';
        btn.disabled = false;
      }
    });
  }
});