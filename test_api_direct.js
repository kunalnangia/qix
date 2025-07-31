const axios = require('axios');
const API_BASE_URL = 'http://localhost:8001/api/v1';

async function testEndpoint(method, url, data = null, customHeaders = {}) {
  try {
    console.log(`\n=== Testing ${method.toUpperCase()} ${url} ===`);
    
    // Prepare headers
    const headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      ...customHeaders
    };
    
    // Prepare config
    const config = {
      method: method,
      url: `${API_BASE_URL}${url}`,
      headers: headers,
      data: data ? JSON.stringify(data) : null,
      // Enable request/response interception
      transformRequest: [function (data, headers) {
        console.log('\n--- Request Details ---');
        console.log('Method:', method.toUpperCase());
        console.log('URL:', `${API_BASE_URL}${url}`);
        console.log('Headers:', JSON.stringify(headers, null, 2));
        if (data) {
          console.log('Request Body:', JSON.stringify(JSON.parse(data), null, 2));
        }
        return data;
      }],
      transformResponse: [function (data) {
        try {
          const parsedData = JSON.parse(data);
          console.log('\n--- Response Body ---');
          console.log(JSON.stringify(parsedData, null, 2));
          return parsedData;
        } catch (e) {
          console.log('\n--- Response Body (raw) ---');
          console.log(data);
          return data;
        }
      }]
    };
    
    // Log the request details
    console.log('\n--- Sending Request ---');
    console.log(`${method.toUpperCase()} ${config.url}`);
    console.log('Headers:', JSON.stringify(config.headers, null, 2));
    if (data) {
      console.log('Body:', JSON.stringify(JSON.parse(JSON.stringify(data)), null, 2));
    }
    
    const response = await axios(config);
    
    console.log('✅ Success! Status:', response.status);
    console.log('Response headers:', JSON.stringify(response.headers, null, 2));
    console.log('Response data:', JSON.stringify(response.data, null, 2));
    
    return response.data;
  } catch (error) {
    console.error('❌ Error:', error.message);
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response headers:', JSON.stringify(error.response.headers, null, 2));
      console.error('Response data:', JSON.stringify(error.response.data, null, 2));
    } else if (error.request) {
      console.error('No response received');
      console.error('Request:', error.request);
    } else {
      console.error('Error setting up the request:', error.message);
    }
    throw error;
  }
}

async function runTests() {
  try {
    console.log('Testing API endpoints directly...');
    
    // Test root endpoint
    await testEndpoint('get', '/');
    
    // Test health check endpoint if available
    await testEndpoint('get', '/health').catch(() => {
      console.log('Health check endpoint not available, continuing with other tests...');
    });
    
    // Test registration
    const userData = {
      email: 'test@example.com',
      password: 'testpassword',
      full_name: 'Test User'
    };
    
    await testEndpoint('post', '/auth/register', userData).catch(() => {
      console.log('User may already be registered, continuing with login...');
    });
    
    // Test login
    const loginData = {
      username: 'test@example.com',
      password: 'testpassword'
    };
    
    const loginResponse = await testEndpoint('post', '/auth/login', loginData);
    const authToken = loginResponse.access_token;
    
    if (!authToken) {
      throw new Error('No authentication token received');
    }
    
    console.log('✅ Successfully authenticated. Token received.');
    
    // Test creating a project
    const projectData = {
      name: 'Test Project',
      description: 'Test project description',
      is_active: true
    };
    
    const project = await testEndpoint('post', '/projects', projectData, {
      'Authorization': `Bearer ${authToken}`
    });
    
    console.log('✅ Project created with ID:', project.id);
    
  } catch (error) {
    console.error('\n❌ Test failed with error:', error.message);
    process.exit(1);
  }
}

runTests();
