import React, { useState } from "react";
import "./Timeline.css";

const formatDuration = (duration) => {
    if (!duration) return '';
    // Extract just the days part from "X day(s), HH:MM:SS" or "X days"
    const match = duration.match(/(\d+)\s+day/);
    if (match) {
        const days = parseInt(match[1]);
        return days === 1 ? '1 day' : `${days} days`;
    }
    return duration;
};

const getDateRange = (start, end) => {
    const result = [];
    let [y, m, d] = start.split("-").map(Number);
    const [ey, em, ed] = end.split("-").map(Number);

    while (
        y < ey ||
        (y === ey && m < em) ||
        (y === ey && m === em && d <= ed)
    ) {
        result.push(
            `${y}-${String(m).padStart(2, "0")}-${String(d).padStart(2, "0")}`
        );

        d++;
        const daysInMonth = new Date(y, m, 0).getDate();
        if (d > daysInMonth) {
            d = 1;
            m++;
            if (m > 12) {
                m = 1;
                y++;
            }
        }
    }

    return result;
};

/**
 * Stack overlapping meds into rows
 * Same medications stay on same row (old gets truncated), different meds stack
 */
const assignRows = (items) => {
    const medRowMap = {};
    const rows = [];

    items.forEach((item) => {
        const start = item.start_date;
        const end = item.end_date;

        let row;

        if (medRowMap[item.medication] !== undefined) {
            row = medRowMap[item.medication];
        } else {
            row = 0;
            while (true) {
                if (!rows[row]) rows[row] = [];
                const conflict = rows[row].some(
                    (r) => r.medication !== item.medication && r.start_date <= end && r.end_date >= start
                );
                if (!conflict) break;
                row++;
            }
            medRowMap[item.medication] = row;
        }

        if (!rows[row]) rows[row] = [];
        rows[row].push(item);
        item._row = row;
    });
};

const Timeline = ({ items, daysAfter = 14, apiUrl, onPrescriptionDeleted }) => {
    const [selectedMed, setSelectedMed] = useState(null);
    const [deleting, setDeleting] = useState(false);

    const handleDelete = async () => {
        if (!selectedMed || !selectedMed.id) return;

        if (!window.confirm("Are you sure you want to delete this prescription?")) {
            return;
        }

        setDeleting(true);
        try {
            const response = await fetch(`${apiUrl}/api/prescriptions/${selectedMed.id}/`, {
                method: "DELETE"
            });

            if (!response.ok) {
                throw new Error("Failed to delete prescription");
            }

            setSelectedMed(null);
            if (onPrescriptionDeleted) {
                onPrescriptionDeleted();
            }
        } catch (err) {
            alert(`Error deleting prescription: ${err.message}`);
        } finally {
            setDeleting(false);
        }
    };

    if (!items || items.length === 0) {
        return <div>No medication history</div>;
    }

    const dates = items.flatMap((i) => [i.start_date, i.end_date]).sort();
    const minDate = dates[0];
    const maxDate = dates[dates.length - 1];

    const [y, m, d] = maxDate.split("-").map(Number);
    let extendedDay = d + daysAfter;
    let extendedMonth = m;
    let extendedYear = y;

    const daysInMonth = new Date(extendedYear, extendedMonth, 0).getDate();
    while (extendedDay > daysInMonth) {
        extendedDay -= daysInMonth;
        extendedMonth++;
        if (extendedMonth > 12) {
            extendedMonth = 1;
            extendedYear++;
        }
    }

    const extendedMaxDate = `${extendedYear}-${String(extendedMonth).padStart(2, "0")}-${String(extendedDay).padStart(2, "0")}`;

    const timelineDays = getDateRange(minDate, extendedMaxDate);

    assignRows(items);

    return (
        <div className="timeline-container">
            {/* Day ruler */}
            <div
                className="timeline-ruler"
                style={{
                    gridTemplateColumns: `repeat(${timelineDays.length}, 80px)`,
                }}
            >
                {timelineDays.map((day) => (
                    <div key={day} className="timeline-day">
                        {day.slice(5)}
                    </div>
                ))}
            </div>

            {/* Medication bars */}
            <div
                className="timeline-bars"
                style={{
                    gridTemplateColumns: `repeat(${timelineDays.length}, 80px)`,
                }}
            >

                {items.map((med) => {
                    let displayEndDate = med.end_date;

                    // Subtract a day from truncated meds for display
                    if (med.is_truncated) {
                        const [y, m, d] = med.end_date.split("-").map(Number);
                        let newDay = d - 1;
                        let newMonth = m;
                        let newYear = y;

                        if (newDay < 1) {
                            newMonth--;
                            if (newMonth < 1) {
                                newMonth = 12;
                                newYear--;
                            }
                            newDay = new Date(newYear, newMonth, 0).getDate();
                        }

                        displayEndDate = `${newYear}-${String(newMonth).padStart(2, "0")}-${String(newDay).padStart(2, "0")}`;
                    }

                    const startIndex = timelineDays.indexOf(med.start_date);
                    const endIndex = timelineDays.indexOf(displayEndDate);

                    if (startIndex === -1 || endIndex === -1) {
                        return null;
                    }

                    return (
                        <div
                            key={med.id}
                            className="medication-bar"
                            style={{
                                gridColumnStart: startIndex + 1,
                                gridColumnEnd: endIndex + 2,
                                gridRowStart: med._row + 1,
                                cursor: "pointer",
                            }}
                            title={`${med.medication}\n${med.start_date} → ${med.end_date}`}
                            onClick={() => setSelectedMed(med)}
                        >
                            {med.medication}
                        </div>
                    );
                })}
            </div>

            {/* Detail Modal */}
            {selectedMed && (
                <div className="modal-overlay" onClick={() => setSelectedMed(null)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <button className="modal-close" onClick={() => setSelectedMed(null)}>✕</button>
                        <h2>{selectedMed.medication}</h2>
                        <p><strong>Start Date:</strong> {selectedMed.start_date}</p>
                        <p><strong>End Date:</strong> {selectedMed.end_date}</p>

                        {selectedMed.notes && (
                            <p><strong>Notes:</strong> {selectedMed.notes}</p>
                        )}

                        {selectedMed.dosages && selectedMed.dosages.length > 0 && (
                            <div>
                                <h3>Dosage Schedule</h3>
                                <ul>
                                    {selectedMed.dosages.map((dosage, idx) => (
                                        <li key={idx}>
                                            <strong>{dosage.dose}</strong> - {dosage.frequency} ({dosage.route})
                                            {dosage.duration && <span> for {formatDuration(dosage.duration)}</span>}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        <button
                            className="delete-btn"
                            onClick={handleDelete}
                            disabled={deleting}
                        >
                            {deleting ? "Deleting..." : "Delete Prescription"}
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Timeline;