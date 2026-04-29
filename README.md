# Automated Tour Recommendation System for Htundla Safaris

A web-based tour recommendation system developed for **Htundla Safaris** as a final year project. The system is designed to help tourists explore safari and MICE travel options in Kenya through a guided chatbot that collects travel preferences and generates a draft itinerary. A human tour operator then reviews the itinerary, prepares the final cost sheet, and sends the final proposal to the customer by email.

## Project Purpose

Many tour companies still rely on static websites, WhatsApp messages, phone calls, and email exchanges to collect travel requirements and prepare itineraries manually. This slows down response time, makes personalization difficult, and increases the workload on tour operators.

This project addresses that problem by introducing a simple, workable, and demo-friendly system that:

- collects customer preferences through a guided chatbot
- validates the submitted information
- generates a draft itinerary automatically using rule-based recommendation logic
- allows a human tour operator to review and finalize the proposal
- supports structured and centralized handling of inquiries

## Project Scope

This system focuses on:

- **Safari tours**
- **MICE travel** (Meetings, Incentives, Conferences, and Exhibitions)

The system supports a **minimum of 3 days** and a **maximum of 5 days** for safari itinerary generation, excluding arrival and departure days.

## Design Principle

This project follows the **KISS principle**:

> **Keep It Simple**

The goal is not to build an industry-grade commercial product. The goal is to build a system that is:

- functional
- clear
- easy to explain
- easy to demonstrate
- realistic for an undergraduate final year project

## Key Features

### Customer Side
- Homepage with project/company introduction
- Destinations page showing supported destinations
- Contact page with guided chatbot
- Step-by-step collection of travel preferences
- Frontend validation of chatbot inputs
- Draft itinerary generation after successful submission

### Backend / System Side
- Django-powered backend logic
- Backend validation of all submitted chatbot data
- Storage of inquiries, destinations, activities, itineraries, and operator responses
- Rule-based recommendation module for itinerary generation
- Centralized operator view/admin area for reviewing inquiries
- Human-in-the-loop proposal finalization
- Email-based proposal delivery

### Operator Side
- View inquiries collected from the chatbot
- View generated draft itineraries
- Edit/refine itinerary if necessary
- Add final cost sheet
- Add proposal notes
- Mark proposal as finalized/sent

## Recommendation Logic

The system uses a **rule-based automated recommendation approach**, not heavy machine learning.

The recommendation module generates draft itineraries by matching:

- travel type
- preferred destination
- travel style
- group size
- selected interests

Activities are further filtered and ordered using structured metadata such as:

- **time slot**: Morning, Afternoon, Evening, Full-day, Flexible
- **day suitability**: Arrival, Mid-trip, Departure, Any
- **intensity level**: Light, Moderate, Heavy
- **duration type**: Short, Half-day, Full-day, Multi-day

This allows the system to avoid unrealistic scheduling, such as placing an evening-only activity in the morning.

## Human-in-the-Loop Design

The system intentionally includes a human tour operator in the workflow.

This is important because travel planning in safari and MICE contexts involves real-world operational constraints that cannot always be fully captured in a database, including:

- vehicle availability
- lodge capacity
- seasonal access
- changing prices
- venue availability
- operator-specific business decisions

For that reason, the system generates a **draft itinerary**, while the **final cost and final proposal remain the responsibility of the tour operator**.

## Technology Stack

### Frontend
- HTML
- CSS
- JavaScript

### Backend
- Python
- Django

### Database
- SQLite (development)
- MySQL (optional / production-ready direction)

### Other Tools
- Django Admin (for centralized operator-side management)
- Email backend in Django
- Git / GitHub for version control

## Current Frontend Pages

The current frontend includes:

- `index.html` — Homepage
- `destinations.html` — Destinations page
- `contactus.html` — Contact page with chatbot integration point

## Planned / Core Workflow

1. User visits the website
2. User opens the contact page
3. User interacts with the chatbot
4. Chatbot collects:
   - full name
   - email address
   - phone number
   - travel type
   - preferred destination
   - duration
   - travel style
   - group size
   - interests
5. Frontend validates the input in real time
6. Data is submitted to Django backend
7. Django performs backend validation
8. Valid inquiry is stored in the database
9. The recommendation module generates a draft itinerary
10. Operator accesses the inquiry and generated itinerary in a centralized backend/admin view
11. Operator edits or confirms the itinerary
12. Operator adds final cost and proposal notes
13. Final proposal is sent to the customer by email

## Supported Destinations

The project dataset is built around 10 destination groups:

1. Nairobi
2. Maasai Mara
3. Amboseli
4. Lake Nakuru
5. Mount Kenya / Nanyuki
6. Lake Naivasha & Hell’s Gate
7. Samburu
8. Tsavo
9. Laikipia / Ol Pejeta
10. Kenyan Coast

## Supported Experience Categories

The system supports itinerary generation around activities such as:

- Local Cuisines
- Site Seeing
- Animal Spotting
- Mountain Hiking
- Photo Sites
- Camping Sites
- Snorkelling
- Culture Immersion
- Hot Air Balloon Safaris
- Bird Spotting
- Nature Walks

## Travel Styles

Instead of asking users for direct budget values, the system uses:

- **Budget-friendly**
- **Standard**
- **Luxury**

This keeps the interface simple while still helping the system recommend suitable activities. Final pricing is handled manually by the operator.

## System Validation

### Frontend Validation
The chatbot validates user input in real time to improve usability.

Examples:
- numeric checks for duration and group size
- email format check
- controlled options for travel type and travel style

### Backend Validation
Django validates all submitted data again before storing it in the database.

This ensures:
- data integrity
- protection against malformed submissions
- protection against bypassing frontend validation

## Database Overview

The core entities in the system are:

- `USER`
- `INQUIRY`
- `DESTINATION`
- `ACTIVITY`
- `ITINERARY`
- `ITINERARY_ITEM`
- `OPERATOR`
- `OPERATOR_RESPONSE`

These support:
- user inquiry handling
- destination and activity management
- draft itinerary generation
- operator review and response handling

## Project Structure

A typical structure for this project is expected to look like this:

```bash
project-root/
│
├── manage.py
├── README.md
├── requirements.txt
│
├── project_name/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── app_name/
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── migrations/
│   └── templates/
│       ├── index.html
│       ├── destinations.html
│       └── contactus.html
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
└── media/