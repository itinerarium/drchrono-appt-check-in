# drchrono Hackathon

## drchrono appointment kiosk

The drchrono appointment kiosk offers patients a paperless, digital check-in experience and offers doctors an opportunity to gather and view patient wait time metrics.

**Brief: Check-in kiosk**

Picture going to the doctor's office and replacing the receptionist and paper forms with a kiosk similar to checking in for a flight.

There should be an account association flow where a doctor can authenticate using their drchrono account and set up the kiosk for their office.

After the doctor is logged in, a page should be displayed that lets patients check in. A patient with an appointment should first confirm their identity (first/last name maybe SSN) then be able to update their demographic information using the patient chart API endpoint.  Once the they have filled out that information the app can set the appointment status to "Arrived" (Appointment API Docs).

The doctor should also have their own page they can leave open that displays today’s appointments, indicating which patients have checked in and how long they have been waiting. From this screen, the doctor can indicate they are seeing a patient, which stops the “time spent waiting” clock. The doctor should also see the overall average wait time for all patients they have ever seen.
Outside of these base requirements, you are free to develop any features you think make sense.

### Notes

Again, while inferences and considerations were made without contact with the end user, the idea is to iterate on the project based on actual use.

drchrono, as practice management software, serves as the system of record and a balance is to be struck between storing data necessary for use of the system locally, caching, and querying live data on each access to ensure freshness.

### Thoughts

1. While the receptionist's work can be reduced, there are situations where human intervention should be expected (e.g., for cancelling a check-in, rescheduling, walk-in, new patient forms, etc). Additionally, identity verification is weak, based on public details (that must be matched exactly). Perhaps, consider ID scanning in the future?
2. Should the system source and accept important data points that the system does not have on record? No, as some form of human verification process should be expected (e.g., if there is no date of birth on record, one should be entered when it is read off a trustworthy document).
3. The brief requests identity confirmation, at minimum, with first and last names. However, neither field is required and the patient may not know what name is on their record (e.g., Alexa versus Alexandria or due to typos in back office data entry). As a result, the patient is able to choose their appointment time (and, in cases of duplicate appointments, their appointment ID, which should be known to them in a reminder?) and we seek to confirm the details that are present in drchrono. If this verification is not successful, office staff should be expected to assist. Also, this approach increases the effort to determine if a given patient is to be seen on a day as all appointments may need to be tested. (There was an initial problematic (two patients can have identical initials at the same time) idea to allow patients to select their appointment based on initials and time, confirming their identity by choosing their name components from several options with the same initials.)
4. The brief suggests that the doctor initially authenticates with their credentials. However, their credentials are tied to their drchrono account and reuse of their session could be problematic. An initial solution is to create a GUID for the kiosk, end the doctor's session, and utilize the difficult to guess property of the GUID to limit access for kiosk functions.
5. Should log out functionality exist for the kiosk? A patient could inadvertently log out for the practice, disabling the device. The doctor can terminate the session from their site.
6. How should a check-in be cancelled? As noted previously, the humans are not removed from the loop and the doctor mark the status to cancelled if the patient changes their mind.
7. How should abandonment be handled? Pages have timeouts that result in redirection to the kiosk screen.
8. How should wait time be calculated? As status change times do not appear to be available from the API, arrival times are tracked locally. Industry guidance will be helpful for determining if naive wait time (relative to arrival time) is preferable or relative to max(appointment time, arrival time) for early/late arrivals would be more helpful (or some other variation).
9. The brief requests an average wait time over all patients and the values can be affected by outliers. While a median or distribution is more likely to be helpful, average is implemented, to begin, as requested. Separately, calculating the average over a large number of entries can be simplified by only keeping track of the sum and number of items.
10. To avoid patient frustration (e.g., name mismatch), have an error page suggesting that human intervention be sought.
11. Pages work without JavaScript enabled, allowing for operation on low-powered devices (and in special environments) and minimized maintenance.
12. A day's appointments can easily include the next day (e.g., at night). For now, only the current day's appointments (including those in the past) are shown. Consider getting user insight regarding having a sliding window and handling no-shows on behalf of the practice (separate batch process?).
13. Consider options to create audit logs as API-level changes may not have the associated reasoning checked.
14. The demographic update options exposed to the patient are fewer than those exposed by the API (which, in turn, is fewer than those exposed by the web interface). The exposed fields are those seen as likely to change and can safely be changed without human verification. End user testing may reveal changes to the field set.
15. Operations occur based on the selected timezone (defaulting to US/Eastern) for now, pending implementation of the sliding window for appointments.
16. No-shows/session completion should be handled elsewhere. No-shows can be easily handled as a nightly (or appropriately offset) process for the previous conceptual day while session completion should end with the saving of the electronic health record (as the check-in kiosk does not handle the data collection for the health care visit).
17. One would expect the doctor to retrieve the next patient's details prior to welcoming the patient. Accordingly, there is no need (and a benefit) to not displaying patient names on the doctor view (e.g., curious patients when the doctor looks away).

### Oddities
1. API does not appear to provide timezone of office, but times and dates without timezones.
2. Patching an empty string appears to be problematic for appointment status.
3. Some demographic details, shown on the internal interface, does not appear to be accessible through the API.

### Unrequested features

1. Error page for human intervention
2. Drop access using stored tokens
3. Added identifiers for separate per-doctor devices within a practice.
4. Separate identification (using asterisk) for untracked arrivals (i.e., entered via the calendar interface) for which no wait time information is available.
5. Dashboard to allow patients to change their mind (i.e., cancel after arrival).

### TODO

1. Assumption is that token access will not be revoked. However, failed get requests will be noted. Failed PATCH requests are not retried.
