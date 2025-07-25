import { render } from '@testing-library/react';
import App from './App';

// Simple smoke test: component renders without throwing
it('renders App without crashing', () => {
  const { container } = render(<App />);
  expect(container).toBeTruthy();
});
