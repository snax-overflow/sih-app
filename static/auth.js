document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const loginSection = document.getElementById('loginSection');
  const registerSection = document.getElementById('registerSection');
  const goToRegister = document.getElementById('goToRegister');
  const goToLogin = document.getElementById('goToLogin');

  const loginForm = document.getElementById('loginForm');
  const registerForm = document.getElementById('registerForm');

  // Toggle to Register
  goToRegister.addEventListener('click', () => {
    loginSection.classList.add('hidden');
    registerSection.classList.remove('hidden');
  });

  // Toggle to Login
  goToLogin.addEventListener('click', () => {
    registerSection.classList.add('hidden');
    loginSection.classList.remove('hidden');
  });

  // Login Submit Handler
  loginForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const username = document.getElementById('loginUsername').value.trim();
    const password = document.getElementById('loginPassword').value;
    const btn = document.getElementById('loginBtn');

    if (!username || !password) {
      alert('Please fill in both fields.');
      return;
    }

    btn.innerText = 'Signing In...';
    btn.disabled = true;

    console.log('Login Payload ready for backend:', { username, password });

    setTimeout(() => {
      btn.innerText = 'Sign In';
      btn.disabled = false;
    }, 1200);
  });

  // Register Submit Handler
  registerForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const username = document.getElementById('regUsername').value.trim();
    const email = document.getElementById('regEmail').value.trim();
    const password = document.getElementById('regPassword').value;
    const btn = document.getElementById('regBtn');

    if (!username || !email || !password) {
      alert('Please fill in all registration fields.');
      return;
    }

    btn.innerText = 'Creating Account...';
    btn.disabled = true;

    console.log('Register Payload ready for backend:', { username, email, password });

    setTimeout(() => {
      btn.innerText = 'Create Account';
      btn.disabled = false;
    }, 1200);
  });
});