import streamlit as st
from linkedin_api import Linkedin
import io

# Helper function to format dates
def format_date(date):
    return f"{date.get('month', '')}/{date.get('year', '')}" if date else ""

# Create a resume from LinkedIn profile data
def create_resume(profile_data, contact_info):
    # Personal Details
    full_name = f"{profile_data.get('firstName', '')} {profile_data.get('lastName', '')}"
    headline = profile_data.get('headline', 'No headline available')
    location = profile_data.get('locationName', 'Unknown location')
    summary = profile_data.get('summary', 'No summary available')

    # Contact Information
    email = contact_info.get('email_address', 'Not provided')
    github = next((site['url'] for site in contact_info.get('websites', []) if site.get('label') == 'PORTFOLIO'), 'Not provided')

    # Experience Section
    experience_entries = profile_data.get('experience', [])
    experience_str = "\n".join([
        f"{exp.get('title', 'N/A')} at {exp.get('companyName', 'N/A')} ({format_date(exp.get('timePeriod', {}).get('startDate'))} - {format_date(exp.get('timePeriod', {}).get('endDate')) or 'Present'})\n"
        f"Location: {exp.get('locationName', 'N/A')}\n"
        f"Description: {exp.get('description', 'No description available')}\n"
        for exp in experience_entries
    ])

    # Education Section
    education_entries = profile_data.get('education', [])
    education_str = "\n".join([
        f"{edu.get('schoolName', 'Unknown School')} - {edu.get('degreeName', '')} ({format_date(edu.get('timePeriod', {}).get('startDate'))} - {format_date(edu.get('timePeriod', {}).get('endDate'))})\n"
        f"Field of Study: {edu.get('fieldOfStudy', 'N/A')}\n"
        for edu in education_entries
    ])

    # Skills Section
    skills = profile_data.get('skills', [])
    skills_str = ", ".join([skill.get('name') for skill in skills])

    # Certifications Section
    certifications = profile_data.get('certifications', [])
    cert_str = "\n".join([
        f"{cert.get('name', 'Unknown Certification')} by {cert.get('authority', 'Unknown Authority')} ({format_date(cert.get('timePeriod', {}).get('startDate'))})"
        for cert in certifications
    ])

    # Languages Section
    languages = profile_data.get('languages', [])
    languages_str = ", ".join([f"{lang.get('name')} ({lang.get('proficiency')})" for lang in languages])

    # Final Resume Format
    resume = f"""
    {full_name}
    {headline}
    {location}

    Contact Information:
    Email: {email}
    GitHub: {github}

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

# Generate resume when the button is clicked
if st.button('Generate Resume'):
    if linkedin_username and linkedin_password and profile_target:
        try:
            with st.spinner("Fetching LinkedIn profile..."):
                # Authenticate and fetch profile
                api = Linkedin(linkedin_username, linkedin_password)
                profile_data = api.get_profile(profile_target)
                contact_info = api.get_profile_contact_info(profile_target)

            # Create the resume
            resume = create_resume(profile_data, contact_info)
            
            # Display the resume in a text area
            st.text_area("Generated Resume", resume, height=400)

            # Create a buffer to hold the resume data
            with io.StringIO() as resume_buffer:
                resume_buffer.write(resume)
                resume_data = resume_buffer.getvalue()

            # Create a download button for the resume
            st.download_button(
                label="Download Resume as TXT",
                data=resume_data,
                file_name=f"{profile_target}_resume.txt",
                mime="text/plain"
            )

        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter LinkedIn credentials and the target profile username.")
