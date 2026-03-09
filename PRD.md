# Product Requirement Document (PRD): Link Analytics Shortener

## 1. Objective
To build a lightweight, fast, and reliable URL shortener that tracks link usage and persists data across sessions.

## 2. Implementation Approach
* **Frontend/Framework:** Streamlit (Python). Chosen for its rapid UI generation and built-in state management.
* **Data Persistence:** SQLite3. A serverless, file-based relational database that perfectly handles persistent storage of URLs and click counts without external dependencies.
* **Routing/Redirection Mechanism:** Utilized Streamlit's `st.query_params` to detect short IDs in the URL. When detected, the application queries the database, increments the click counter, and executes an HTML `<meta http-equiv="refresh">` tag to seamlessly redirect the user to the original destination.

## 3. Core Features Executed
* **URL Shortening:** Generates a unique 6-character alphanumeric ID for valid URLs.
* **Redirection:** Captures the `id` query parameter and routes to the original URL.
* **Click Tracking:** Database atomically updates the click integer upon routing.
* **Dashboard:** Real-time Pandas dataframe querying the SQLite database to display the Original URL, Short ID, and Total Clicks.
* **Validation:** Enforces `http://` or `https://` prefixes to prevent dead routing.