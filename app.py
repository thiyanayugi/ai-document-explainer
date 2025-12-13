"""
AI Document Explainer - Production-ready Streamlit Application

This application allows users to upload official documents (PDFs or images),
extracts text using PyMuPDF and Tesseract OCR, and analyzes them using OpenAI's
Chat API to provide clear explanations, deadlines, obligations, risks, and action items.
"""

import os
import io
import json
import streamlit as st
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
from openai import OpenAI
from datetime import datetime
from database.models import (
    init_database, 
    save_analysis, 
    get_all_analyses, 
    delete_all_analyses
)

# Page configuration
st.set_page_config(
    page_title="AI Document Explainer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
MAX_FILE_SIZE_MB = 20
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_EXTENSIONS = ['pdf', 'png', 'jpg', 'jpeg', 'tiff']
OCR_LANGUAGES = 'eng+deu'  # English + German


def init_session_state():
    """Initialize Streamlit session state variables."""
    if 'db_initialized' not in st.session_state:
        engine, Session = init_database()
        st.session_state.engine = engine
        st.session_state.Session = Session
        st.session_state.db_initialized = True


def validate_file(uploaded_file):
    """
    Validate uploaded file for size and type.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if uploaded_file is None:
        return False, "No file uploaded"
    
    # Check file size
    if uploaded_file.size > MAX_FILE_SIZE_BYTES:
        return False, f"File size exceeds {MAX_FILE_SIZE_MB} MB limit"
    
    # Check file extension
    file_extension = uploaded_file.name.split('.')[-1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
    
    return True, None


def extract_text_from_pdf(pdf_bytes):
    """
    Extract text from PDF using PyMuPDF with OCR fallback for scanned pages.
    
    Args:
        pdf_bytes: PDF file content as bytes
        
    Returns:
        str: Extracted text from all pages
    """
    extracted_text = []
    
    try:
        # Open PDF with PyMuPDF
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            
            # Try to extract text directly
            text = page.get_text()
            
            # If page has no selectable text, use OCR
            if not text.strip():
                st.info(f"Page {page_num + 1} has no selectable text. Applying OCR...")
                
                # Convert page to image
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better OCR
                img_bytes = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_bytes))
                
                # Apply OCR
                text = pytesseract.image_to_string(img, lang=OCR_LANGUAGES)
            
            extracted_text.append(text)
        
        pdf_document.close()
        
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return ""
    
    return "\n\n".join(extracted_text)


def extract_text_from_image(image_bytes):
    """
    Extract text from image using Tesseract OCR.
    
    Args:
        image_bytes: Image file content as bytes
        
    Returns:
        str: Extracted text
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(img, lang=OCR_LANGUAGES)
        return text
    except Exception as e:
        st.error(f"Error extracting text from image: {str(e)}")
        return ""


def analyze_document_with_llm(text, api_key):
    """
    Analyze document text using OpenAI Chat API with strict JSON output.
    
    Args:
        text: Extracted document text
        api_key: OpenAI API key
        
    Returns:
        dict: Analysis results or None if failed
    """
    if not text.strip():
        st.error("No text to analyze")
        return None
    
    try:
        client = OpenAI(api_key=api_key)
        
        system_prompt = """You are a professional document analyst. Your task is to analyze official documents and provide clear, actionable insights.

CRITICAL: You must respond with ONLY valid JSON. Do not include any text before or after the JSON.

Rules:
- Do NOT invent facts or information not present in the document
- If information is unclear or not mentioned, use "unknown" or "not specified"
- Keep explanations concise and avoid legal jargon
- Focus on what matters to the document recipient"""

        user_prompt = f"""Analyze the following document and provide a structured analysis in JSON format.

Document text:
{text[:8000]}  

Return ONLY a valid JSON object with this exact structure:
{{
  "summary": "Brief summary of the document in 2-3 sentences",
  "important_points": ["key point 1", "key point 2", ...],
  "deadlines": ["deadline 1 with date if available", ...],
  "obligations": ["what the recipient must do", ...],
  "risks": ["potential risks or consequences", ...],
  "recommended_next_steps": ["recommended action 1", ...],
  "action_items": ["specific actionable item 1", ...],
  "confidence": "high/medium/low - your confidence in this analysis"
}}"""

        # First attempt
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        result_text = response.choices[0].message.content
        
        # Parse JSON
        try:
            result = json.loads(result_text)
            
            # Validate required fields
            required_fields = [
                'summary', 'important_points', 'deadlines', 'obligations',
                'risks', 'recommended_next_steps', 'action_items', 'confidence'
            ]
            
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")
            
            return result
            
        except json.JSONDecodeError as e:
            st.warning("Invalid JSON received. Retrying...")
            
            # Retry once
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            
            return result
    
    except Exception as e:
        st.error(f"Error analyzing document: {str(e)}")
        return None


def display_analysis(analysis):
    """
    Display analysis results in a structured format.
    
    Args:
        analysis: Dictionary containing analysis results
    """
    st.success("✅ Analysis Complete!")
    
    # Summary
    st.subheader("📋 Summary")
    st.write(analysis.get('summary', 'No summary available'))
    
    # Create two columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        # Important Points
        st.subheader("💡 Important Points")
        points = analysis.get('important_points', [])
        if points:
            for point in points:
                st.markdown(f"- {point}")
        else:
            st.write("No important points identified")
        
        # Deadlines
        st.subheader("⏰ Deadlines")
        deadlines = analysis.get('deadlines', [])
        if deadlines:
            for deadline in deadlines:
                st.markdown(f"- {deadline}")
        else:
            st.write("No deadlines identified")
        
        # Obligations
        st.subheader("📌 Your Obligations")
        obligations = analysis.get('obligations', [])
        if obligations:
            for obligation in obligations:
                st.markdown(f"- {obligation}")
        else:
            st.write("No obligations identified")
    
    with col2:
        # Risks
        st.subheader("⚠️ Potential Risks")
        risks = analysis.get('risks', [])
        if risks:
            for risk in risks:
                st.markdown(f"- {risk}")
        else:
            st.write("No risks identified")
        
        # Recommended Next Steps
        st.subheader("🎯 Recommended Next Steps")
        next_steps = analysis.get('recommended_next_steps', [])
        if next_steps:
            for step in next_steps:
                st.markdown(f"- {step}")
        else:
            st.write("No recommendations available")
        
        # Action Items
        st.subheader("✅ Action Checklist")
        action_items = analysis.get('action_items', [])
        if action_items:
            for item in action_items:
                st.checkbox(item, key=f"action_{hash(item)}")
        else:
            st.write("No action items identified")
    
    # Confidence indicator
    confidence = analysis.get('confidence', 'unknown')
    confidence_color = {
        'high': '🟢',
        'medium': '🟡',
        'low': '🔴'
    }.get(confidence.lower(), '⚪')
    
    st.info(f"{confidence_color} **Analysis Confidence:** {confidence.capitalize()}")


def main():
    """Main application function."""
    
    # Initialize database
    init_session_state()
    
    # Header
    st.title("📄 AI Document Explainer")
    st.markdown("Upload official documents and get clear explanations, deadlines, and action items.")
    
    # Privacy disclaimer
    with st.expander("🔒 Privacy & Security Information", expanded=False):
        st.warning("""
        **Important Privacy Information:**
        
        - Your document text will be sent to OpenAI's API for analysis
        - We do not log or store the raw document content
        - Only the AI-generated summary and analysis are saved to the database
        - You can delete your analysis history at any time
        - Please do not upload documents containing highly sensitive personal information
        
        By uploading a document, you acknowledge and accept these terms.
        """)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
        api_key = os.getenv('OPENAI_API_KEY', '')
        
        if not api_key:
            api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                help="Enter your OpenAI API key. Set OPENAI_API_KEY environment variable to avoid entering it each time."
            )
        else:
            st.success("✅ API Key loaded from environment")
        
        st.divider()
        
        # History section
        st.header("📚 Analysis History")
        
        session = st.session_state.Session()
        analyses = get_all_analyses(session)
        
        if analyses:
            st.write(f"Total analyses: {len(analyses)}")
            
            if st.button("🗑️ Delete All History", type="secondary"):
                count = delete_all_analyses(session)
                st.success(f"Deleted {count} records")
                st.rerun()
        else:
            st.write("No analysis history yet")
        
        session.close()
    
    # Main content
    if not api_key:
        st.error("⚠️ Please provide an OpenAI API key to continue")
        st.stop()
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload a document (PDF or Image)",
        type=ALLOWED_EXTENSIONS,
        help=f"Maximum file size: {MAX_FILE_SIZE_MB} MB"
    )
    
    if uploaded_file:
        # Validate file
        is_valid, error_message = validate_file(uploaded_file)
        
        if not is_valid:
            st.error(f"❌ {error_message}")
            st.stop()
        
        # Display file info
        st.info(f"📎 **File:** {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")
        
        # Process button
        if st.button("🚀 Analyze Document", type="primary"):
            with st.spinner("Processing document..."):
                
                # Extract text based on file type
                file_extension = uploaded_file.name.split('.')[-1].lower()
                file_bytes = uploaded_file.read()
                
                if file_extension == 'pdf':
                    st.info("📖 Extracting text from PDF...")
                    extracted_text = extract_text_from_pdf(file_bytes)
                else:
                    st.info("🖼️ Extracting text from image using OCR...")
                    extracted_text = extract_text_from_image(file_bytes)
                
                if not extracted_text.strip():
                    st.error("❌ No text could be extracted from the document")
                    st.stop()
                
                st.success(f"✅ Extracted {len(extracted_text)} characters")
                
                # Analyze with LLM
                st.info("🤖 Analyzing document with AI...")
                analysis = analyze_document_with_llm(extracted_text, api_key)
                
                if analysis:
                    # Display results
                    display_analysis(analysis)
                    
                    # Save to database
                    session = st.session_state.Session()
                    save_analysis(session, uploaded_file.name, analysis)
                    session.close()
                    
                    st.success("💾 Analysis saved to database")
                    
                    # Show raw text in expander
                    with st.expander("📄 View Raw Extracted Text", expanded=False):
                        st.text_area(
                            "Extracted Text",
                            value=extracted_text,
                            height=300,
                            disabled=True
                        )
                else:
                    st.error("❌ Failed to analyze document")


if __name__ == "__main__":
    main()
