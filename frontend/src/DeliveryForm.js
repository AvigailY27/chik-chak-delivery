import React, { useState } from "react";
import DeliveryTable from "./DeliveryTable"; // רכיב הטבלה
import './style.css';

const DeliveryForm = () => {
    const [tableData, setTableData] = useState([
        { clientName: "", address: "", deliveryDate: "", startTime: "", lastTime: "", status: "" },
    ]);
    const [file, setFile] = useState(null);
    const [message, setMessage] = useState("");

    // טיפול בהעלאת קובץ
    const handleFileUpload = (e) => {
        const uploadedFile = e.target.files[0];

        if (!uploadedFile || (!uploadedFile.name.endsWith(".csv") && !uploadedFile.name.endsWith(".json"))) {
            alert("אנא העלה קובץ מסוג CSV או JSON בלבד.");
            return;
        }
        setFile(uploadedFile);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
    
        // אם יש קובץ, נשלח אותו לשרת
        if (file) {
            const formData = new FormData();
            formData.append("file", file);
    
            try {
                const response = await fetch("http://localhost:5000/upload", {
                    method: "POST",
                    body: formData,
                });
    
                if (!response.ok) {
                    throw new Error("שגיאה בתגובה מהשרת.");
                }
    
                const result = await response.json();
                setMessage(result.message);
    
                // איפוס הטופס לאחר שליחה מוצלחת
                setFile(null);
                setTableData([{ destination: "", timeMax: "", startTime: "", endTime: "" }]);
            } catch (error) {
                console.error("שגיאה בשליחת הקובץ:", error);
                setMessage("שגיאה בשליחת הקובץ.");
            }
            return;
        }
    
        // סינון שורות ריקות
        const filteredTableData = tableData.filter(row =>
            row.destination.trim() &&
            row.timeMax.trim() &&
            row.startTime.trim() &&
            row.endTime.trim()
        );
    
        if (filteredTableData.length === 0) {
            alert("אין נתונים לשליחה.");
            return;
        }
    
        // יצירת קובץ CSV
        const csvContent =
        "\uFEFFכתובת,זמן אספקה מקסימלי,שעת התחלה,שעת סיום\n" +
        filteredTableData
            .map((row) => `${row.destination},${row.timeMax},${row.startTime},${row.endTime}`)
            .join("\n");
        const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
        const formData = new FormData();
        formData.append("file", new File([blob], "deliverybest.csv"));
    
        try {
            const response = await fetch("http://localhost:5000/upload", {
                method: "POST",
                body: formData,
            });
    
            if (!response.ok) {
                throw new Error("שגיאה בתגובה מהשרת.");
            }
    
            const result = await response.json();
            setMessage(result.message);
    
            // איפוס הטופס לאחר שליחה מוצלחת
            setTableData([{ destination: "", timeMax: "", startTime: "", endTime: "" }]);
        } catch (error) {
            console.error("שגיאה בשליחת הנתונים:", error);
            setMessage("שגיאה בשליחת הנתונים.");
        }
    };
    return (
        <div className="container">
            <h2>📦 טופס פרטי משלוחים</h2>
            <form onSubmit={handleSubmit}>
                <input type="file" accept=".csv,.json" onChange={handleFileUpload} />
                {!file && (
                    <DeliveryTable tableData={tableData} setTableData={setTableData} />
                )}
                <button type="submit">📤 שלח נתונים</button>
            </form>
            {message && <p className="message">{message}</p>}
        </div>
    );
};

export default DeliveryForm;