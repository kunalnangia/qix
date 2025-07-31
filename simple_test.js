const http = require('http');

const API_HOST = 'localhost';
const API_PORT = 8001;
const API_PATH = '/api/v1/';

function testEndpoint(method, path, headers = {}, body = null) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: API_HOST,
      port: API_PORT,
      path: API_PATH + path.replace(/^\/+/, ''),
      method: method,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...headers
      }
    };

    console.log(`\n=== Testing ${method} ${options.path} ===`);
    console.log('Request Headers:', JSON.stringify(options.headers, null, 2));
    
    const req = http.request(options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        console.log('Status Code:', res.statusCode);
        console.log('Response Headers:', JSON.stringify(res.headers, null, 2));
        
        try {
          const jsonData = data ? JSON.parse(data) : {};
          console.log('Response Body:', JSON.stringify(jsonData, null, 2));
          resolve({ statusCode: res.statusCode, headers: res.headers, body: jsonData });
        } catch (e) {
          console.log('Response Body (raw):', data);
          resolve({ statusCode: res.statusCode, headers: res.headers, body: data });
        }
      });
    });

    req.on('error', (error) => {
      console.error('Request Error:', error);
      reject(error);
    });

    if (body) {
      console.log('Request Body:', JSON.stringify(body, null, 2));
      req.write(JSON.stringify(body));
    }
    
    req.end();
  });
}

async function runTests() {
  try {
    console.log('Starting simple API tests...');
    
    // Test 1: GET root endpoint
    await testEndpoint('GET', '/');
    
    // Test 2: Test registration
    await testEndpoint('POST', '/auth/register', {}, {
      email: 'test@example.com',
      password: 'testpassword',
      full_name: 'Test User'
    }).catch(err => {
      console.log('Registration test failed (might be expected if user exists)');
    });
    
    // Test 3: Test login
    const loginResponse = await testEndpoint('POST', '/auth/login', {}, {
      username: 'test@example.com',
      password: 'testpassword'
    });
    
    if (loginResponse.body && loginResponse.body.access_token) {
      const token = loginResponse.body.access_token;
      console.log('✅ Successfully authenticated');
      
      // Test 4: Create a project
      await testEndpoint('POST', '/projects', {
        'Authorization': `Bearer ${token}`
      }, {
        name: 'Test Project',
        description: 'Test project description',
        is_active: true
      });
    }
    
  } catch (error) {
    console.error('Test failed with error:', error);
  }
}

runTests();
