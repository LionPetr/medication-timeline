# medication-timeline


conflicts will be represented with red on the timeline 

no end date will be defaulted to currently taking (marked as present on the end date)

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