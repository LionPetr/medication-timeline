# medication-timeline


conflicting prescriptions will be overriden by the newest prescription as it follows real world prescription usage.  

The prescription end date will be calculated using the duration field in the DosageSchedule objects attached to the prescription. if there is no DosageSchedule field then the medication 
will be shown to have been taken for 1 day using the start date. 

no start date will be defaulted to nothing and will need to be shown using some kind of visual element on the timeline 
and marked as "no start date" when user checks record

changes to medication will be marked on the timeline 

there will be 2 different timelines one showing the overall patient timeline with all courses of medication prescribed 
and another showing a specific medication course timeline and all the changes associated with that medication 

For future implementation: 
- add more robust rules when it comes to conflict checking 
- add clinician tables with things like contact information to establish proper communication channels 
- making Route its own table if there are more ways to administer medicine
- add a range for different medications using the medication table and give a warning if the dosage is outside of that range (in case of mistyping)
- add a system to recycle lines that arnt being used anymore (if prescription ends the line can be used for a new prescription)