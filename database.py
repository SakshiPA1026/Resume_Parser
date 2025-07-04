import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# --- Firestore Initialization ---
# This part handles Firebase initialization.
# It first tries to use Application Default Credentials (standard for Google Cloud environments).
# If that fails (e.g., in local development without GOOGLE_APPLICATION_CREDENTIALS set),
# it falls back to looking for a JSON string in the FIREBASE_CREDENTIALS_JSON environment variable.

if not firebase_admin._apps:
    try:
        # Attempt to load credentials from GOOGLE_APPLICATION_CREDENTIALS environment variable
        # This is the standard way for Google Cloud services or local setup
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred)
        print("Firebase Admin SDK initialized using Application Default Credentials.")
    except Exception as e:
        print(f"Warning: Could not initialize Firebase with Application Default Credentials: {e}")
        # Fallback for local development or Render if using a direct JSON string env var
        try:
            firebase_credentials_json = os.environ.get('FIREBASE_CREDENTIALS_JSON')
            if firebase_credentials_json:
                # Load credentials from the environment variable (JSON string)
                cred = credentials.Certificate(json.loads(firebase_credentials_json))
                firebase_admin.initialize_app(cred)
                print("Firebase Admin SDK initialized using FIREBASE_CREDENTIALS_JSON environment variable.")
            else:
                # If neither method works, raise an error
                raise Exception("Firebase credentials not found. Please set GOOGLE_APPLICATION_CREDENTIALS or FIREBASE_CREDENTIALS_JSON environment variable.")
        except Exception as e_fallback:
            print(f"Error: Failed to initialize Firebase Admin SDK: {e_fallback}")
            print("Please ensure your Firebase service account key is correctly configured.")
            raise e_fallback # Re-raise the exception to stop the app if init fails

db = firestore.client()
print("Firestore client initialized.")

# --- Database Operations ---

def insert_resume_data(data, original_filename=None):
    """
    Inserts parsed resume data into Firestore.

    Args:
        data (dict): A dictionary containing parsed resume details.
        original_filename (str, optional): The filename of the uploaded resume.
    Returns:
        str: The ID of the newly inserted document.
    """
    try:
        # Create a new document in the 'resumes' collection
        doc_ref = db.collection('resumes').document()
        
        # Firestore can directly store Python dicts and lists, no need for json.dumps
        resume_doc = {
            'name': data.get('name', ''),
            'email': data.get('email', ''),
            'phone': data.get('phone', ''),
            'skills': data.get('skills', []),
            'education': data.get('education', []),
            'work_experience': data.get('work_experience', []),
            'original_filename': original_filename,
            'timestamp': firestore.SERVER_TIMESTAMP # Add a server timestamp for ordering
        }
        
        doc_ref.set(resume_doc)
        print(f"Firestore: Data saved with ID: {doc_ref.id}")
        return doc_ref.id
    except Exception as e:
        print(f"Firestore Error: Failed to insert data: {e}")
        raise

def get_all_resumes():
    """
    Fetches all resume data from Firestore, ordered by timestamp.
    Returns:
        list: A list of dictionaries, each representing a resume.
    """
    try:
        resumes_ref = db.collection('resumes')
        # Order by timestamp in descending order (latest first)
        docs = resumes_ref.order_by('timestamp', direction=firestore.Query.DESCENDING).stream() 
        
        all_resumes = []
        for doc in docs:
            resume_data = doc.to_dict()
            resume_data['id'] = doc.id # Add the document ID to the data
            all_resumes.append(resume_data)
        print(f"Firestore: Fetched {len(all_resumes)} resumes.")
        return all_resumes
    except Exception as e:
        print(f"Firestore Error: Failed to fetch all resumes: {e}")
        return []

def get_resume_by_id(resume_id):
    """
    Fetches a single resume by its ID from Firestore.
    Args:
        resume_id (str): The ID of the resume document.
    Returns:
        dict: The resume data, or None if not found.
    """
    try:
        doc_ref = db.collection('resumes').document(resume_id)
        doc = doc_ref.get()
        if doc.exists:
            resume_data = doc.to_dict()
            resume_data['id'] = doc.id # Add the document ID
            print(f"Firestore: Fetched resume with ID: {resume_id}")
            return resume_data
        else:
            print(f"Firestore: Resume with ID {resume_id} not found.")
            return None
    except Exception as e:
        print(f"Firestore Error: Failed to fetch resume by ID {resume_id}: {e}")
        return None

def delete_resume_data(resume_id):
    """
    Deletes a resume document from Firestore by its ID.
    Args:
        resume_id (str): The ID of the resume document to delete.
    """
    try:
        db.collection('resumes').document(resume_id).delete()
        print(f"Firestore: Resume with ID {resume_id} deleted successfully.")
    except Exception as e:
        print(f"Firestore Error: Failed to delete resume with ID {resume_id}: {e}")
        raise

# No explicit init_db() call here, as Firebase initialization happens on import
# The `db` client is ready to be used by `app.py`
