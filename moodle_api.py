import requests
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Moodle connection details
MOODLE_URL = "https://destiny-platform.moodlecloud.com"
MOODLE_TOKEN = "2e3a870bef21779c430a1b0627725e4f"  # Your token from earlier

def get_moodle_courses():
    """Fetch courses from Moodle API with proper error handling"""
    endpoint = f"{MOODLE_URL}/webservice/rest/server.php"
    params = {
        "wstoken": MOODLE_TOKEN,
        "wsfunction": "core_course_get_courses",
        "moodlewsrestformat": "json"
    }
    
    try:
        logger.info(f"Connecting to Moodle API at {MOODLE_URL}")
        response = requests.get(endpoint, params=params)
        
        # Check for HTTP errors
        response.raise_for_status()
        
        # Parse response
        data = response.json()
        
        # Check for Moodle API errors
        if isinstance(data, dict) and "exception" in data:
            logger.error(f"Moodle API error: {data.get('message', 'Unknown error')}")
            return {"error": data.get('message', 'Unknown error')}
        
        logger.info(f"Successfully retrieved {len(data)} courses from Moodle")
        return data
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error: {e}")
        return {"error": f"HTTP Error: {str(e)}"}
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection Error: {e}")
        return {"error": f"Connection Error: {str(e)}"}
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout Error: {e}")
        return {"error": f"Timeout Error: {str(e)}"}
    except requests.exceptions.RequestException as e:
        logger.error(f"Request Exception: {e}")
        return {"error": f"Request Exception: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"error": f"Unexpected error: {str(e)}"}