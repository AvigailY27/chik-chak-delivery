import React, { useState } from "react";
import DeliveryForm from "./DeliveryForm";
import CourierForm from "./CourierForm";
import "./style.css"; // Assuming you have some styles for the panel
const ManagerPanel = () => {
    const [couriers, setCouriers] = useState([]);
    const [deliveries, setDeliveries] = useState([]);

    const addCourier = (courier) => setCouriers([...couriers, courier]);
    const addDelivery = (delivery) => setDeliveries([...deliveries, delivery]);

    return (
        <div>
            <h2>פאנל מנהל</h2>
            <DeliveryForm onAdd={addDelivery} />
            <CourierForm onAddCourier={addCourier} />
            <h3>רשימת שליחים:</h3>
            <ul>
                {couriers.map((c, i) => <li key={i}>{c.name} ({c.start}-{c.end})</li>)}
            </ul>
        </div>
    );
};

export default ManagerPanel;