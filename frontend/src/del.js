import React, { useState } from "react";

const DeliveryForm = () => {
    const [tableData, setTableData] = useState([
        { clientName: "", address: "", deliveryDate: "", status: "" },
    ]);
    const [file, setFile] = useState(null);
    const [message, setMessage] = useState("");

    const handleFileUpload = (e) => {
        setFile(e.target.files[0]);
    };

    const addRow = () => {
        setTableData([
            ...tableData,
            { clientName: "", address: "", deliveryDate: "", status: "" },
        ]);
    };

    const removeRow = (index) => {
        const newTableData = tableData.filter((_, i) => i !== index);
        setTableData(newTableData);
    };

    const handleInputChange = (index, e) => {
        const newTableData = [...tableData];
        newTableData[index][e.target.name] = e.target.value;
        setTableData(newTableData);
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (file) {
            // אם יש קובץ, להעלות אותו
            alert("הקובץ יועלה ויתוקן בשרת.");
            // להוסיף כאן קוד העלאת הקובץ לשרת
        } else {
            // אם אין קובץ, שולחים את הנתונים מהטבלה
            const csvContent =
                "שם הלקוח,כתובת,תאריך משלוח,סטטוס\n" +
                tableData
                    .map((row) => `${row.clientName},${row.address},${row.deliveryDate},${row.status}`)
                    .join("\n");

            const blob = new Blob([csvContent], { type: "text/csv" });
            const link = document.createElement("a");
            link.href = URL.createObjectURL(blob);
            link.download = "shipping_data.csv";
            link.click();

            // מציגים הודעה
            setMessage("הנתונים נשמרו כקובץ CSV!");
        }
    };

    return (
        <div>
            <h1>טופס שליחים</h1>
            <form onSubmit={handleSubmit}>
                <h3>העלה קובץ משלוחים</h3>
                <input type="file" id="fileUpload" onChange={handleFileUpload} />
                <br />
                <br />

                <h3>או מלא את פרטי המשלוחים בטבלה</h3>
                <table id="deliveryTable">
                    <thead>
                        <tr>
                            <th>שם הלקוח</th>
                            <th>כתובת</th>
                            <th>תאריך משלוח</th>
                            <th>סטטוס</th>
                        </tr>
                    </thead>
                    <tbody>
                        {tableData.map((row, index) => (
                            <tr key={index}>
                                <td>
                                    <input
                                        type="text"
                                        name="clientName"
                                        value={row.clientName}
                                        onChange={(e) => handleInputChange(index, e)}
                                    />
                                </td>
                                <td>
                                    <input
                                        type="text"
                                        name="address"
                                        value={row.address}
                                        onChange={(e) => handleInputChange(index, e)}
                                    />
                                </td>
                                <td>
                                    <input
                                        type="date"
                                        name="deliveryDate"
                                        value={row.deliveryDate}
                                        onChange={(e) => handleInputChange(index, e)}
                                    />
                                </td>
                                <td>
                                    <input
                                        type="text"
                                        name="status"
                                        value={row.status}
                                        onChange={(e) => handleInputChange(index, e)}
                                    />
                                </td>
                                <td>
                                    <button type="button" onClick={() => removeRow(index)}>
                                        הסר שורה
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>

                <button type="button" onClick={addRow}>
                    הוסף שורה
                </button>
                <br />
                <button type="submit">שלח</button>
            </form>

            {message && <div>{message}</div>}
        </div>
    );
};

export default DeliveryForm;
// Compare this snippet from delivery-form/delivery-form/src/index.css: