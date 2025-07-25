// setupTests.ts
// Runs before every Vitest test file
import '@testing-library/jest-dom';

// polyfill matchMedia for jsdom environment used by Vitest
// Source: https://github.com/jsdom/jsdom/issues/3002
if (typeof window !== 'undefined' && !window.matchMedia) {
  window.matchMedia = (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {}, // deprecated
    removeListener: () => {}, // deprecated
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  } as any);
}
