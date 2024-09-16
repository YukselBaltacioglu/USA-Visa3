import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, BrowserRouter } from 'react-router-dom';
import Login from './Login';
import EmailManager from './EmailManager';  // Yönlendirmek istediğiniz yeni sayfa

const App = () => {
    return (
      <div>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/emails" element={<EmailManager />} />
          </Routes>
        </BrowserRouter>
      </div>
    );
};

export default App;

