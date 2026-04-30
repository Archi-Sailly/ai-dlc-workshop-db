import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import './index.css';

// Mock 인터셉터 (개발용 — 백엔드 없이 테스트할 때만 활성화)
// import { setupMockInterceptor } from './mocks/handlers';
// setupMockInterceptor();

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
);
