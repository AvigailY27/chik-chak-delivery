import React from "react";

const DeliveryTable = ({ tableData, setTableData }) => {
    const addRow = () => {
        setTableData([...tableData, { destination: "", timeMax: "", startTime: "", endTime: "" }]);
    };

    const removeRow = (index) => {
        setTableData(tableData.filter((_, i) => i !== index));
    };

    const handleInputChange = (index, e) => {
        const { name, value } = e.target;
        const newTableData = [...tableData];
        newTableData[index][name] = value;

        // בדיקה אם זמן אספקה מקסימלי הוא מספר חיובי
        if (name === "timeMax") {
            const timeMax = parseFloat(value);
            if (isNaN(timeMax) || timeMax <= 0) {
                alert("זמן אספקה מקסימלי חייב להיות מספר חיובי.");
                return;
            }
        }

        // בדיקה אם שעת התחלה קטנה משעת סיום
        if (name === "startTime" || name === "endTime") {
            const startTime = newTableData[index].startTime;
            const endTime = newTableData[index].endTime;

            if (startTime && endTime && startTime >= endTime) {
                alert("שעת התחלה חייבת להיות קטנה משעת סיום.");
                return;
            }
        }

        setTableData(newTableData);
    };

    return (
        <table>
            <thead>
                <tr>
                    <th>כתובת יעד</th>
                    <th>זמן אספקה מקסימלי (שעות)</th>
                    <th>שעת התחלה</th>
                    <th>שעת סיום</th>
                    <th>🗑️</th>
                </tr>
            </thead>
            <tbody>
                {tableData.map((row, index) => (
                    <tr key={index}>
                        <td><input type="text" name="destination" value={row.destination} onChange={(e) => handleInputChange(index, e)} /></td>
                        <td><input type="number" name="timeMax" value={row.timeMax} onChange={(e) => handleInputChange(index, e)} /></td>
                        <td><input type="time" name="startTime" value={row.startTime} onChange={(e) => handleInputChange(index, e)} /></td>
                        <td><input type="time" name="endTime" value={row.endTime} onChange={(e) => handleInputChange(index, e)} /></td>
                        <td><button type="button" onClick={() => removeRow(index)}>x</button></td>
                    </tr>
                ))}
            </tbody>
            <tfoot>
                <tr>
                    <td colSpan="5">
                        <button type="button" onClick={addRow}>➕ הוסף שורה</button>
                    </td>
                </tr>
            </tfoot>
        </table>
    );
};

export default DeliveryTable;