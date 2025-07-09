import React, { useState, useEffect } from "react";
import DeliveryTable from "./DeliveryTable"; // רכיב הטבלה
import CourierPanel from "./CourierPanel"; // רכיב טופס השליחים
import './style.css';

const DeliveryForm = () => {
  const [tableData, setTableData] = useState([
    { address: "", startTime: "", lastTime: "", status: "" },
  ]);
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");
  const [isProcessing, setIsProcessing] = useState(false); // מצב לעיבוד נתונים
  const [showMessage, setShowMessage] = useState(true); // מצב להצגת ההודעה
  const [showCourierForm, setShowCourierForm] = useState(false); // מצב להצגת טופס השליחים
  const [couriers, setCouriers] = useState([]);
  const [selectedOption, setSelectedOption] = useState(null); // מצב לבחירת פעולה

  useEffect(() => {
    const timer = setTimeout(() => {
      setShowMessage(false); // הסתרת ההודעה
    }, 10000); // 10 שניות

    return () => clearTimeout(timer); // ניקוי הטיימר אם הקומפוננטה מתעדכנת
  }, []);

  const handleFileUpload = (e) => {
    const uploadedFile = e.target.files[0];

    if (
      !uploadedFile ||
      (!uploadedFile.name.endsWith(".csv") && !uploadedFile.name.endsWith(".json"))
    ) {
      alert("Please upload a file in CSV or JSON format only.");
      return;
    }
    setFile(uploadedFile);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsProcessing(true);

    const formData = new FormData();

    if (file) {
      // טיפול במקרה של העלאת קובץ
      formData.append("file", file);
    } else {
      // טיפול במקרה של מילוי טופס
      const filteredTableData = tableData.filter(
        (row) =>
          row &&
          row.destination?.trim() &&
          row.timeMax?.trim() &&
          row.start?.trim() &&
          row.end?.trim()
      );

      if (filteredTableData.length === 0) {
        alert("No valid data to submit.");
        setIsProcessing(false);
        return;
      }

      formData.append("tableData", JSON.stringify(filteredTableData));
    }

    try {
      const response = await fetch("http://localhost:5000/process_data", {
        method: "POST",
        body: formData,
      });

      console.log("File sent to server:", file);

      if (!response.ok) {
        const errorResult = await response.json();

        // בדיקה אם זו שגיאה על חוסר בשליחים
        if (errorResult.couriers_needed !== undefined) {
          alert(`חסרים ${errorResult.couriers_needed} שליחים. יש להוסיף שליחים.`);
          setShowCourierForm(true); // פתיחת טופס השליחים
        } else {
          console.error("Error response from server:", errorResult);
          alert("תקלה בעיבוד הנתונים. נסה שוב.");
        }

        setIsProcessing(false);
        return;
      }

      const result = await response.json();
      console.log("Server response:", result);
      setMessage(result);

      // לאחר קבלת מספר השליחים, שאל את הלקוח אם להשתמש בשליחים קיימים או להוסיף חדשים
      const useExistingCouriers = window.confirm(
        "Do you want to use existing couriers? Click 'Cancel' to add new couriers."
      );

      if (useExistingCouriers) {
        const couriersResponse = await fetch("http://localhost:5000/couriers", {
          method: "GET",
        });
        console.log("File sent to server:", file);
        const couriersResult = await couriersResponse.json();

        if (couriersResult.couriers && couriersResult.couriers.length > 0) {
          console.log("Existing couriers:", couriersResult.couriers);
          alert("Using existing couriers.");
        } else {
          alert("No existing couriers found. Please add new couriers.");
          console.log("Setting showCourierForm to true");
          setShowCourierForm(true); // הצגת טופס השליחים
        }
      } else {
        console.log("Setting showCourierForm to true");
        setShowCourierForm(true); // הצגת טופס השליחים
      }

      setIsProcessing(false);
    } catch (error) {
      console.error("Error processing the data:", error);
      setMessage({ message: "Error processing the data." });
      setIsProcessing(false);
    }
  };

  const handleAssignCouriers = async () => {
    console.log("Current tableData:", tableData);
    console.log("Current couriers:", couriers);

    const response = await fetch("http://localhost:5000/assign_couriers", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        deliveries: tableData, // רשימת המשלוחים
        couriers: couriers, // רשימת השליחים
      }),
    });

    const result = await response.json();

    if (response.ok) {
      alert("Couriers assigned successfully!");
      console.log("Assignments:", result.assignments);
    } else {
      alert("Error assigning couriers.");
      console.error(result.error);
    }
  };

  return (
    <div className="delivery-form-container">
      <h1>Welcome, Manager</h1>

      {!selectedOption && (
        <div className="delivery-form-actions">
          <button
            onClick={() => setSelectedOption("uploadFile")}
            className={`action-button ${selectedOption === "uploadFile" ? "active" : ""}`}
          >
            Upload File🔍
          </button>
          <button
            onClick={() => setSelectedOption("fillForm")}
            className={`action-button ${selectedOption === "fillForm" ? "active" : ""}`}
          >
            Fill Delivery Form📰
          </button>
        </div>
      )}

      {selectedOption === "uploadFile" && (
        <form onSubmit={handleSubmit} className="upload-form">
          <input type="file" accept=".csv,.json" onChange={handleFileUpload} />
          <button type="submit" className="submit-button">
            📤 Submit Data
          </button>
        </form>
      )}

      {selectedOption === "fillForm" && (
        <div>
          <DeliveryTable tableData={tableData} setTableData={setTableData} />
          <button
            onClick={handleSubmit}
            className="submit-button"
            style={{ marginTop: "20px" }}
          >
            📤 Submit Data
          </button>
        </div>
      )}

      <div className="delivery-form-content">
        {/* הצגת הודעה כאשר isProcessing הוא true */}
        {isProcessing && (
          <div className="processing-message">
            <p>Processing data, please wait...</p>
          </div>
        )}

        {/* הצגת ההודעה שחזרה מהשרת */}
        {message && (
          <div className="server-message">
            <p>{message.message}</p>
            {message.couriers_needed && (
              <p>Number of couriers needed: {message.couriers_needed}</p>
            )}
          </div>
        )}
      </div>

      {/* הצגת טופס השליחים כאשר showCourierForm הוא true */}
      {showCourierForm && (
        <CourierPanel
          couriers={couriers}
          setCouriers={setCouriers}
          setShowCourierForm={setShowCourierForm}
        />
      )}
    </div>
  );
};

export default DeliveryForm;
