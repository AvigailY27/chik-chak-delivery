import React from 'react';

const DeliveryList = ({ deliveries, completedDeliveries }) => {
  return (
    <div>
      <h2>רשימת משלוחים</h2>
      <ul>
        {deliveries.map((delivery, index) => (
          <li key={index} style={{ textDecoration: completedDeliveries.includes(delivery.destination) ? 'line-through' : 'none' }}>
            <strong>{delivery.destination}</strong> - זמן סיום: {delivery.end}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default DeliveryList;