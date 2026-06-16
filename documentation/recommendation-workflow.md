# Recommendation Workflow: Chatbot → Preferences → Recommendation → Itinerary → Operator Review

This document explains how Htundla Safaris turns a visitor's guided chatbot answers into a draft itinerary and then exposes that itinerary for operator review.

## 1. Chatbot collects inquiry details

**Code location:** `core/templates/core/contactus.html`

The user-facing intake starts on the Contact Us page. The visible interface is a guided chatbot, while the real Django form is kept hidden and submitted after the conversation is complete.

Key code references:

- The chatbot UI containers are defined in the Contact Us template: `chat-thread`, `chat-actions`, and `chat-input` render the conversation, choices, and text input.
- The hidden Django form is rendered as `form.as_p` with CSRF protection. This keeps the normal Django POST workflow while presenting a conversational UI to the user.
- JavaScript reads destination choices from the hidden form's `destination` field, then falls back to a hard-coded destination list if no database destinations are available.
- JavaScript reads interest options from the hidden form's `interests` checkboxes so the chatbot uses the same allowed values as the backend form.
- The `steps` array controls the conversation order: full name, email, phone number, travel type, destination, duration, travel style, group size, and interests.

Step-by-step:

1. `ask()` displays the current question from the `steps` array.
2. For single-choice fields, the chatbot creates one button per choice.
3. For multi-choice interests, the chatbot lets the user toggle one or more interest buttons and then click **Finish Selection**.
4. For text fields, the chatbot validates the input before moving forward.
5. Duration is checked on the frontend, including the business rule that Safari trips must be between 3 and 5 days.
6. `record()` stores each answer in the `answers` object and advances the chatbot to the next step.
7. When all steps are complete, `submit()` copies chatbot answers into the hidden Django form fields and submits the form.

## 2. Preferences are validated by Django

**Code location:** `core/forms.py`

The backend validates the same preference data again through `InquiryForm`. This matters because frontend validation can be bypassed.

Key code references:

- `ALLOWED_INTERESTS` defines the controlled list of interest values accepted by the application.
- `InquiryForm` exposes the submitted fields: full name, email, phone number, travel type, destination, duration, travel style, group size, and interests.
- `clean_destination()` confirms the submitted destination exists in the database.
- `clean()` enforces the Safari duration rule again on the server: Safari trips must be between 3 and 5 days.

Step-by-step:

1. The POST request reaches Django with the hidden form values populated by the chatbot.
2. `InquiryForm(request.POST)` binds the submitted values.
3. Django field validation checks model-level types and validators, such as positive integers for duration and group size.
4. `clean_destination()` rejects unsupported destination IDs.
5. `clean()` rejects Safari requests outside the 3-to-5-day range.
6. If validation passes, the view can safely save the inquiry.

## 3. Inquiry is saved and recommendation generation starts

**Code location:** `core/views.py`

The `contact_us` view is the bridge between the chatbot submission and itinerary generation.

Key code references:

- On POST, `contact_us` creates an `InquiryForm` from `request.POST`.
- If the form is valid, `form.save()` creates an `Inquiry` record.
- Immediately after saving, the view calls `generate_itinerary(inquiry)`.
- The view displays a success message and redirects back to the Contact Us page.

Step-by-step:

1. User finishes the chatbot.
2. The hidden form submits a POST request to `contact_us`.
3. `InquiryForm` validates the submitted preferences.
4. `form.save()` persists the inquiry in the database.
5. `generate_itinerary(inquiry)` runs the recommendation engine for that inquiry.
6. The user sees confirmation that the inquiry was submitted and a draft itinerary was generated.

## 4. Data model links preferences, activities, itinerary, and operator response

**Code location:** `core/models.py`

The recommendation workflow depends on these model relationships:

- `Inquiry` stores the visitor's preferences: travel type, destination, duration, travel style, group size, and interests.
- `Activity` stores possible itinerary activities for destinations. Each activity includes travel type, style, interest category, suitable time slot, day suitability, intensity, and base score.
- `Itinerary` has a one-to-one relationship with `Inquiry`, meaning each inquiry gets one draft itinerary.
- `ItineraryItem` belongs to an `Itinerary`, meaning each draft itinerary can contain many day/time-slot activities.
- `OperatorResponse` has a one-to-one relationship with `Inquiry`, meaning the operator can add final cost, notes, status, and sent metadata for that inquiry.

Step-by-step data flow:

1. The chatbot produces an `Inquiry`.
2. The recommender searches `Activity` records matching that inquiry.
3. The recommender creates or refreshes the related `Itinerary`.
4. The recommender creates multiple `ItineraryItem` rows under that itinerary.
5. The operator later uses `OperatorResponse` to finalize proposal details.

## 5. Recommendation engine selects matching activities

**Code location:** `core/recommender.py`

The recommendation logic is deterministic and rule-based. It does not use machine learning or an external AI API. The selected activities are explainable because every score comes from explicit code rules.

### 5.1 Itinerary setup

1. `generate_itinerary(inquiry)` creates or retrieves the itinerary for the inquiry.
2. Existing itinerary items are deleted before regeneration, preventing duplicate or stale activities.
3. The recommender first searches for activities matching both the inquiry destination and travel type.
4. If no exact travel-type matches exist, it falls back to all activities for the selected destination.
5. If there are still no activities, the itinerary summary becomes `No matching activities found yet.` and generation stops.

### 5.2 Trip phase calculation

The `_phase(day, total)` helper labels each day as:

- `Arrival` for day 1.
- `Departure` for the final day.
- `Mid-trip` for all days between arrival and departure.

This lets the recommender prefer activities that fit the travel stage.

### 5.3 Scoring logic

The `_score(activity, inquiry, phase, slot, used_titles)` helper starts with `activity.base_score`, then adjusts the score:

| Rule | Score effect | Purpose |
| --- | ---: | --- |
| Activity style matches inquiry travel style | `+4` | Prefer Budget-friendly, Standard, or Luxury activities that match the user's selected style. |
| Activity interest is in the user's selected interests | `+5` | Strongly prefer activities aligned to the user's stated interests. |
| Activity day suitability matches the current phase, or is `Any` | `+3` | Prefer activities suitable for arrival, mid-trip, departure, or any day. |
| Activity time slot matches the current slot, or is `Flexible`/`Full-day` | `+3` | Prefer activities that fit Morning, Afternoon, or Evening scheduling. |
| Activity name has already been used | `-3` | Reduce repetition across the itinerary. |

### 5.4 Day-by-day and slot-by-slot assignment

1. The recommender loops from day `1` to `inquiry.duration_days`.
2. For each day, it calculates the phase with `_phase()`.
3. For each day, it fills the three configured slots: `Morning`, `Afternoon`, and `Evening`.
4. If all candidate activities have been used from the `remaining` list, the recommender resets `remaining` back to the full activity list.
5. It sorts remaining activities by highest score first. If scores tie, it sorts by activity name for deterministic output.
6. It chooses the top-ranked activity as the pick for that day and slot.
7. The picked activity is removed from `remaining` and added to `used`.
8. An `ItineraryItem` is created with day number, time slot, activity title, and notes showing phase, interest, intensity, and style.
9. After all days and slots are filled, the itinerary summary is updated with a plain-language draft summary.

## 6. Operator reviews and finalizes the proposal

**Code locations:** `core/admin.py`, `core/views.py`, and `core/templates/core/admin_dashboard.html`

After the draft itinerary exists, an operator can review inquiries and proposal information through the admin workflow and operator dashboard.

Key code references:

- `ItineraryAdmin` displays itinerary items inline, making the generated day/time-slot plan reviewable in Django admin.
- `InquiryAdmin` lists inquiry details and exposes an admin action named `finalize_and_send`.
- `finalize_and_send()` creates or retrieves an `OperatorResponse`, marks it finalized, records the operator and timestamp, sends an email, and updates the inquiry status to `Proposal Sent`.
- The `send_proposal` view is staff-protected, validates `ProposalForm`, stores final cost and proposal notes, sends an email including itinerary text, and updates the inquiry status.
- The operator dashboard shows recent inquiries with destination, status, itinerary item count, and an action link.

Step-by-step operator workflow:

1. Operator opens the Django admin or operator dashboard.
2. Operator reviews the inquiry preferences and generated itinerary items.
3. Operator adds proposal notes and final cost where needed.
4. Operator sends/finalizes the proposal.
5. The system records who finalized it, when it was sent, and updates the inquiry status to `Proposal Sent`.
6. The customer receives an email proposal containing notes, final cost, and itinerary details.

## 7. Full workflow summary

```text
Visitor answers chatbot questions
        ↓
Chatbot stores answers in JavaScript
        ↓
Chatbot copies answers into hidden Django form fields
        ↓
Django InquiryForm validates submitted preferences
        ↓
contact_us saves an Inquiry
        ↓
generate_itinerary searches and scores Activity records
        ↓
Itinerary and ItineraryItem records are created
        ↓
Operator reviews generated draft itinerary
        ↓
Operator finalizes proposal notes/cost
        ↓
System sends proposal email and marks inquiry as Proposal Sent
```

## 8. Why the logic is explainable

The recommendation output can be explained by looking at four inputs and five scoring rules:

1. **Inputs from the user:** destination, travel type, duration, style, and interests.
2. **Candidate activity metadata:** destination, travel type, style, interest, time slot, day suitability, intensity, and base score.
3. **Trip context:** arrival, mid-trip, or departure day.
4. **Schedule context:** Morning, Afternoon, or Evening slot.
5. **Scoring rules:** style match, interest match, phase suitability, slot suitability, and repetition penalty.

Because the recommender uses explicit scoring values and deterministic sorting, the same inquiry and activity data should produce the same draft itinerary every time.
