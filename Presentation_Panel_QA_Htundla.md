# Htundla Safaris Presentation Panel Q&A

This file replaces the previous `.docx` presentation-preparation document so the pull request can be reviewed without binary-file limitations.

## Focus Areas

- Guided chatbot flow
- Client-side and server-side validation
- Inquiry persistence
- Rule-based itinerary generation
- Database model relationships
- Django admin/operator workflow
- Email proposal flow

---

## 1. Chatbot Flow

**Question:** How does the chatbot move step-by-step instead of behaving like a normal form?

**Answer:** The chatbot is controlled by a structured JavaScript `steps` array. Each step contains the field key, question prompt, input type, and validation rule where needed. The `ask()` function displays the current question, and `record()` stores the response before advancing to the next step. This creates a guided, pre-programmed conversation.

**Code location:** `core/templates/core/contactus.html`

---

## 2. Client-Side Email Validation

**Question:** How is the email checked before the inquiry is submitted?

**Answer:** The email step uses a regular expression check before allowing the user to continue. This helps catch invalid email formats immediately on the frontend, although the backend still performs authoritative validation through Django forms.

**Code location:** `core/templates/core/contactus.html`

---

## 3. Client-Side Number Validation

**Question:** How are duration and group size validated in the chatbot?

**Answer:** Duration and group size are checked as positive numeric values on the client side. The Safari-specific business rule is also enforced in the chatbot so Safari trips must be between 3 and 5 days before the user can continue.

**Code location:** `core/templates/core/contactus.html`

---

## 4. Chatbot Submission Trigger

**Question:** How does chatbot data reach the Django backend?

**Answer:** After the final chatbot step, the collected answers are copied into hidden Django form fields. The script then triggers `form.submit()`, which sends the data to the Django `contact_us` view using the normal POST workflow and CSRF protection.

**Code locations:**

- `core/templates/core/contactus.html`
- `core/views.py`

---

## 5. Backend Inquiry Saving

**Question:** Where is the customer inquiry saved to the database?

**Answer:** The `contact_us` view receives the POST request, binds it to `InquiryForm`, validates it, and then saves it using `form.save()`. After saving, the system immediately calls `generate_itinerary(inquiry)` to create a draft itinerary.

**Code location:** `core/views.py`

---

## 6. Backend Validation

**Question:** Why is backend validation necessary if the chatbot already validates inputs?

**Answer:** Frontend validation improves user experience, but it cannot be trusted because users can bypass or modify browser-side code. Backend validation in `InquiryForm` is authoritative and protects the database from invalid categorical values, unsupported destinations, and invalid Safari durations.

**Code location:** `core/forms.py`

---

## 7. Destination and Activity Retrieval

**Question:** How does the system retrieve destinations and activities?

**Answer:** Django ORM queries are used instead of raw SQL. Destinations are retrieved for page/form rendering, while the recommender filters activities by the selected destination and travel type. If no exact travel-type match is found, it falls back to destination-only activities.

**Code locations:**

- `core/views.py`
- `core/recommender.py`

---

## 8. Rule-Based Recommendation Scoring

**Question:** How does the itinerary recommendation engine decide which activities are best?

**Answer:** The recommender uses a deterministic scoring function. It adds weight for travel style match, user interest match, day suitability, and time-slot suitability. The highest-ranked available activity is selected for each itinerary slot.

**Code location:** `core/recommender.py`

---

## 9. Itinerary Day-by-Day Assignment

**Question:** How is the final draft itinerary created?

**Answer:** The recommender loops through each day of the requested duration and assigns activities into Morning, Afternoon, and Evening slots. It ranks available activities, selects the best candidate, removes it from the remaining pool to reduce repetition, and creates an `ItineraryItem` record.

**Code location:** `core/recommender.py`

---

## 10. Itinerary Regeneration Cleanup

**Question:** What happens if an itinerary needs to be regenerated?

**Answer:** Existing itinerary items are deleted before new ones are created. This prevents duplicate or stale itinerary entries from remaining in the database.

**Code location:** `core/recommender.py`

---

## 11. Database Relationships

**Question:** What are the main database relationships in the system?

**Answer:** The main relationships are:

- `Inquiry` belongs to a selected `Destination`.
- `Itinerary` has a one-to-one relationship with `Inquiry`.
- `ItineraryItem` belongs to an `Itinerary`.
- `OperatorResponse` has a one-to-one relationship with `Inquiry`.
- `Activity` belongs to a `Destination`.

**Code location:** `core/models.py`

---

## 12. Admin Panel Workflow

**Question:** How does the operator view and process chatbot inquiries?

**Answer:** Django admin provides the centralized backend interface. Operators can view submitted inquiries, review generated itineraries, add proposal notes and final costs, and use admin actions to finalize and send proposals.

**Code locations:**

- `core/admin.py`
- `core/models.py`

---

## 13. Proposal Finalization

**Question:** How does the system mark a proposal as finalized and sent?

**Answer:** The admin action or proposal view updates the operator response, sets the finalized flag, records the sent timestamp, stores the operator user, and updates the inquiry status to `Proposal Sent`.

**Code locations:**

- `core/admin.py`
- `core/views.py`

---

## 14. Email Proposal Flow

**Question:** How does the project handle proposal email communication?

**Answer:** The system uses Django's `send_mail()` function. In development, the project uses Django's console email backend, so emails are printed in the terminal instead of being sent to real customers. This is safer for demonstration and testing.

**Code locations:**

- `core/admin.py`
- `core/views.py`
- `htundla_safaris/settings.py`

---

## 15. Seed Data

**Question:** How are destinations and activities loaded for demonstrations?

**Answer:** The `seed_data` management command creates or updates destination and activity records. It uses `get_or_create()` for destinations and `update_or_create()` for activities, making the command safe to run multiple times during testing.

**Code location:** `core/management/commands/seed_data.py`

---

## Short Defense Summary

The system uses a simple Django architecture with a guided JavaScript chatbot on the frontend, Django forms for backend validation, SQLite/Django ORM for persistence, a deterministic rule-based recommendation module for itinerary generation, and Django admin for operator review and final proposal handling. This keeps the project explainable, demo-friendly, and suitable for an academic final-year project.
