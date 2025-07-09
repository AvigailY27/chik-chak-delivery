import React from "react";

const DeliveryTable = ({ tableData, setTableData }) => {
    const addRow = () => {
        setTableData([...tableData, { destination: "", timeMax: "", start: "", end: "" }]);
    };

    const removeRow = (index) => {
        setTableData(tableData.filter((_, i) => i !== index));
    };

    const handleInputChange = (index, e) => {
        const { name, value } = e.target;
        const newTableData = [...tableData];
        newTableData[index][name] = value;

        // Validate that Max Delivery Time is a positive number
        if (name === "timeMax") {
            const timeMax = parseFloat(value);
            if (isNaN(timeMax) || timeMax <= 0) {
                alert("Max Delivery Time must be a positive number.");
                return;
            }
        }

        // Validate that Start Time is earlier than End Time
        if (name === "start" || name === "end") {
            const start = newTableData[index].start;
            const end = newTableData[index].end;

            if (start && end && start >= end) {
                alert("Start Time must be earlier than End Time.");
                return;
            }
        }

        setTableData(newTableData);
    };

    return (
        <table>
            <thead>
                <tr>
                    <th>Destination Address</th>
                    <th>Max Delivery Time (hours)</th>
                    <th>Start</th>
                    <th>End </th>
                    <th>🗑️</th>
                </tr>
            </thead>
            <tbody>
                {tableData.map((row, index) => (
                    <tr key={index}>
                        <td><input type="text" name="destination" value={row.destination} onChange={(e) => handleInputChange(index, e)} /></td>
                        <td><input type="number" name="timeMax" value={row.timeMax} onChange={(e) => handleInputChange(index, e)} /></td>
                        <td><input type="time" name="start" value={row.start} onChange={(e) => handleInputChange(index, e)} /></td>
                        <td><input type="time" name="end" value={row.end} onChange={(e) => handleInputChange(index, e)} /></td>
                        <td><button type="button" onClick={() => removeRow(index)}>x</button></td>
                    </tr>
                ))}
            </tbody>
            <tfoot>
                <tr>
                    <td colSpan="5">
                        <button type="button" onClick={addRow}>➕ Add Row</button>
                    </td>
                </tr>
            </tfoot>
        </table>
    );
};

export default DeliveryTable;