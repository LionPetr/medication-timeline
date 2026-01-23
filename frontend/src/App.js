import React, { useEffect, useState } from "react";
import MedicationTimeline from "./components/Timeline";
import UndatedMedications from "./components/UndatedMedications";
import AddPrescription from "./components/AddPrescription";

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [timelineItems, setTimelineItems] = useState([]);
  const [undatedItems, setUndatedItems] = useState([]);
  const [selectedMed, setSelectedMed] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchTimeline = async () => {
    try {
      const response = await fetch(
        `${API_URL}/api/patients/1/timeline/`
      );

      if (!response.ok) {
        throw new Error("Failed to fetch medication timeline");
      }

      const data = await response.json();
      setTimelineItems(data);
    } catch (err) {
      console.error(err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchUndatedMeds = async () => {
    try {
      const response = await fetch(
        `${API_URL}/api/patients/1/undated_medications/`
      );

      if (!response.ok) {
        throw new Error("Failed to fetch undated medications");
      }

      const data = await response.json();
      setUndatedItems(data);
    } catch (err) {
      console.error("Error fetching undated meds:", err);
    }
  };

  useEffect(() => {
    fetchTimeline();
    fetchUndatedMeds();
  }, []);

  if (loading) {
    return <div style={{ padding: 20 }}>Loading medication timeline…</div>;
  }

  if (error) {
    return (
      <div style={{ padding: 20, color: "red" }}>
        Error: {error}
      </div>
    );
  }

  return (
    <div style={{ padding: 20 }}>
      <h2>Medication History</h2>
      <AddPrescription
        patientId={1}
        onPrescriptionAdded={() => {
          fetchTimeline();
          fetchUndatedMeds();
        }}
        apiUrl={API_URL}
      />
      <MedicationTimeline
        items={timelineItems}
        apiUrl={API_URL}
        onPrescriptionDeleted={() => {
          fetchTimeline();
          fetchUndatedMeds();
        }}
      />
      <UndatedMedications
        items={undatedItems}
        apiUrl={API_URL}
        onPrescriptionDeleted={() => {
          fetchTimeline();
          fetchUndatedMeds();
        }}
      />
    </div>
  );
}

export default App;