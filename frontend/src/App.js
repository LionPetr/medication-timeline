import React, { useEffect, useState } from "react";
import MedicationTimeline from "./components/Timeline";
import UndatedMedications from "./components/UndatedMedications";

function App() {
  const [timelineItems, setTimelineItems] = useState([]);
  const [undatedItems, setUndatedItems] = useState([]);
  const [selectedMed, setSelectedMed] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTimeline = async () => {
      try {
        const response = await fetch(
          "http://localhost:8000/api/patients/1/timeline/"
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
          "http://localhost:8000/api/patients/1/undated_medications/"
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
      <MedicationTimeline items={timelineItems} onSelectMed={setSelectedMed} selectedMed={selectedMed} />
      <UndatedMedications items={undatedItems} onSelectMed={setSelectedMed} />
    </div>
  );
}

export default App;