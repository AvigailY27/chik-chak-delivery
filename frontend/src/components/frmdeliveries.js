import React, { useState, useEffect } from 'react';
import 'leaflet/dist/leaflet.css';

const Frmdeliveries = () => {
  const [phone, setPhone] = useState('');
  const [cluster, setCluster] = useState('');
  const [deliveries, setDeliveries] = useState([]);
  const [deliveriesUse, setDeliveriesUse] = useState([]);
  const [notdeliveries, setnotDeliveries] = useState([]);
  const [error, setError] = useState('');
  const [courierInfo, setCourierInfo] = useState(null);
  const [statusMessage, setStatusMessage] = useState('');
  const [mapPoints, setMapPoints] = useState([]);
  const [showMap, setShowMap] = useState(false);
  const [shouldUpdateRoute, setShouldUpdateRoute] = useState(false);

  useEffect(() => {
    if (shouldUpdateRoute && deliveriesUse.length > 0) {
      requestRoute(deliveriesUse);
      console.log('Updating route with deliveriesUse:', deliveriesUse);
      setShouldUpdateRoute(false); 
    }
  }, [deliveriesUse, shouldUpdateRoute]);

  const fetchDeliveries = async () => {
    try {
      setStatusMessage('Looking for your deliveries today...');
      const response = await fetch(`http://localhost:5000/get_deliveries_by_phone/${phone}`);
      const data = await response.json();

      if (response.ok) {
        setCluster(data.cluster || '');
        setDeliveries(data.deliveries);
        setnotDeliveries(data.notdeliveries);
        setCourierInfo(data.courier);
        console.log('notdeliveries', data.notdeliveries);
        console.log('deliveries', data.deliveries);
        setError('');
        setStatusMessage('Deliveries fetched successfully!');
      } else {
        setError(data.message || 'Error fetching data');
        setDeliveries([]);
        setnotDeliveries(data.notdeliveries || []);
        setCluster('');
        setStatusMessage('No deliveries found for today. Please try again later.');
      }
    } catch (err) {
      console.error('Error:', err);
      setError('Server error');
      setDeliveries([]);
      setnotDeliveries([]);
      setCluster('');
      setStatusMessage('Error fetching deliveries. Please try again later.');
    }
  };

  // פונקציה שמחשבת מסלול לפי משלוחים (מקבלת רשימת משלוחים כפרמטר)
  const requestRoute = async (deliveriesParam = deliveries) => {
    try {
      const response = await fetch('http://localhost:5000/get_route', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          courierInfo: courierInfo,
          deliveries: deliveriesParam,
          start_location: courierInfo?.current_location
        })
      });

      const data = await response.json();
      if (response.ok) {
        setDeliveries(data.route || []);
        setCourierInfo({ ...courierInfo, current_location: data.current_location });
        alert('Route received successfully');
        console.log(data.route);
        generateAndShowMap();
      } else {
        setError(data.message || 'Error getting route');
      }
    } catch (err) {
      console.error('Error:', err);
      setError('Server error');
    }
  };

  const generateAndShowMap = async () => {
    await fetch('http://localhost:5000/generate_map', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        deliveries: deliveries,
        start_address: courierInfo?.current_location
      })
    });
    setShowMap(true);
    refreshMap();
  };
  function refreshMap() {
    setShowMap(false);
    setTimeout(() => {
      setShowMap(true);
    }, 50);  // השהייה קצרה לפני הצגת ה-iframe מחדש
  }
  // בעת הגעה ליעד – הסרת היעד הראשון ועדכון מסלול
  const handleArrivalAtDestination = () => {
    if (deliveries.length > 0) {
      const remainingDeliveries = deliveries.slice(1);
      console.log('Remaining deliveries:', remainingDeliveries);
      setDeliveriesUse(remainingDeliveries);  // נעדכן רק את deliveriesUse
      setShouldUpdateRoute(true);             // יפעיל useEffect
    }
  };

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', overflow: 'hidden', fontFamily: 'Arial, sans-serif' }}>
      {/* פאנל של השליח */}
      <div style={{
        width: '350px',
        backgroundColor: '#e8f5e9',
        padding: '30px',
        boxShadow: '2px 0 10px rgba(0,0,0,0.1)',
        overflowY: 'auto'
      }}>
        <h2 style={{ color: '#2e7d32', textAlign: 'center' }}>Hello Courier</h2>

        {!courierInfo && (
          <>
            <input
              type="text"
              placeholder="Enter phone number"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              style={{
                width: '100%',
                padding: '10px',
                margin: '10px 0',
                borderRadius: '6px',
                border: '1px solid #ccc'
              }}
            />
            <button
              onClick={fetchDeliveries}
              style={{
                width: '100%',
                padding: '10px',
                backgroundColor: '#4caf50',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer'
              }}
            >
              Login
            </button>
          </>
        )}

        {statusMessage && <p style={{ color: 'blue', marginTop: '15px' }}>{statusMessage}</p>}
        {error && <p style={{ color: 'red', marginTop: '10px' }}>{error}</p>}
        {cluster && deliveries.length > 0 && (
          <div>
            <h4 style={{ color: '#388e3c' }}>Delivery Addresses:</h4>
            <ul>
              {courierInfo?.current_location && (
                <li style={{ color: 'green' }}>
                  current_location: {courierInfo.current_location}
                </li>
              )}

              {deliveries.length > 0 && (
                <>
                  <li style={{ color: 'blue' }}>
                    
                    <strong>next stop :</strong> {deliveries[0].destination}
                    <button
                      onClick={() => requestRoute()}
                      style={{
                        marginLeft: '10px',
                        padding: '5px 10px',
                        backgroundColor: '#2e7d32',
                        color: 'white',
                        border: 'none',
                        borderRadius: '5px',
                        cursor: 'pointer'
                      }}
                    >
                  Get Route optimized
                    </button>
                  </li>
                </>
              )}

              {deliveries.slice(1).map((delivery, index) => (
                <li key={index + 1}>{delivery.destination}</li>
              ))}
            </ul>

          {notdeliveries?.length > 0 && (
            <>
              <h4 style={{ color: 'gray' }}>משלוחים שלא הוכנסו:</h4>
              <ul>
                {notdeliveries.map((notdelivery, index) => (
                  <li key={index}>{notdelivery.destination}</li>
                ))}
              </ul>
            </>
          )}


            <button
              onClick={() => generateAndShowMap()}
              style={{
                marginTop: '20px',
                width: '100%',
                padding: '10px',
                backgroundColor: '#388e3c',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer'
              }}
            >
              Show Route on Map
            </button>
          </div>
        )}

        {cluster && deliveries.length === 0 && (
          <p style={{ color: 'orange', marginTop: '10px' }}>
          </p>
        )}
      </div>

      {/* מפה */}
      {showMap && (
        <div style={{ flex: 1, height: '100%' }}>
          <iframe
            src={`http://localhost:5000/get_map_html?ts=${Date.now()}`}
            width="100%"
            height="100%"
            style={{ border: 'none' }}
            title="Map"
          />
        </div>
      )}
    </div>
  );
};

export default Frmdeliveries;
