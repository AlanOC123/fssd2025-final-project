import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [status, setStatus] = useState<string>('Checking connection...');

  useEffect(() => {
    fetch('/admin/login/')
      .then((res) => {
        if (res.status === 200) {
          setStatus('Connected to Web Service! (200 OK)');
        } else {
          setStatus(`Connected but got status: ${res.status}`);
        }
      })
      .catch((err) => {
        console.error(err);
        setStatus('Failed to connect to Web Service');
      });
  }, []);

  return (
    <div style={{ padding: '50px', textAlign: 'center' }}>
      <h1>Apex Integration Test</h1>
      <h2>Status: {status}</h2>
      <p>
        If you see the green checkmark, React is successfully talking to Django
        via Docker!
      </p>
    </div>
  );
}

export default App;
