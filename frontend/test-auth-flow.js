// Test script to verify authentication flow
async function testAuthFlow() {
  console.log('Starting authentication flow test...');
  
  // Clear any existing tokens
  localStorage.removeItem('access_token');
  localStorage.removeItem('user');
  
  // Test login
  try {
    console.log('Attempting to log in...');
    
    // First, let's check if the user exists
    console.log('\n1. Checking if test user exists...');
    const testUser = {
      email: 'test@example.com',
      password: 'testpassword123',
      full_name: 'Test User'
    };
    
    // Try to register the test user first
    console.log('\n2. Registering test user...');
    const registerResponse = await fetch('http://127.0.0.1:8001/api/auth/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        email: testUser.email,
        password: testUser.password,
        full_name: testUser.full_name
      })
    });
    
    const registerData = await registerResponse.json().catch(() => ({}));
    console.log('Register response:', {
      status: registerResponse.status,
      data: registerData
    });
    
    // If registration fails with 400, the user might already exist - that's okay
    if (registerResponse.status !== 200 && registerResponse.status !== 400) {
      throw new Error(`Registration failed: ${registerData.detail || 'Unknown error'}`);
    }
    
    // Now try to log in
    console.log('\n3. Attempting to log in...');
    const loginForm = new URLSearchParams();
    loginForm.append('username', testUser.email);
    loginForm.append('password', testUser.password);
    
    console.log('Login form data:', Object.fromEntries(loginForm.entries()));
    
    const loginResponse = await fetch('http://127.0.0.1:8001/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
      },
      body: loginForm.toString()
    });
    
    const loginData = await loginResponse.json().catch(err => {
      console.error('Failed to parse login response as JSON:', err);
      return { detail: 'Invalid JSON response' };
    });
    
    console.log('Login response:', {
      status: loginResponse.status,
      statusText: loginResponse.statusText,
      headers: Object.fromEntries(loginResponse.headers.entries()),
      data: loginData
    });
    
    if (!loginResponse.ok) {
      throw new Error(`Login failed: ${loginData.detail || 'Unknown error'}`);
    }
    
    // Test protected endpoint
    console.log('\nTesting protected endpoint...');
    const testResponse = await fetch('http://127.0.0.1:8001/api/v1/test-cases', {
      headers: {
        'Authorization': `Bearer ${loginData.access_token}`,
        'Accept': 'application/json'
      }
    });
    
    const testData = await testResponse.json().catch(() => ({}));
    console.log('Test endpoint response:', {
      status: testResponse.status,
      data: testData
    });
    
    if (!testResponse.ok) {
      throw new Error(`Test endpoint failed: ${testData.detail || 'Unknown error'}`);
    }
    
    console.log('\n✅ Authentication flow test completed successfully!');
    return { success: true };
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    console.error('Error details:', error);
    return { success: false, error: error.message };
  }
}

// Run the test
console.log('Copy and paste the following into the browser console to run the test:');
console.log('(' + testAuthFlow.toString() + ')();');
console.log('\nOr click the button below to run the test:');

// Create a button to run the test
const button = document.createElement('button');
button.textContent = 'Run Auth Flow Test';
button.style.padding = '10px 20px';
button.style.margin = '10px';
button.style.fontSize = '16px';
button.style.cursor = 'pointer';
button.onclick = testAuthFlow;
document.body.appendChild(button);
