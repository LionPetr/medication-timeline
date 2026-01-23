import React, { useState } from "react";
import "./UndatedMedications.css";

const formatDuration = (duration) => {
    if (!duration || duration === null || duration === 'null') return '';

    // Handle string format
    const durationStr = String(duration);

    // Match patterns like "7 days, 0:00:00" or "1 day, 0:00:00" or just "7 days"
    const match = durationStr.match(/(\d+)\s+day/);
    if (match) {
        const days = parseInt(match[1]);
        return days === 1 ? '1 day' : `${days} days`;
    }

    // If no match, return empty string instead of raw value
    return '';
};

const UndatedMedications = ({ items, onSelectMed }) => {
    const [selectedMed, setSelectedMed] = useState(null);

    if (!items || items.length === 0) {
        return null;
    }

    return (
        <>
            <div className="undated-section">
                <h3>Other Medications</h3>
                <div className="undated-list">
                    {items.map((med) => (
                        <div
                            key={med.id}
                            className="undated-item"
                            onClick={() => setSelectedMed(med)}
                        >
                            <span className="undated-med-name">{med.medication.name}</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Detail Modal */}
            {selectedMed && (
                <div className="modal-overlay" onClick={() => setSelectedMed(null)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <button className="modal-close" onClick={() => setSelectedMed(null)}>✕</button>
                        <h2>{selectedMed.medication.name}</h2>

                        {selectedMed.source_facility && (
                            <p><strong>Facility:</strong> {selectedMed.source_facility.name}</p>
                        )}
                        {selectedMed.notes && (
                            <p><strong>Notes:</strong> {selectedMed.notes}</p>
                        )}

                        {selectedMed.dosage_schedules && selectedMed.dosage_schedules.length > 0 && (
                            <div>
                                <h3>Dosage Schedule</h3>
                                <ul>
                                    {selectedMed.dosage_schedules.map((dosage, idx) => {
                                        const formattedDuration = formatDuration(dosage.duration);
                                        return (
                                            <li key={idx}>
                                                {dosage.dose && <><strong>{dosage.dose}</strong></>}
                                                {dosage.frequency && <>{dosage.dose ? ' - ' : ''}{dosage.frequency}</>}
                                                {dosage.route && <> ({dosage.route})</>}
                                                {formattedDuration && <span> for {formattedDuration}</span>}
                                            </li>
                                        );
                                    })}
                                </ul>
                            </div>
                        )}
                        {(!selectedMed.dosage_schedules || selectedMed.dosage_schedules.length === 0) && (
                            <p style={{ fontStyle: "italic", color: "#999" }}>No dosage information available</p>
                        )}
                    </div>
                </div>
            )}
        </>
    );
};

export default UndatedMedications;
