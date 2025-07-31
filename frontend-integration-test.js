const axios = require('axios');
const API_BASE_URL = 'http://localhost:8001/api/v1';

// Test user credentials
const testUser = {
  email: 'test@example.com',
  password: 'testpassword',
  full_name: 'Test User'
};

let authToken = '';

// Helper function to make authenticated requests
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
api.interceptors.request.use((config) => {
  if (authToken) {
    config.headers.Authorization = `Bearer ${authToken}`;
  }
  return config;
});

// Test cases
const runTests = async () => {
  try {
    console.log('Starting frontend-backend integration tests...\n');
    console.log(`Using API base URL: ${API_BASE_URL}\n`);

    // 1. Test registration
    console.log('1. Testing user registration...');
    try {
      const registerData = {
        email: testUser.email,
        password: testUser.password,
        full_name: testUser.full_name
      };
      
      console.log('Sending registration request with data:', JSON.stringify(registerData, null, 2));
      
      const registerResponse = await api.post('/auth/register', registerData, {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });
      
      console.log('✅ Registration successful. Response status:', registerResponse.status);
      console.log('Response data:', JSON.stringify(registerResponse.data, null, 2));
      
    } catch (error) {
      if (error.response) {
        console.error('Registration error response:', {
          status: error.response.status,
          statusText: error.response.statusText,
          headers: error.response.headers,
          data: error.response.data
        });
      } else if (error.request) {
        console.error('No response received for registration request:', error.request);
      } else {
        console.error('Error setting up registration request:', error.message);
      }
      
      if (error.response && error.response.status === 400 && 
          error.response.data.detail === 'Email already registered') {
        console.log('ℹ️ User already exists, continuing with login...');
      } else {
        console.error('❌ Registration test failed');
        throw error;
      }
    }

    // 2. Test login
    console.log('\n2. Testing user login...');
    const loginResponse = await api.post('/auth/login', {
      username: testUser.email,
      password: testUser.password
    });
    
    authToken = loginResponse.data.access_token;
    console.log('✅ Login successful. Token received.');

    // 3. Test creating a project
    console.log('\n3. Testing project creation...');
    const projectData = {
      name: 'Test Project',
      description: 'This is a test project',
      is_active: true
    };
    
    const projectResponse = await api.post('/projects', projectData);
    const projectId = projectResponse.data.id;
    console.log('✅ Project created:', projectResponse.data);

    // 4. Test getting projects
    console.log('\n4. Testing get all projects...');
    const projectsResponse = await api.get('/projects');
    console.log(`✅ Retrieved ${projectsResponse.data.length} projects`);

    // 5. Test getting a single project
    console.log('\n5. Testing get single project...');
    const singleProjectResponse = await api.get(`/projects/${projectId}`);
    console.log('✅ Retrieved project:', singleProjectResponse.data.name);

    // 6. Test creating a test case
    console.log('\n6. Testing test case creation...');
    const testCaseData = {
      title: 'Sample Test Case',
      description: 'This is a test case',
      steps: '1. Step 1\n2. Step 2\n3. Step 3',
      expected_result: 'Test passes',
      project_id: projectId,
      priority: 'high',
      status: 'not_run'
    };
    
    const testCaseResponse = await api.post('/test-cases', testCaseData);
    const testCaseId = testCaseResponse.data.id;
    console.log('✅ Test case created:', testCaseResponse.data.title);

    // 7. Test getting test cases for project
    console.log('\n7. Testing get test cases for project...');
    const testCasesResponse = await api.get(`/test-cases?project_id=${projectId}`);
    console.log(`✅ Retrieved ${testCasesResponse.data.length} test cases for project`);

    // 8. Test updating a test case
    console.log('\n8. Testing test case update...');
    const updateData = {
      title: 'Updated Test Case',
      status: 'passed'
    };
    
    const updateResponse = await api.put(`/test-cases/${testCaseId}`, updateData);
    console.log('✅ Test case updated:', updateResponse.data.title, 'Status:', updateResponse.data.status);

    // 9. Test deleting the test case
    console.log('\n9. Testing test case deletion...');
    await api.delete(`/test-cases/${testCaseId}`);
    console.log('✅ Test case deleted');

    // 10. Test deleting the project
    console.log('\n10. Testing project deletion...');
    await api.delete(`/projects/${projectId}`);
    console.log('✅ Project deleted');

    console.log('\n✅ All tests completed successfully!');
    
  } catch (error) {
    console.error('\n❌ Test failed:');
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error('Response data:', error.response.data);
      console.error('Status code:', error.response.status);
      console.error('Headers:', error.response.headers);
    } else if (error.request) {
      // The request was made but no response was received
      console.error('No response received:', error.request);
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error('Error:', error.message);
    }
    process.exit(1);
  }
};

// Run the tests
runTests();
