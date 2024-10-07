import streamlit as st
from linkedin_api import Linkedin
from dotenv import load_dotenv
import os
import io

# Load environment variables (if any)
load_dotenv()

# Helper function to format dates
def format_date(date):
    return f"{date.get('month', '')}/{date.get('year', '')}" if date else ""

# Create a resume from LinkedIn profile data
def create_resume(profile_data, contact_info):
    # Personal Details
    full_name = f"{profile_data.get('firstName', '')} {profile_data.get('lastName', '')}"
    headline = profile_data.get('headline', '')
    location = profile_data.get('locationName', 'Unknown')
    summary = profile_data.get('summary', 'No summary available')

    # Contact Information
    email = contact_info.get('email_address', 'Not provided')
    github = next((site.get('url') for site in contact_info.get('websites', []) if site['label'] == 'PORTFOLIO'), 'Not provided')
    portfolio = contact_info.get('websites', [])
    
    # Experience
    experience_entries = profile_data.get('experience', [])
    experience_str = ""
    for exp in experience_entries:
        company = exp.get('companyName', 'N/A')
        title = exp.get('title', 'N/A')
        location = exp.get('locationName', 'N/A')
        start_date = format_date(exp.get('timePeriod', {}).get('startDate', {}))
        end_date = format_date(exp.get('timePeriod', {}).get('endDate', {})) or 'Present'
        description = exp.get('description', 'No description available')
        experience_str += f"{title} at {company} ({start_date} - {end_date})\n"
        experience_str += f"Location: {location}\n"
        experience_str += f"Description: {description}\n\n"

    # Education
    education_entries = profile_data.get('education', [])
    education_str = ""
    for edu in education_entries:
        school = edu.get('schoolName', 'Unknown School')
        field_of_study = edu.get('fieldOfStudy', 'N/A')
        degree = edu.get('degreeName', '')
        start_date = format_date(edu.get('timePeriod', {}).get('startDate', {}))
        end_date = format_date(edu.get('timePeriod', {}).get('endDate', {}))
        education_str += f"{school} - {degree} ({start_date} - {end_date})\n"
        education_str += f"Field of Study: {field_of_study}\n\n"

    # Skills
    skills = profile_data.get('skills', [])
    skills_str = ", ".join([skill.get('name') for skill in skills])

    # Certifications
    certifications = profile_data.get('certifications', [])
    cert_str = ""
    for cert in certifications:
        cert_name = cert.get('name', 'Unknown Certification')
        authority = cert.get('authority', 'Unknown Authority')
        start_date = format_date(cert.get('timePeriod', {}).get('startDate', {}))
        cert_str += f"{cert_name} by {authority} ({start_date})\n"

    # Languages
    languages = profile_data.get('languages', [])
    languages_str = ", ".join([f"{lang.get('name')} ({lang.get('proficiency')})" for lang in languages])

    # Format resume
    resume = f"""
    {full_name}
    {headline}
    {location}

    Contact Information:
    Email: {email}
    GitHub: {github}
    Portfolio: {portfolio}

    Summary:
    {summary}

    Experience:
    {experience_str}

    Education:
    {education_str}

    Skills:
    {skills_str}

    Certifications:
    {cert_str}

    Languages:
    {languages_str}
    """
    
    return resume

# Streamlit app title
st.title('📄 LinkedIn Profile to Resume Generator')

# Sidebar for LinkedIn login credentials
st.sidebar.header("🔑 LinkedIn Login")
linkedin_username = st.sidebar.text_input("Username", placeholder="Enter your LinkedIn username")
linkedin_password = st.sidebar.text_input("Password", type="password", placeholder="Enter your LinkedIn password")

# Input field for target LinkedIn profile in the main content area
st.subheader("Generate a Resume")
profile_target = st.text_input("Target LinkedIn Profile", placeholder="Enter the LinkedIn profile target username")

# Add instructions and generate button
st.info("Enter your LinkedIn credentials in the sidebar and the target LinkedIn profile username to generate a resume.")

if st.button('Generate Resume'):
    if linkedin_username and linkedin_password and profile_target:
        try:
            # Authenticate and fetch profile
            api = Linkedin(linkedin_username, linkedin_password)
            profile_data = api.get_profile(profile_target)
            contact_info = api.get_profile_contact_info(profile_target)

            # Create the resume
            resume = create_resume(profile_data, contact_info)
            
            # Display the resume in a text area
            st.text_area("Generated Resume", resume, height=400)

            # Create a buffer to hold the resume data
            resume_buffer = io.StringIO(resume)
            
            # Create a download button for the resume
            st.download_button(
                label="Download Resume as TXT",
                data=resume_buffer.getvalue(),
                file_name=f"{profile_target}_resume.txt",
                mime="text/plain"
            )

        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter LinkedIn credentials and the target profile username.")
