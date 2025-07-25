/* Test utility wrappers and helpers */
import { ReactElement } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '@/hooks/useAuth';

// Helper to create a wrapper with AuthProvider and QueryClientProvider
// AdditionalProvider is an optional extra provider that can be passed in
const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: {
      retry: false, // Don't retry failed queries in tests
    },
  },
});

type ProviderProps = {
  children: React.ReactNode;
};

export const createWrapper = (AdditionalProvider?: React.ComponentType<ProviderProps>) => {
  const queryClient = createTestQueryClient();
  
  return ({ children }: { children: ReactElement }) => (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        {AdditionalProvider ? <AdditionalProvider>{children}</AdditionalProvider> : children}
      </AuthProvider>
    </QueryClientProvider>
  );
};
