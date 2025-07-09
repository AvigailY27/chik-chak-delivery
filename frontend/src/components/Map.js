import React from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';

const Map = ({ route, currentLocation }) => {
  return (
    <MapContainer center={currentLocation} zoom={13} style={{ height: '100vh', width: '100%' }}>
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution="&copy; OpenStreetMap contributors"
      />
      {route.map((point, index) => (
        <Marker key={index} position={point}>
          <Popup>יעד {index + 1}</Popup>
        </Marker>
      ))}
    </MapContainer>
  );
};

export default Map;