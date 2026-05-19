# Htundla Safaris — Presentation Panel Q&A (Source-Code Focus)

Below are high-impact questions a panelist is likely to ask, with concise model answers and exact code locations.

## 1) Chatbot / Inquiry Intake Flow

### Q1. Is this a true AI chatbot or a guided form flow? Why was this approach chosen?
**Answer:** It is a guided, deterministic intake flow (not LLM-driven). The project explicitly avoids external AI dependencies and uses rule-based logic so behavior is predictable, explainable, and easier to assess academically.

**Where in code:**
- `README.md` (features/notes mention guided chatbot + rule-based recommendation)
- `core/forms.py` (`InquiryForm` defines structured fields and allowed interests)
- `core/views.py` (`contact_us` handles POST validation and submission)

### Q2. What validations happen before an inquiry is accepted?
**Answer:** Validation exists both in model constraints and form-level checks. Examples: `duration_days` and `group_size` must be positive; phone format is regex-validated; destination must exist; Safari trips are constrained to 3–5 days in form `clean()`.

**Where in code:**
- `core/models.py` (`MinValueValidator`, `RegexValidator` in `Inquiry`)
- `core/forms.py` (`clean_destination`, `clean`)

### Q3. How do you prevent invalid “interest” values from entering the system?
**Answer:** Interests are restricted by `ALLOWED_INTERESTS` and exposed as `MultipleChoiceField`; only listed options can be submitted through normal form validation.

**Where in code:**
- `core/forms.py` (`ALLOWED_INTERESTS`, `InquiryForm.interests`)
- `core/models.py` (`interests` stored as `JSONField`)

## 2) Itinerary Generation Logic

### Q4. Walk through what happens right after a valid inquiry is submitted.
**Answer:** In `contact_us`, the form is saved, then `generate_itinerary(inquiry)` is called immediately. A draft itinerary is created/reset and filled day-by-day across Morning/Afternoon/Evening slots.

**Where in code:**
- `core/views.py` (`contact_us`)
- `core/recommender.py` (`generate_itinerary`)

### Q5. How are activities ranked for each slot?
**Answer:** The score combines: base score, style match, interest match, day-phase suitability (Arrival/Mid-trip/Departure), time-slot fit, and a repeat penalty if already used. Highest score wins; ties break by activity name.

**Where in code:**
- `core/recommender.py` (`_score`, `sorted(... key=lambda a: (-_score(...), a.name))`)

### Q6. How do you handle sparse data (few activities) or no matches?
**Answer:** If no activities match travel type, it falls back to all destination activities. If still empty, it writes a summary saying no matches found. If activities run out mid-generation, the list is recycled to continue filling slots.

**Where in code:**
- `core/recommender.py` (fallback filters, `if not activities`, `if not remaining: remaining = activities[:]`)

### Q7. Why choose rule-based recommendation instead of ML?
**Answer:** For this project, explainability and deterministic outputs are priorities. Every itinerary choice can be justified using explicit scoring factors visible in source code, which is ideal for demonstration and operator trust.

**Where in code:**
- `README.md` (rule-based rationale)
- `core/recommender.py` (transparent scoring function)

## 3) Database & Data Model

### Q8. What are the core entities and relationships?
**Answer:**
- `Destination` 1→many `Activity`
- `Inquiry` references one `Destination`
- `Inquiry` 1→1 `Itinerary`
- `Itinerary` 1→many `ItineraryItem`
- `Inquiry` 1→1 `OperatorResponse`
- `Operator` 1→1 Django `User`

**Where in code:**
- `core/models.py` (all FK and OneToOneField definitions)

### Q9. Why store `interests` as JSON instead of a normalized many-to-many table?
**Answer:** It simplifies capture of multiple checkbox choices for this prototype and aligns with rule-based matching (`interest in inquiry.interests`). Tradeoff: weaker relational integrity and less flexible analytics compared to normalized taxonomy tables.

**Where in code:**
- `core/models.py` (`Inquiry.interests = models.JSONField(default=list)`)
- `core/recommender.py` (`if activity.interest in inquiry.interests`)

### Q10. What data-protection or integrity safeguards exist?
**Answer:** Examples include `on_delete=models.PROTECT` for inquiry destination (prevents deleting referenced destination), validators for numeric and phone fields, and constrained choices for key enums (travel type/style/time slots).

**Where in code:**
- `core/models.py` (validators, choices, `on_delete` behaviors)

## 4) Admin Panel / Operator Workflow

### Q11. What exactly does the admin do after a draft itinerary is generated?
**Answer:** Admin/operators review inquiry details, adjust/finalize proposal details (`OperatorResponse`), and send proposal emails. They can also run a bulk action to finalize and send selected inquiries.

**Where in code:**
- `core/admin.py` (`InquiryAdmin`, `OperatorResponseAdmin`, `finalize_and_send` action)
- `core/views.py` (`send_proposal` endpoint for finalize/send path)

### Q12. How is proposal sending implemented?
**Answer:** Uses Django `send_mail`. In development, backend defaults to console output (per README), so emails are observable in terminal. On send, status is updated to `Proposal Sent`, and timestamps/operator metadata are recorded.

**Where in code:**
- `core/views.py` (`send_proposal`)
- `core/admin.py` (`finalize_and_send`)
- `README.md` (console email backend note)

### Q13. Are there any authorization gaps panelists may ask about?
**Answer:** Yes—`send_proposal` does not enforce explicit staff/admin permission in the view itself; it only checks whether user is authenticated to assign operator identity. In production, this should be protected (e.g., `@staff_member_required` or permission checks).

**Where in code:**
- `core/views.py` (`send_proposal`)

## 5) Architecture & Maintainability

### Q14. Where is separation of concerns visible?
**Answer:**
- Validation: `core/forms.py`
- Persistence schema: `core/models.py`
- Request/response orchestration: `core/views.py`
- Recommendation domain logic: `core/recommender.py`
- Back-office operations: `core/admin.py`

This is a clean, understandable layering for a student project.

**Where in code:**
- files listed above

### Q15. If you had to scale this, what would you refactor first?
**Answer:** Move proposal lifecycle into dedicated service methods, add stricter permission gates, normalize interests taxonomy, add tests for scoring determinism and edge cases, and make itinerary generation async for heavier workloads.

**Where in code to start:**
- `core/views.py` / `core/admin.py` (shared sending/finalization logic)
- `core/recommender.py` (unit-testable scoring and generation rules)
- `core/models.py` (schema evolution)

## 6) Good “defense” points for viva/panel discussion

### Q16. What design choices are intentionally simple?
**Answer:** Deterministic scoring, Django admin-led operations, and console-email default are deliberate to prioritize demonstrability, traceability, and low operational complexity for an academic prototype.

**Where in code:**
- `README.md`
- `core/recommender.py`
- `core/admin.py`

### Q17. What known limitations would you openly acknowledge?
**Answer:** No true conversational AI/NLP, limited permission hardening around proposal endpoint, no explicit automated test suite in repo, and simplified data modeling for interests. These are acceptable for MVP/demo but should be addressed for production.

**Where in code:**
- `core/views.py`, `core/forms.py`, `core/models.py`, `core/recommender.py`

---

## Quick “important files” map for your presentation
- Routing: `htundla_safaris/urls.py`
- Inquiry + submit flow: `core/views.py` (`contact_us`)
- Validation rules: `core/forms.py`
- Domain models/DB schema: `core/models.py`
- Itinerary algorithm: `core/recommender.py`
- Admin/operator workflow: `core/admin.py`
- Project context/assumptions: `README.md`
