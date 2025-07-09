import React from 'react';
import FileUpload from './FileUpload';

const Frmmaneger = () => {
  const handleFileUpload = (file) => {
    console.log('קובץ הועלה:', file);
    // שלח את הקובץ ל-Backend לעיבוד
  };

  return (
    <div style={{ textAlign: 'center', marginTop: '50px' }}>
      <h1>Welcome Administrator</h1>
      <FileUpload onFileUpload={handleFileUpload} />
      <p>Here you can upload a delivery file and view the routes.</p>
    </div>
  );
};

export default Frmmaneger;