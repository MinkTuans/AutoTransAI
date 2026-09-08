import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('[ErrorBoundary caught error]:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          minHeight: '100vh',
          background: '#0f172a',
          color: '#fff',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '20px',
          fontFamily: 'sans-serif'
        }}>
          <div style={{
            background: '#1e293b',
            border: '1px solid #ef4444',
            borderRadius: '12px',
            padding: '32px',
            maxWidth: '600px',
            width: '100%',
            textAlign: 'center'
          }}>
            <h2 style={{ color: '#fca5a5', marginTop: 0 }}>❌ Ứng Dụng Gặp Lỗi Giao Diện (UI Runtime Error)</h2>
            <p style={{ color: '#94a3b8', fontSize: '14px' }}>
              Xảy ra lỗi không mong muốn trong giao diện React. Vui lòng bấm nút bên dưới để tải lại ứng dụng.
            </p>
            <div style={{
              background: '#450a0a',
              color: '#fecdd3',
              padding: '12px',
              borderRadius: '6px',
              fontFamily: 'monospace',
              fontSize: '12px',
              textAlign: 'left',
              marginBottom: '20px',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-all'
            }}>
              {this.state.error?.toString() || 'Unknown Error'}
            </div>
            <button
              onClick={() => window.location.reload()}
              style={{
                background: '#2563eb',
                color: '#fff',
                border: 'none',
                padding: '10px 20px',
                borderRadius: '8px',
                fontWeight: 'bold',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              🔄 Tải lại trang (Reload App)
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>,
);
