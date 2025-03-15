from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt  # Add this import
import json
from api.moodle_api import get_moodle_courses
import logging
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

logger = logging.getLogger(__name__)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def fetch_courses(request):
    """Fetch courses from Moodle and return as JSON"""
    logger.info("API call received: fetch_courses")
    
    # Log request information for debugging
    logger.debug(f"Request headers: {request.headers}")
    
    courses = get_moodle_courses()
    
    # Check if there was an error
    if isinstance(courses, dict) and "error" in courses:
        logger.error(f"Error fetching Moodle courses: {courses['error']}")
        return JsonResponse({"error": courses["error"]}, status=500)
    
    logger.info(f"Successfully fetched {len(courses)} courses")
    return JsonResponse(courses, safe=False)

@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def recommend_course(request):
    """Recommend courses based on user preferences"""
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)
    
    try:
        logger.info("API call received: recommend_course")
        data = json.loads(request.body)
        liked_course = data.get("liked_course", "").strip().lower()
        
        logger.info(f"Finding recommendations for course: {liked_course}")
        
        # Get all courses from Moodle
        moodle_courses = get_moodle_courses()
        
        # Check if there was an error fetching courses
        if isinstance(moodle_courses, dict) and "error" in moodle_courses:
            logger.error(f"Error fetching Moodle courses for recommendations: {moodle_courses['error']}")
            return JsonResponse({"error": moodle_courses["error"]}, status=500)
        
        # Log all courses for debugging
        logger.debug(f"All Moodle courses: {moodle_courses}")
        
        # Find the category of the liked course
        liked_course_category = None
        liked_course_obj = None
        
        for course in moodle_courses:
            if (course["shortname"].lower() == liked_course or 
                course["fullname"].lower() == liked_course or 
                str(course["id"]) == liked_course):
                liked_course_category = course.get("categoryid")
                liked_course_obj = course
                break
        
        if not liked_course_obj:
            logger.warning(f"Course not found: {liked_course}")
            return JsonResponse({"error": "Course not found"}, status=404)
            
        # Find other courses in the same category
        recommendations = []
        if liked_course_category:
            for course in moodle_courses:
                if (course["categoryid"] == liked_course_category and 
                    course["id"] != liked_course_obj["id"]):
                    recommendations.append({
                        "id": course["id"],
                        "name": course["fullname"],
                        "shortname": course["shortname"],
                        "summary": course.get("summary", "")
                    })
        
        # If no recommendations in the same category, recommend from all categories
        if not recommendations:
            logger.info("No recommendations found in the same category. Recommending from all categories.")
            for course in moodle_courses:
                if course["id"] != liked_course_obj["id"]:
                    recommendations.append({
                        "id": course["id"],
                        "name": course["fullname"],
                        "shortname": course["shortname"],
                        "summary": course.get("summary", "")
                    })
        
        logger.info(f"Found {len(recommendations)} recommendations")
        return JsonResponse({"recommended_courses": recommendations[:3]}, status=200)
    
    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body")
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"Error in recommendation: {str(e)}")
        return JsonResponse({"error": f"Server error: {str(e)}"}, status=500)