AMBIGUITY_DETECTION_PROMPT = """
You are an expert Project Manager. Analyze the following raw project kickoff notes and identify any:
1. Contradictions (statements that conflict with each other).
2. Ambiguities (vague requirements that need more detail).
3. Missing Critical Information (e.g., specific tech stack, timeline, budget, or user roles not mentioned).

Raw Notes:
{raw_input}

Output a JSON list of objects with "type" (contradiction, ambiguity, missing), "description", and "question_for_client".
"""

PRD_GENERATION_PROMPT = """
You are an expert Technical Product Manager. Based on the following clarified project notes, generate a comprehensive Product Requirements Document (PRD).

Project Name: {project_name}
Clarified Notes:
{clarified_input}

Include the following sections:
1. Executive Summary
2. Target Audience
3. Key Features & Functional Requirements
4. Technical Constraints & Stack
5. User Journeys
6. Out of Scope

Format the output in clean Markdown.
"""

ROLE_EXTRACTION_PROMPT = """
Analyze the following PRD and identify the specific software engineering and design roles required to build this project.

PRD:
{prd_text}

For each role, provide:
1. Title (e.g., Senior Backend Engineer)
2. Responsibilities (Short summary)
3. Key Required Skills (Comma-separated list)

Output as a JSON list of objects.
"""

MATCHING_PROMPT = """
You are a technical recruiter. Match the following Job Description (JD) against the provided Employee Resume.

JD:
{jd_text}

Resume:
{resume_text}

Evaluate the match and provide:
1. Score: A numeric score from 0 to 100 based on skill overlap and experience level.
2. Justification: A detailed explanation of why they are or are not a good fit, highlighting specific strengths and gaps.

Output as a JSON object with "score" and "justification".
"""
