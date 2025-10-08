<template>
    <div class="login-container">
      <div class="login-card">
        <h1 class="title">Clinical Trial Tool</h1>
        <p class="subtitle">Welcome back! Please sign in to your account.</p>
  
        <form @submit.prevent="handleLogin">
          <div class="input-group">
            <label for="email">Email Address</label>
            <input type="email" id="email" v-model="email" placeholder="user@domain.com" required />
          </div>
          <div class="input-group">
            <label for="password">Password</label>
            <input type="password" id="password" v-model="password" placeholder="••••••••" required />
          </div>
          <button type="submit" class="btn btn-primary">Sign In</button>
        </form>
  
        <div class="divider">OR</div>
  
        <button class="btn btn-secondary" @click="handleCorporateLogin">
          Sign in with Corporate Account
        </button>
        <button class="btn btn-secondary google" @click="handleGoogleLogin">
          <svg aria-hidden="true" width="18" height="18" viewBox="0 0 18 18"><path d="M16.51 8.1H9v3.4h4.14c-.16 1.18-1.12 2.3-2.64 2.3-1.6 0-2.9-1.3-2.9-2.9s1.3-2.9 2.9-2.9c.74 0 1.43.3 1.93.8l2.6-2.6C14.4 3.2 12 2.4 9.1 2.4c-3.6 0-6.6 2.9-6.6 6.6s3 6.6 6.6 6.6c3.7 0 6.4-2.6 6.4-6.4 0-.4-.05-.8-.1-1.2z" fill="#4285F4"></path></svg>
          Sign in with Google
        </button>
        
        <div class="footer-note">
          Don't have an account? <a href="#">Contact Administrator</a>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  import { useRouter } from 'vue-router';
  
  // 🧩 State: User Credentials
  // Purpose: Reactive references to hold user input
  const email = ref('');
  const password = ref('');
  const router = useRouter();
  
  // 🧩 Function: handleLogin
  // Purpose: Placeholder for authenticating with local credentials
  const handleLogin = () => {
    // In a real app, this would call our auth service:
    // await authStore.login({ email.value, password.value });
    console.log('Attempting login with:', email.value);
    // On success, redirect to the main dashboard
    // router.push({ name: 'Home' }); 
  };
  
  // 🧩 Function: handleCorporateLogin
  // Purpose: Placeholder for company SSO (e.g., SAML/OIDC)
  const handleCorporateLogin = () => {
    console.log('Redirecting to corporate SSO...');
    alert('Corporate login is not yet implemented.');
  };
  
  // 🧩 Function: handleGoogleLogin
  // Purpose: Placeholder for Google OAuth2 flow
  const handleGoogleLogin = () => {
    console.log('Initiating Google OAuth flow...');
    alert('Google login is not yet implemented.');
  };
  </script>
  
  <style scoped>
  /* Using Inter font as recommended */
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap');
  
  .login-container {
    font-family: 'Inter', sans-serif;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    /* Background Gradient from UI Language */
    background: linear-gradient(145deg, #fdfbfb 0%, #ebedee 100%);
  }
  
  .login-card {
    background-color: white;
    padding: 40px;
    border-radius: 12px;
    box-shadow: 0 10px 25px rgba(215, 227, 244, 0.7); /* High-Light Blue as shadow */
    border: 1px solid #E4E4E7; /* Base Grey for border */
    width: 100%;
    max-width: 400px;
    text-align: center;
  }
  
  .title {
    font-size: 24px;
    font-weight: 700;
    margin-bottom: 8px;
    color: #333;
  }
  
  .subtitle {
    font-size: 16px;
    color: #666;
    margin-bottom: 32px;
  }
  
  .input-group {
    text-align: left;
    margin-bottom: 20px;
  }
  
  .input-group label {
    display: block;
    font-size: 14px;
    font-weight: 500;
    margin-bottom: 8px;
    color: #444;
  }
  
  .input-group input {
    width: 100%;
    padding: 12px 16px;
    border: 1px solid #E4E4E7; /* Base Grey */
    border-radius: 8px;
    font-size: 16px;
    transition: border-color 0.2s, box-shadow 0.2s;
  }
  
  .input-group input:focus {
    outline: none;
    border-color: #FF77C9; /* Emphasis Color */
    box-shadow: 0 0 0 3px rgba(255, 119, 201, 0.2);
  }
  
  .btn {
    width: 100%;
    padding: 12px;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
  }
  
  .btn-primary {
    background-color: #F7C8E0; /* Primary Color */
    color: #333;
    margin-bottom: 24px;
  }
  
  .btn-primary:hover {
    background-color: #FF77C9; /* Emphasis Color */
  }
  
  .btn-secondary {
    background-color: #f0f0f1;
    color: #333;
    border: 1px solid #E4E4E7; /* Base Grey */
    margin-bottom: 12px;
  }
  
  .btn-secondary:hover {
    background-color: #E4E4E7;
    border-color: #d1d1d3;
  }
  
  .divider {
    display: flex;
    align-items: center;
    text-align: center;
    color: #aaa;
    margin: 0px 0 24px;
    font-size: 12px;
    text-transform: uppercase;
  }
  .divider::before, .divider::after {
    content: '';
    flex: 1;
    border-bottom: 1px solid #E4E4E7; /* Base Grey */
  }
  .divider:not(:empty)::before {
    margin-right: .5em;
  }
  .divider:not(:empty)::after {
    margin-left: .5em;
  }
  
  .footer-note {
    margin-top: 24px;
    font-size: 14px;
    color: #666;
  }
  
  .footer-note a {
    color: #FF77C9; /* Emphasis Color */
    text-decoration: none;
    font-weight: 500;
  }
  
  .footer-note a:hover {
    text-decoration: underline;
  }
  </style>