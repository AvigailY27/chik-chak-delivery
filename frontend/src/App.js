import './App.css';
import React, { useState } from "react";
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import DeliveryForm from './components/DeliveryForm.js';
import Frmmain from './components/frmmain.js';
import Frmdeliveries from './components/frmdeliveries.js';


function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Frmmain />} />
        <Route path="/Administrator" element={<DeliveryForm />} />
        <Route path="/deliver" element={<Frmdeliveries />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
