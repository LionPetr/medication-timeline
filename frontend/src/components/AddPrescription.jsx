import React, { useState, useEffect } from "react";
import "./AddPrescription.css";

const AddPrescription = ({ patientId, onPrescriptionAdded, apiUrl }) => {
    const [showForm, setShowForm] = useState(false);
    const [medications, setMedications] = useState([]);
    const [formData, setFormData] = useState({
        medication_id: "",
        start_date: "",
        notes: "",
        dosages: [{ dose: "", frequency: "", route: "", duration: "" }]
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchMedications();
    }, []);

    const fetchMedications = async () => {
        try {
            const response = await fetch(`${apiUrl}/api/medications/`);
            if (!response.ok) throw new Error("Failed to fetch medications");
            const data = await response.json();
            setMedications(data);
        } catch (err) {
            console.error("Error fetching medications:", err);
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleDosageChange = (index, field, value) => {
        const newDosages = [...formData.dosages];
        newDosages[index][field] = value;
        setFormData(prev => ({ ...prev, dosages: newDosages }));
    };

    const addDosageField = () => {
        setFormData(prev => ({
            ...prev,
            dosages: [...prev.dosages, { dose: "", frequency: "", route: "", duration: "" }]
        }));
    };

    const removeDosageField = (index) => {
        if (formData.dosages.length > 1) {
            setFormData(prev => ({
                ...prev,
                dosages: prev.dosages.filter((_, i) => i !== index)
            }));
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        console.log("Form data:", formData);
        console.log("Medication ID:", formData.medication_id, "Type:", typeof formData.medication_id);

        // Validate medication is selected
        if (!formData.medication_id || formData.medication_id === "") {
            setError("Please select a medication");
            return;
        }

        setLoading(true);
        setError(null);

        try {
            const medicationId = parseInt(formData.medication_id);
            console.log("Parsed medication ID:", medicationId);

            const payload = {
                patient: parseInt(patientId),
                medication: medicationId,
                start_date: formData.start_date || null,  // Allow null for undated medications
                notes: formData.notes
            };
            console.log("Sending payload:", payload);

            // Create prescription
            const prescriptionResponse = await fetch(`${apiUrl}/api/prescriptions/`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            if (!prescriptionResponse.ok) {
                const errorData = await prescriptionResponse.json().catch(() => ({}));
                throw new Error(JSON.stringify(errorData) || "Failed to create prescription");
            }

            const prescription = await prescriptionResponse.json();

            // Create dosage schedules
            for (const dosage of formData.dosages) {
                if (dosage.dose || dosage.frequency || dosage.route) {
                    // Parse duration as integer, default to 1 if empty
                    const durationDays = dosage.duration && dosage.duration !== "" ? parseInt(dosage.duration) : 1;

                    const payload = {
                        prescription: prescription.id,
                        dose: dosage.dose,
                        frequency: dosage.frequency,
                        route: dosage.route,
                        duration: durationDays
                    };
                    console.log("Sending dosage payload:", payload);

                    const dosageResponse = await fetch(`${apiUrl}/api/dosageschedules/`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(payload)
                    });

                    if (!dosageResponse.ok) {
                        const dosageError = await dosageResponse.json().catch(() => ({}));
                        console.error("Dosage error response:", dosageError);
                        throw new Error(`Failed to create dosage schedule: ${JSON.stringify(dosageError)}`);
                    }
                }
            }

            // Reset form and notify parent
            setFormData({
                medication_id: "",
                start_date: "",
                notes: "",
                dosages: [{ dose: "", frequency: "", route: "", duration: "" }]
            });
            setShowForm(false);
            onPrescriptionAdded();
        } catch (err) {
            setError(err.message);
            console.error("Error creating prescription:", err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="add-prescription-container">
            {!showForm ? (
                <button
                    className="add-prescription-btn"
                    onClick={() => setShowForm(true)}
                >
                    + Add Prescription
                </button>
            ) : (
                <form className="add-prescription-form" onSubmit={handleSubmit}>
                    <h3>Add New Prescription</h3>

                    <div className="form-group">
                        <label>Medication *</label>
                        <select
                            name="medication_id"
                            value={formData.medication_id}
                            onChange={handleInputChange}
                            required
                        >
                            <option value="">Select a medication</option>
                            {medications.map(med => (
                                <option key={med.id} value={med.id}>{med.name}</option>
                            ))}
                        </select>
                    </div>

                    <div className="form-group">
                        <label>Start Date (optional)</label>
                        <input
                            type="date"
                            name="start_date"
                            value={formData.start_date}
                            onChange={handleInputChange}
                        />
                    </div>

                    <div className="form-group">
                        <label>Notes</label>
                        <textarea
                            name="notes"
                            value={formData.notes}
                            onChange={handleInputChange}
                            placeholder="Add any notes about this prescription"
                        />
                    </div>

                    <div className="dosages-section">
                        <h4>Dosage Schedules</h4>
                        {formData.dosages.map((dosage, index) => (
                            <div key={index} className="dosage-group">
                                <div className="dosage-fields">
                                    <input
                                        type="text"
                                        placeholder="Dose (e.g., 2 pills)"
                                        value={dosage.dose}
                                        onChange={(e) => handleDosageChange(index, "dose", e.target.value)}
                                    />
                                    <input
                                        type="text"
                                        placeholder="Frequency (e.g., twice daily)"
                                        value={dosage.frequency}
                                        onChange={(e) => handleDosageChange(index, "frequency", e.target.value)}
                                    />
                                    <select
                                        value={dosage.route}
                                        onChange={(e) => handleDosageChange(index, "route", e.target.value)}
                                    >
                                        <option value="">Route</option>
                                        <option value="oral">Oral</option>
                                        <option value="intravenous">Intravenous</option>
                                        <option value="intramuscular">Intramuscular</option>
                                        <option value="subcutaneous">Subcutaneous</option>
                                        <option value="topical">Topical</option>
                                        <option value="inhalation">Inhalation</option>
                                        <option value="rectal">Rectal</option>
                                        <option value="other">Other</option>
                                    </select>
                                    <input
                                        type="number"
                                        min="1"
                                        max="100"
                                        placeholder="Duration (days: 1-100)"
                                        value={dosage.duration}
                                        onChange={(e) => handleDosageChange(index, "duration", e.target.value)}
                                    />
                                </div>
                                {formData.dosages.length > 1 && (
                                    <button
                                        type="button"
                                        className="remove-dosage-btn"
                                        onClick={() => removeDosageField(index)}
                                    >
                                        Remove
                                    </button>
                                )}
                            </div>
                        ))}
                        <button
                            type="button"
                            className="add-dosage-btn"
                            onClick={addDosageField}
                        >
                            + Add Another Dosage
                        </button>
                    </div>

                    {error && <p className="error-message">{error}</p>}

                    <div className="form-actions">
                        <button type="submit" disabled={loading}>
                            {loading ? "Saving..." : "Save Prescription"}
                        </button>
                        <button
                            type="button"
                            onClick={() => setShowForm(false)}
                            disabled={loading}
                        >
                            Cancel
                        </button>
                    </div>
                </form>
            )}
        </div>
    );
};

export default AddPrescription;
