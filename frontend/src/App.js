import React, { useEffect, useState } from "react";
import MedicationTimeline from "./components/Timeline";
import UndatedMedications from "./components/UndatedMedications";
import AddPrescription from "./components/AddPrescription";

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [timelineItems, setTimelineItems] = useState([]);
  const [undatedItems, setUndatedItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchTimeline = async () => {
    try {
      const response = await fetch(
        `${API_URL}/api/patients/1/timeline/`,
        { timeout: 60000 }  // 60 second timeout for cold starts
      );

      if (!response.ok) {
        throw new Error("Failed to fetch medication timeline");
      }

      const data = await response.json();
      setTimelineItems(data);
      setError(null);  // Clear any previous errors on success
    } catch (err) {
      if (err.name === 'TypeError' && err.message.includes('fetch')) {
        setError("Server is starting up (this takes 30-60 seconds on first load). Please wait...");
      } else {
        setError(err.message);
      }
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
      // Silently fail - undated meds section just won't show
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
      <div style={{ padding: 20 }}>
        <div style={{ color: "red", marginBottom: 10 }}>
          Error: {error}
        </div>
        <button onClick={() => {
          setLoading(true);
          setError(null);
          fetchTimeline();
          fetchUndatedMeds();
        }}>
          Retry
        </button>
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