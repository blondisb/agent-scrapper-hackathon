Okay, here is a `README.md` file explaining how to execute the provided Python code.

---

# Modern Slavery Statement Scraper & Analyzer API

This project provides a FastAPI-based web API to search for companies and retrieve/analyze their Modern Slavery Statements from various national registers (Australia, UK, Canada). It automates the process of finding company identifiers, locating statements, downloading associated PDFs, and using an LLM agent to summarize the findings.

## Features

- Search for companies in Australia (ABN), UK (Company Number), and Canada.
- Automatically find and download Modern Slavery Statement PDFs.
- Use an LLM agent (`smolagents`) to analyze and summarize the statements.
- Caching mechanism to avoid re-processing.
- Includes a generic webpage content analyzer (`/scrapperagent`).
- Built with FastAPI for easy API access.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- **Python 3.8+**: The code is written in Python.
- **pip**: Python package installer.
- **API Key for LiteLLM Model**: Specifically for `gemini/gemini-2.0-flash` (or a compatible model) from Google AI. (Set as `GEMINI_API_KEY` in environment variables).
- **Internet Access**: To reach external websites and APIs.
- **Write Permissions**: For `/tmp` directories (`/tmp/au`, `/tmp/uk`, `/tmp/ca`) or wherever `BASE_PATH_*` directories are configured.

## Installation

1.  **Clone the Repository:**

    ```bash
    git clone <repository_url> # Replace with your actual repo URL if applicable
    cd <project_directory>
    ```

2.  **Create a Virtual Environment (Recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

    FOR DOCKER:
    docker build -t app-10k-reports-ai .



3.  **Install Dependencies:**

    Create a `requirements.txt` file (based on imports) or install packages directly:

    ```bash
    pip install fastapi uvicorn httpx lxml python-dotenv smolagents
    # If using Ollama (optional model), ensure ollama is running and the model is pulled.
    ```

    ALREADY IN DOCKERFILE


4.  **Set Up Environment Variables:**

    FOR DOCKER: In running

    Create a `.env` file in the project root directory and add the following variables:

    ```env
    # Port for the FastAPI server (default is 8080)
    PORT=8080

    # Base URL prefix for API endpoints (default is /outslavery)
    BASE_URL=/outslavery

    # URLs for external services (defaults provided, usually fine)
    AU_COMPANIES_ID=https://abr.business.gov.au/Search/ResultsActive
    AU_STATEMENTS_URL=https://modernslaveryregister.gov.au
    UK_COMPANIES_ID=https://find-and-update.company-information.service.gov.uk/search/companies
    UK_STATEMENTS_URL=https://modern-slavery-statement-registry.service.gov.uk
    CA_BASE_URL=https://www.publicsafety.gc.ca/cnt/rsrcs/lbrr/ctlg
    CA_FINDER_URL=/rslts-en.aspx?l=2,3,7&a=

    # API Key for the LiteLLM model (e.g., Gemini)
    GEMINI_API_KEY=YOUR_GOOGLE_AI_STUDIO_API_KEY_HERE

    # Optional: If using a local Ollama model instead
    # OLLAMA_API_BASE=http://localhost:11434 # (if needed by smolagents)
    ```

    **Important:** Replace `YOUR_GOOGLE_AI_STUDIO_API_KEY_HERE` with your actual API key from Google AI Studio.

## Running the Application
    FOR DOCKER:
    docker run -d -p 8080:8080 -e GEMINI_API_KEY="zzz" --add-host host.docker.internal:host-gateway --name reports10k-container app-10k-reports-ai

1.  Ensure your virtual environment is activated (if you created one).
2.  Navigate to the project directory.
3.  Run the application using Uvicorn:

    ```bash
    python main.py
    ```
    Or, if you prefer to run it directly with uvicorn:
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8080
    ```
    *(Adjust `--port` if you changed the `PORT` in `.env`)*

4.  The API should now be running. You can access the interactive API documentation (Swagger UI) at `http://localhost:8080/docs` (or your configured host/port).

## API Endpoints

The base URL prefix is defined by the `BASE_URL` environment variable (default `/outslavery`).

### 1. Search Australian Companies

- **URL:** `GET /outslavery/AUcompanies/search`
- **Query Parameters:**
  - `company` (string, required, min length 2): The name of the company to search for.
- **Description:** Searches the Australian Business Register (ABR) for active companies matching the name and returns potential matches with their ABNs.
- **Example:** `http://localhost:8080/outslavery/AUcompanies/search?company=Department%20of%20Innovation`

### 2. Get Australian Modern Slavery Statements

- **URL:** `GET /outslavery/AUcompanies/statements`
- **Query Parameters:**
  - `abn` (string, required): The Australian Business Number (ABN) of the company.
- **Description:** Finds the Modern Slavery Statement for the given ABN, downloads associated PDFs, analyzes them with an LLM agent, and returns a summary. Results are cached.
- **Example:** `http://localhost:8080/outslavery/AUcompanies/statements?abn=12345678901`

### 3. Search UK Companies

- **URL:** `GET /outslavery/UKcompanies/search`
- **Query Parameters:**
  - `company` (string, required, min length 2): The name of the company to search for.
- **Description:** Searches the UK Companies House register for companies matching the name and returns potential matches with their Company Numbers.
- **Example:** `http://localhost:8080/outslavery/UKcompanies/search?company=Innovation%20Ltd`

### 4. Get UK Modern Slavery Statements

- **URL:** `GET /outslavery/UKstatements`
- **Query Parameters:**
  - `id_company` (string, required): The Company Number from Companies House.
- **Description:** Finds the Modern Slavery Statement for the given Company Number, downloads associated PDFs, analyzes them with an LLM agent, and returns a summary. Results are cached.
- **Example:** `http://localhost:8080/outslavery/UKstatements?id_company=12345678`

### 5. Search Canadian Modern Slavery Statements

- **URL:** `GET /outslavery/CAstatements`
- **Query Parameters:**
  - `company_name` (string, required, min length 2): The name of the company to search for.
- **Description:** Searches the Public Safety Canada Library for statements related to the company name, downloads associated PDFs, analyzes them with an LLM agent, and returns a summary. Results are cached.
- **Example:** `http://localhost:8080/outslavery/CAstatements?company_name=3M%20Canada`

### 6. Generic Webpage Content Analyzer (Scrapper Agent)

- **URL:** `GET /outslavery/scrapperagent`
- **Query Parameters:**
  - `company` (string, required, min length 2): The name of the company or website.
  - `country` (string, required, min length 2): The country context (e.g., AU, UK, CA).
- **Description:** Attempts to find the official website for the company/country combination and extracts/analyzes the main webpage content using an LLM agent.
- **Example:** `http://localhost:8080/outslavery/scrapperagent?company=Toyota&country=CA`

### 7. Delete Temporary Folders

- **URL:** `DELETE /outslavery/deletefolder`
- **Query Parameters:**
  - `folder_name` (string, optional, default '.'): **(Caution!)** The name of the folder to delete within the current working directory. Defaults to the current directory (`.`). This endpoint deletes folders.
- **Description:** Allows deletion of temporary folders used for caching (e.g., `/tmp/au`, `/tmp/uk`, `/tmp/ca`) or other folders. **Use with extreme caution.**
- **Example:** `curl -X DELETE "http://localhost:8080/outslavery/deletefolder?folder_name=/tmp/au"`

## How It Works (Simplified Flow)

1.  **Search:** User provides a company name.
2.  **Lookup:** The API queries the relevant national register (ABR, Companies House, Public Safety Canada) to find a unique identifier (ABN, Company Number, or matching entry).
3.  **Statement Retrieval:** Using the identifier/name, the API searches the specific Modern Slavery Statement registry.
4.  **PDF Download:** It identifies and downloads the statement PDFs to a temporary folder (`/tmp/{country}/{identifier}/pdf`).
5.  **LLM Analysis:** The `main_agents` function is called, which likely uses the `LiteLLMModel` to read the PDFs and generate a summary, saved to `/tmp/{country}/{identifier}/summary.txt`.
6.  **Cache:** If the `summary.txt` already exists, it's returned directly without re-downloading/analyzing.
7.  **Response:** The summary or search results are returned as JSON.

## Notes

- The application uses `/tmp` directories for storing downloaded files and summaries. Ensure sufficient space and permissions.
- The LLM processing (`main_agents`) is the core analysis part; its specific implementation details are in `utils_folder` and `services_agents`.
- Error handling is done via `HTTPException` and custom logging (`log_normal`).
- The `smolagents` library is used for the LLM interaction. Ensure it's correctly configured for your chosen model (Gemini or Ollama).

---