import React, { useState } from "react";

const CourierPanel = ({ setShowCourierForm }) => {
    const [couriers, setCouriers] = useState([]);
    const [newCourier, setNewCourier] = useState({
        id: "",
        phone: "",
        startTime: "",
        endTime: "",
        current_location: "מחסן" // ברירת מחדל
    });

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setNewCourier((prev) => ({ ...prev, [name]: value }));
    };

    const addCourier = () => {
        if (
            !newCourier.id.trim() ||
            !newCourier.phone.trim() ||
            !newCourier.startTime.trim() ||
            !newCourier.endTime.trim()
        ) {
            alert("יש למלא את כל השדות החיוניים");
            return;
        }

        setCouriers((prev) => [...prev, newCourier]);

        setNewCourier({
            id: "",
            phone: "",
            startTime: "",
            endTime: "",
            current_location: "מחסן",
        });
    };

    const saveCouriers = async () => {
        console.log("Saving couriers:", couriers); // לבדיקה

        if (couriers.length === 0) {
            alert("אין שליחים לשמירה.");
            return;
        }

        try {
            const response = await fetch("http://localhost:5000/couriers", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ couriers }),
            });

            if (!response.ok) {
                throw new Error("שגיאה בשמירת השליחים");
            }

            alert("שליחים נשמרו בהצלחה!");
            setShowCourierForm(false);
        } catch (error) {
            console.error("שגיאה בשמירת שליחים:", error);
            alert("אירעה שגיאה בשמירת שליחים.");
        }
    };

    return (
        <div className="courier-panel">
            <h2>ניהול שליחים</h2>
            <div>
                <label>
                    ת.ז שליח:
                    <input
                        type="text"
                        name="id"
                        value={newCourier.id}
                        onChange={handleInputChange}
                        required
                    />
                </label>
                <label>
                    טלפון:
                    <input
                        type="text"
                        name="phone"
                        value={newCourier.phone}
                        onChange={handleInputChange}
                        required
                    />
                </label>
                <label>
                    מיקום נוכחי:
                    <input
                        type="text"
                        name="location"
                        value={newCourier.location}
                        onChange={handleInputChange}
                    />
                </label>
                <label>
                    שעת התחלה:
                    <input
                        type="time"
                        name="startTime"
                        value={newCourier.startTime}
                        onChange={handleInputChange}
                        required
                    />
                </label>
                <label>
                    שעת סיום:
                    <input
                        type="time"
                        name="endTime"
                        value={newCourier.endTime}
                        onChange={handleInputChange}
                        required
                    />
                </label>
                <button onClick={addCourier}>הוסף שליח</button>
            </div>

            <div>
                <h3>שליחים שנוספו</h3>
                <ul>
                    {couriers.map((courier, index) => (
                        <li key={index}>
                            {courier.id} - {courier.phone} - {courier.startTime} עד {courier.endTime} - {courier.current_location}
                        </li>
                    ))}
                </ul>
            </div>

            <button onClick={saveCouriers}>שמור שליחים</button>
        </div>
    );
};

export default CourierPanel;
