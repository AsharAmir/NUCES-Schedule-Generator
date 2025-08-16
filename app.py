"""
NUCES FAST University Timetable Parser

A Flask web application that extracts course timetables from Google Sheets
and generates personalized timetables for students at NUCES FAST University.

Author: @AsharAmir
License: MIT
"""

from flask import Flask, render_template, request, jsonify
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import json
import re
import os
from datetime import datetime
import logging

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def get_google_credentials():
    """
    Retrieve Google Sheets API credentials from environment variables.
    
    Returns:
        dict: Google service account credentials
    """
    return {
        "type": os.getenv('GOOGLE_TYPE', 'service_account'),
        "project_id": os.getenv('GOOGLE_PROJECT_ID'),
        "private_key_id": os.getenv('GOOGLE_PRIVATE_KEY_ID'),
        "private_key": os.getenv('GOOGLE_PRIVATE_KEY'),
        "client_email": os.getenv('GOOGLE_CLIENT_EMAIL'),
        "client_id": os.getenv('GOOGLE_CLIENT_ID'),
        "auth_uri": os.getenv('GOOGLE_AUTH_URI'),
        "token_uri": os.getenv('GOOGLE_TOKEN_URI'),
        "auth_provider_x509_cert_url": os.getenv('GOOGLE_AUTH_PROVIDER_X509_CERT_URL'),
        "client_x509_cert_url": os.getenv('GOOGLE_CLIENT_X509_CERT_URL'),
        "universe_domain": os.getenv('GOOGLE_UNIVERSE_DOMAIN', 'googleapis.com')
    }

# Initialize Google Sheets client
def initialize_google_sheets_client():
    """
    Initialize and return Google Sheets client.
    
    Returns:
        gspread.Client: Authorized Google Sheets client
    """
    try:
        credentials_json = get_google_credentials()
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_json, scope)
        return gspread.authorize(creds)
    except Exception as e:
        logger.error(f"Failed to initialize Google Sheets client: {e}")
        raise

client = initialize_google_sheets_client()

# Sheet configurations for different schools
SCHOOLS = {
    'engineering': {
        'name': 'FAST School of Engineering',
        'sheet_id': None, # To be added later
        'calendar_link': 'https://calendar.google.com/calendar/embed?src=engineering%40nu.edu.pk&ctz=Asia%2FKarachi',
        'color': '#667eea'
    },
    'computing': {
        'name': 'FAST School of Computing',
        'sheet_id': '1cmDXt7UTIKBVXBHhtZ0E4qMnJrRoexl2GmDFfTBl0Z4',
        'calendar_link': 'https://calendar.google.com/calendar/embed?src=computing%40nu.edu.pk&ctz=Asia%2FKarachi',
        'color': '#4facfe'
    },
    'management': {
        'name': 'FAST School of Management',
        'sheet_id': None,  # To be added later
        'calendar_link': 'https://calendar.google.com/calendar/embed?src=management%40nu.edu.pk&ctz=Asia%2FKarachi',
        'color': '#764ba2'
    }
}

@app.route('/')
def index():
    return render_template('simple.html')

@app.route('/api/schools')
def get_schools():
    """Get available schools with their details"""
    return jsonify({
        school_id: {
            'name': details['name'],
            'calendar_link': details['calendar_link'],
            'color': details['color'],
            'available': details['sheet_id'] is not None
        }
        for school_id, details in SCHOOLS.items()
    })

@app.route('/api/courses/<school>')
def get_course_suggestions(school):
    """
    Get course suggestions for autocomplete based on school selection.
    
    Args:
        school (str): School identifier (engineering, computing, management)
        
    Returns:
        JSON response with course list and metadata
    """
    logger.info(f"Course suggestions requested for school: {school}")
    
    if school not in SCHOOLS or not SCHOOLS[school]['sheet_id']:
        logger.warning(f"School {school} not available or missing sheet_id")
        return jsonify({'error': 'School not available'}), 400
    
    try:
        sheet = client.open_by_key(SCHOOLS[school]['sheet_id'])
        logger.info(f"Successfully opened sheet: {sheet.title}")
        courses = set()
        
        for worksheet in sheet.worksheets():
            sheet_data = worksheet.get_all_values()
            if len(sheet_data) < 2:
                continue
                
            df = pd.DataFrame(sheet_data[1:], columns=sheet_data[0])
            
            # Extract all course patterns from the sheet
            for _, row in df.iterrows():
                for cell_value in row:
                    if cell_value and isinstance(cell_value, str):
                        cell_value = cell_value.strip()
                        if not cell_value or len(cell_value) < 3:
                            continue
                        
                        # Skip time patterns and common headers
                        if re.match(r'^\d{2}:\d{2}', cell_value) or cell_value in ['Day', 'Time', 'Room']:
                            continue
                            
                        # Pattern 1: Theory courses like "Algo (CS-A)", "Data St (AI-A/C)", "ML (AI, 22)", "S/w Re-Engg (SE-A)"
                        theory_matches = re.findall(r'[A-Za-z\s&/-]+\s*\([A-Z]{1,3}[-/]*[A-Z]*[,-]*\s*\d*\)', cell_value)
                        courses.update(theory_matches)
                        
                        # Pattern 2: Lab courses like "IICT Lab (CS-E)", "Data St Lab (SE-B)"
                        lab_matches = re.findall(r'[A-Za-z\s&/]+Lab\s*\([A-Z]{1,3}[-/]*[A-Z]*[,-]*\s*\d*\)', cell_value)
                        courses.update(lab_matches)
                        
                        # Pattern 3: Special standalone courses like "FSM"
                        if re.match(r'^[A-Z&/\s]{2,15}(\s*\(\d+\))?$', cell_value):
                            courses.add(cell_value)
                        
                        # Pattern 4: Time-specific courses like "Psychology (SE-C) 02:00-03:45"
                        time_specific = re.findall(r'([A-Za-z\s&/]+\s*\([A-Z]{1,3}[-/]*[A-Z]*\))\s+\d{2}:\d{2}-\d{2}:\d{2}', cell_value)
                        courses.update(time_specific)
        
        courses_list = sorted(list(courses))
        logger.info(f"Found {len(courses_list)} courses for {school}")
        
        return jsonify({
            'courses': courses_list,
            'school': SCHOOLS[school]['name'],
            'sheet_id': SCHOOLS[school]['sheet_id'],  # Add for debugging
            'count': len(courses_list)
        })
        
    except Exception as e:
        logger.error(f"Failed to fetch courses for {school}: {str(e)}")
        return jsonify({'error': f'Failed to fetch courses: {str(e)}'}), 500

@app.route('/api/generate', methods=['POST'])
def generate_timetable_api():
    """
    Generate personalized timetable based on selected courses.
    
    Expected JSON payload:
        {
            "courses": ["Course 1 (SECTION)", "Course 2 (SECTION)"],
            "school": "engineering" | "computing" | "management"
        }
        
    Returns:
        JSON response with structured timetable data
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        courses = data.get('courses', [])
        school = data.get('school', 'engineering')
        
        if not courses:
            return jsonify({'error': 'No courses specified'}), 400
            
        logger.info(f"Generating timetable for {len(courses)} courses in {school}")

        if school not in SCHOOLS or not SCHOOLS[school]['sheet_id']:
            return jsonify({'error': 'School not available or not configured'}), 400

        sheet = client.open_by_key(SCHOOLS[school]['sheet_id'])
        timetable_data = []
        
    except Exception as e:
        logger.error(f"Error in timetable generation setup: {str(e)}")
        return jsonify({'error': 'Invalid request data'}), 400

    def parse_worksheet(sheet_data, sheet_name):
        """
        Parse a single worksheet to extract course information.
        
        Args:
            sheet_data: Raw sheet data from Google Sheets
            sheet_name: Name of the worksheet (day of week)
        """
        if len(sheet_data) < 2:
            logger.debug(f"Sheet '{sheet_name}' has insufficient data, skipping")
            return
            
        try:
            df = pd.DataFrame(sheet_data[1:], columns=sheet_data[0])
            time_row_index = min(3, len(df) - 1)

            for i, row in df.iterrows():
                for col in df.columns:
                    try:
                        for course in courses:
                            cell_val = row[col]
                            
                            # Convert cell value to string safely
                            if hasattr(cell_val, 'iloc') or hasattr(cell_val, '__array__'):
                                cell_value = str(cell_val.iloc[0] if hasattr(cell_val, 'iloc') else cell_val[0])
                            else:
                                cell_value = str(cell_val) if cell_val is not None else ""
                            
                            # Clean up empty/null strings
                            if not cell_value or cell_value.lower() in ['nan', 'none', 'null']:
                                cell_value = ""
                            
                            # Check if course is found in this cell
                            if course and course in cell_value:
                                c_idx = df.columns.get_loc(col)
                                
                                if time_row_index < len(df) and c_idx < len(df.columns):
                                    time_val = df.iloc[time_row_index, c_idx]
                                    time = str(time_val) if pd.notna(time_val) else "N/A"
                                    
                                    room_val = df.iloc[i, 0] if len(df.columns) > 0 else "N/A"
                                    room = str(room_val) if pd.notna(room_val) else "N/A"
                                    
                                    entry = {
                                        'day': sheet_name,
                                        'time': time,
                                        'room': room,
                                        'course': course
                                    }
                                    timetable_data.append(entry)
                                    logger.debug(f"Found {course} on {sheet_name} at {time}")
                                    
                    except Exception as cell_error:
                        logger.debug(f"Error processing cell [{i}][{col}]: {str(cell_error)}")
                        continue
                        
        except Exception as sheet_error:
            logger.error(f"Error parsing sheet '{sheet_name}': {str(sheet_error)}")
            raise

    try:
        print(f"DEBUG: Starting to process worksheets for school: {school}")
        print(f"DEBUG: Courses to search for: {courses}")
        
        worksheets = sheet.worksheets()
        print(f"DEBUG: Found {len(worksheets)} worksheets")
        
        for worksheet in worksheets:
            sheetName = worksheet.title
            print(f"DEBUG: Processing worksheet: '{sheetName}'")
            
            sheetData = worksheet.get_all_values()
            print(f"DEBUG: Retrieved {len(sheetData)} rows from '{sheetName}'")
            
            parse(sheetData, sheetName)
            print(f"DEBUG: Finished parsing '{sheetName}', current timetable_data length: {len(timetable_data)}")
            
    except Exception as e:
        print(f"DEBUG: Exception in worksheet processing: {str(e)}")
        print(f"DEBUG: Exception type: {type(e)}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Error accessing sheet: {str(e)}'}), 500

    print(f"DEBUG: Final timetable_data length: {len(timetable_data)}")
    if timetable_data:
        print(f"DEBUG: Sample timetable entries: {timetable_data[:3]}")
    
    if not timetable_data:
        print("DEBUG: No timetable data found")
        return jsonify({'error': 'No matching courses found'}), 404

    # Create structured timetable for display
    print("DEBUG: Creating DataFrame from timetable_data")
    try:
        df = pd.DataFrame(timetable_data)
        print(f"DEBUG: DataFrame created with shape: {df.shape}")
        print(f"DEBUG: DataFrame columns: {list(df.columns)}")
        
        # Add validation for required columns
        required_cols = ['day', 'time', 'course']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if df.empty or missing_cols:
            print(f"DEBUG: DataFrame validation failed - missing columns: {missing_cols}")
            return jsonify({'error': f'Invalid timetable data structure - missing: {missing_cols}'}), 500
        
        print("DEBUG: Creating pivot table")
        pivot_table = df.pivot_table(
            index="day",
            columns="time",
            values="course",
            aggfunc=lambda x: '<br>'.join(str(i) for i in x),
            fill_value=""
        )
        print(f"DEBUG: Pivot table created with shape: {pivot_table.shape}")
        
    except Exception as pivot_error:
        print(f"DEBUG: Error creating pivot table: {str(pivot_error)}")
        print(f"DEBUG: Pivot error type: {type(pivot_error)}")
        import traceback
        print(f"DEBUG: Pivot traceback: {traceback.format_exc()}")
        raise

    # Convert to dictionary for JSON response
    timetable_dict = {}
    time_slots = sorted(pivot_table.columns.tolist())
    days = pivot_table.index.tolist()

    for day in days:
        timetable_dict[day] = {}
        for time in time_slots:
            try:
                value = pivot_table.at[day, time]
                timetable_dict[day][time] = str(value) if pd.notna(value) else ""
            except (KeyError, IndexError):
                timetable_dict[day][time] = ""

    return jsonify({
        'success': True,
        'timetable': timetable_dict,
        'time_slots': time_slots,
        'days': days,
        'courses': courses,
        'school': SCHOOLS[school]['name'],
        'school_color': SCHOOLS[school]['color'],
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })


if __name__ == '__main__':
    app.run(debug=True)
