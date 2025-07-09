import React, { useState } from "react";

const CourierForm = ({ onAddCourier }) => {
    const [id, setid] = useState("");
    const [start, setStart] = useState("");
    const [end, setEnd] = useState("");
    const [startLocation, setStartLocation] = useState("");

    const handleSubmit = (e) => {
        e.preventDefault();
        onAddCourier({ id, start, end, startLocation });
        setid(""); setStart(""); setEnd(""); setStartLocation("");
    };

    return (
        <form onSubmit={handleSubmit}>
            <h3>הוסף שליח</h3>
            <input placeholder="שם שליח" value={id} onChange={e => setName(e.target.value)} required />
            <input type="time" value={start} onChange={e => setStart(e.target.value)} required />
            <input type="time" value={end} onChange={e => setEnd(e.target.value)} required />
            <input placeholder="מיקום התחלתי (מחסן)" value={startLocation} onChange={e => setStartLocation(e.target.value)} required />
            <button type="submit">הוסף שליח</button>
        </form>
    );
};

export default CourierForm;