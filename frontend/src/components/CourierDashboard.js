import React, { useState, useEffect } from 'react';

const CourierDashboard = ({ courierId }) => {
    const [assignments, setAssignments] = useState(null);
    const [currentLocation, setCurrentLocation] = useState('');

    useEffect(() => {
        const fetchAssignments = async () => {
            const response = await fetch(`http://localhost:5000/get_courier_assignments/${courierId}`);
            const data = await response.json();
            if (response.ok) {
                setAssignments(data);
            } else {
                alert(data.message);
            }
        };
        fetchAssignments();
    }, [courierId]);

    const handleUpdateLocation = async (destination) => {
        const response = await fetch("http://localhost:5000/optimize_route", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                current_location: destination,
                deliveries: assignments.deliveries,
            }),
        });

        const result = await response.json();
        if (response.ok) {
            alert("Route updated successfully!");
            console.log("Optimized route:", result.route);
        } else {
            alert("Error updating route.");
            console.error(result.error);
        }
    };

    return (
        <div>
            <h1>לוח שליח</h1>
            {assignments ? (
                <>
                    <h2>אזור: {assignments.cluster}</h2>
                    <ul>
                        {assignments.deliveries.map((delivery, index) => (
                            <li key={index}>
                                {delivery.destination}
                                <button onClick={() => handleUpdateLocation(delivery.destination)}>
                                    הגעתי ליעד
                                </button>
                            </li>
                        ))}
                    </ul>
                </>
            ) : (
                <p>טוען נתונים...</p>
            )}
        </div>
    );
};

export default CourierDashboard;