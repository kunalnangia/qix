import { useState, useEffect, createContext, useContext } from 'react';
import { API_ENDPOINTS, getApiUrl } from '@/config/api';

interface AuthContextType {
  user: any | null;
  loading: boolean;
  signUp: (email: string, password: string, fullName?: string) => Promise<{ error: any }>;
  signIn: (email: string, password: string) => Promise<{ error: any }>;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // On mount, check for access_token and user info in localStorage
    const token = localStorage.getItem('access_token');
    const userInfo = localStorage.getItem('user');
    
    if (token) {
      try {
        // If we have a token but no user info, try to parse user data from the token
        if (!userInfo) {
          // In a real app, you might want to verify the token and extract user info
          // For now, we'll just set a minimal user object
          setUser({
            id: 'user-id-from-token',
            email: 'user@example.com',
            full_name: 'User',
            role: 'user'
          });
        } else {
          // We have both token and user info
          setUser(JSON.parse(userInfo));
        }
      } catch (error) {
        console.error('Error parsing user info:', error);
        // Clear invalid data
        localStorage.removeItem('user');
      }
    }
    
    setLoading(false);
  }, []);

  const signUp = async (email: string, password: string, fullName?: string) => {
    setLoading(true);
    try {
      const response = await fetch(getApiUrl(API_ENDPOINTS.AUTH.REGISTER), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, full_name: fullName })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Registration failed');
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));
      setUser(data.user);
      return { error: null };
    } catch (error: any) {
      return { error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const signIn = async (email: string, password: string) => {
    setLoading(true);
    try {
      // Using JSON payload that the backend expects
      const requestBody = {
        email: email,
        password: password
      };
      
      console.log('Sending login request with JSON data:', {
        email: email,
        password: '***' // Don't log actual password
      });
      
      const response = await fetch(getApiUrl(API_ENDPOINTS.AUTH.LOGIN), {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(requestBody)
      });
      
      let data;
      try {
        data = await response.json();
      } catch (jsonError) {
        console.error('Failed to parse JSON response:', jsonError);
        throw new Error('Invalid response from server');
      }
      
      console.log('Login response:', {
        status: response.status,
        statusText: response.statusText,
        headers: Object.fromEntries(response.headers.entries()),
        data
      });
      
      if (!response.ok) {
        // Log the full error response for debugging
        console.error('Login failed with status:', response.status, 'Details:', data);
        
        // Provide more detailed error message
        let errorMessage = 'Login failed';
        if (response.status === 422) {
          errorMessage = 'Validation error: ';
          if (Array.isArray(data.detail)) {
            errorMessage += data.detail.map((err: any) => `${err.loc.join('.')} - ${err.msg}`).join('; ');
          } else if (data.detail) {
            errorMessage += JSON.stringify(data.detail);
          } else {
            errorMessage += 'Invalid request format';
          }
        } else if (data.detail) {
          errorMessage += `: ${data.detail}`;
        }
        
        throw new Error(errorMessage);
      }
      
      // Store the access token
      localStorage.setItem('access_token', data.access_token);
      
      // Create a user object from the token data
      const user = {
        id: data.user_id,
        email: data.email,
        full_name: data.full_name,
        role: data.role
      };
      
      // Store user info in localStorage
      localStorage.setItem('user', JSON.stringify(user));
      setUser(user);
      
      return { error: null };
    } catch (error: any) {
      console.error('Login error:', error);
      return { error: error.message || 'Login failed. Please try again.' };
    } finally {
      setLoading(false);
    }
  };

  const signOut = async () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    setUser(null);
  };

  const value = {
    user,
    loading,
    signUp,
    signIn,
    signOut
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}