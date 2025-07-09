import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Frmmain = () => {
  const [userType, setUserType] = useState(null);
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const navigate = useNavigate();

  const handleLogin = () => {
    if (userType === 'Administrator') {
      if (credentials.username === 'Administrator' && credentials.password === '1020') {
        navigate('/Administrator');
      } else {
        alert("Invalid username or password");
      }
    } else if (userType === 'deliver') {
      navigate('/deliver');
    }
  };

  return (
    <div style={{ textAlign: 'center', marginTop: '50px' }}>
      <h1>Welcome to Chick-Chak Deliveries</h1>
      {!userType && (
        <div>
          <button onClick={() => navigate('Administrator')}>Administrator Login</button>
          <br />
          <button onClick={() => navigate('deliver')}>Courier Login</button>
        </div>
      )}
      {/* {userType === 'Administrator' && (
        <div>
          <h2>Administrator Login</h2>
          <input
            type="text"
            placeholder="Username"
            value={credentials.username}
            onChange={(e) => setCredentials({ ...credentials, username: e.target.value })}
          />
          <input
            type="password"
            placeholder="Password"
            value={credentials.password}
            onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
          />
          <button onClick={handleLogin}>Login</button>
        </div>
      )}
      {userType === 'deliver' && (
        <div>
          <h2>Courier Login</h2>
          <p>נא להזין את מספר הטלפון שלך בכניסה הבאה</p>
          <button onClick={handleLogin}>המשך</button>
        </div>
      )} */}
    </div>
  );
};

export default Frmmain;
