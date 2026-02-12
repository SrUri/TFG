import logging
logger = logging.getLogger('main')

def translate_text_to_english(text: str) -> str:
    logger.info("🌐 Translating text to English with LLM...")
    return f"Translate the following text into English, keeping all technical meaning:\n\n{text}"

def get_extract_theme_prompt(analysis_text: str) -> str:
    return f"""Analyze this university course syllabus and extract the following information:

Return a JSON object with these exact fields:
- "core_topic": Main technical focus (e.g., "Programming Fundamentals")
- "key_contents": List of 3-5 main topics covered
- "application_domain": Field where these skills are applied

IMPORTANT:
1. Focus on the most technical aspects
2. Ignore administrative information
3. If no clear contents found, infer from course title and context
4. Ensure the core_topic and key_contents align with the provided syllabus content

Return a JSON object with the following structure:
{{
    "core_topic": "Programming Fundamentals",
    "key_contents": ["Variables", "Control Structures", "Functions", "Basic Algorithms"],
    "application_domain": "Software Development",
}}

The input text is as follows:
{analysis_text}"""

def get_extract_subjects_prompt(subject_title: str, translated_text: str) -> str:
    return f"""You are an expert academic information extractor. The input text represents the syllabus of a SINGLE university subject titled '{subject_title}'. The text may include sections or topics (e.g., 'Electrostatics', 'Direct Electric Current') that are NOT separate subjects but rather thematic areas within this single subject.

Extract the following information for the subject '{subject_title}':

1. COMPETENCES:
- List 3-5 specific competences the student will acquire
- Focus on technical skills and practical abilities DIRECTLY RELATED to the subject '{subject_title}' (e.g., for Physics, focus on skills like circuit analysis, electromagnetic field calculations)
- Only include competences that align with the subject’s discipline (e.g., for Physics, exclude programming or database skills unless explicitly mentioned in the syllabus)
- Example for Physics: "Analyze and solve electric circuits using Kirchhoff’s laws"
- If the syllabus lacks clear competences, infer 3-5 competences based on the subject title and contents, but ensure they are specific to the discipline

2. OBJECTIVES:
- List 5-8 specific learning objectives
- Start each with an action verb (Design, Implement, Analyze, etc.)
- Be as technical and specific as possible

3. CONTENTS:
- Extract ALL technical contents in detail
- Organize in a hierarchical structure where each key is a topic name and its value is a list of subtopics
- Use the actual topic names from the syllabus as keys (e.g., "Electrostatics", "Direct Electric Current")
- Include specific technologies, methods, or tools mentioned in the subtopics
- Only include topics explicitly mentioned in the syllabus; do NOT add placeholder topics (e.g., "Additional Topic 1")
- If more than 6 topics are present, select the 6 most relevant based on technical depth
- Example: "Electrostatics": ["Electric Field", "Electrostatic Energy and Potential", "Capacitors"]

Return a JSON object with the following structure:
{{
    "{subject_title}": {{
        "competences": ["list", "of", "competences"],
        "objectives": ["list", "of", "objectives"],
        "contents": {{ "Topic 1": ["subtopics"], "Topic 2": ["subtopics"], ... }}
    }}
}}

STRICT RULES:
- Always use double quotes
- Maintain consistent JSON structure
- Translate non-English content to English
- If a section is missing, include it as empty array/dict
- Never add explanatory text outside the JSON
- The JSON must be valid and readable directly with json.loads()
- For competences, ensure they are specific to the subject’s discipline (e.g., for Physics, include skills like "Calculate electric fields" and exclude unrelated skills like "Design relational databases")
- For contents, use the exact topic names from the syllabus as keys (e.g., "Electrostatics") and list subtopics as values
- Format subtopics as individual strings, not concatenated
- Do NOT add placeholder topics like "Additional Topic 1" for missing entries

The input text is as follows:
{translated_text}"""

def get_subject_expert_prompt(comp1: dict, comp2: dict, final_score: float) -> str:
    return f"""You are an expert in comparing academic programs. Analyze the thematic similarity between the following subjects:

Subject 1:
- Name: {comp1['name']}
- Competences: {comp1['competences']}
- Objectives: {comp1['objectives']}
- Contents: {comp1['contents'][:4000]}...

Subject 2:
- Name: {comp2['name']}
- Competences: {comp2['competences']}
- Objectives: {comp2['objectives']}
- Contents: {comp2['contents'][:4000]}...

**Key Instructions:**
- Evaluate thematic similarity by balancing **contents**, **objectives**, and **competences**, prioritizing contents but considering all three.
- Identify **technical and conceptual similarities** (e.g., "Calculate electric fields" is similar to "Analyze electromagnetic forces").
- Treat **minor variations** as equivalent (e.g., "Programming in C++" is similar to "Programming in C").
- List substantial differences as strings describing the distinction (e.g., "Steady-state sinusoidal analysis is covered in Subject 1 but not in Subject 2" or "Digital circuits are central in Subject 2 but absent in Subject 1"). Do not use expressions like "A" vs. "B"; express each difference as a single valid string.
- Exclude generic or non-technical competences (e.g., "teamwork" is not relevant for technical topics).
- If subject names are similar, deeply analyze contents, objectives, and competences to avoid assumptions.
- Do not assume equivalence without clear evidence from the provided texts.
- If the similarity score ({final_score:.2f}) seems inconsistent with your analysis, include a brief warning explaining the discrepancy.
- For the explanation, provide useful insights into the thematic relationship, focusing on both similarities and differences and **using contents** as the primary basis for comparison.

**Devuelve exclusivamente un JSON con las siguientes claves:**
{{
    "similitudes_tecnicas": ["theme 1", "theme 2"],
    "diferencias_sustanciales": ["Difference between theme A and theme B", "Topic X present only in subject 1"],
    "advertencias": ["brief warning"],
    "explicacion": ["Clear justification in six to seven sentences for the score ({final_score:.2f}), based on the content of both subjects and the balanced analysis of similarities and differences."]
}}

**Strict Requirements:**
- Return **ONLY a valid JSON object** with the exact keys: `similitudes_tecnicas` (list of strings), `diferencias_sustanciales` (list of strings), `advertencias` (list of strings), `explicacion` (non-empty string).
- ALWAYS output valid JSON. Escape all double quotes inside strings. Ensure complete syntax with closing braces and brackets.
- Ensure the JSON is properly closed with a closing brace
- Escape any double quotes inside string values using backslash (\")
- Do not include trailing commas in arrays or objects
- Use **double quotes** and properly escape special characters.
- Do **NOT** include additional text, comments, markdown (e.g., ```json), or spaces outside the JSON object.
- Use empty lists `[]` for `similitudes_tecnicas`, `diferencias_sustanciales`, or `advertencias` if none apply.
- Ensure `explicacion` is a clear, non-empty string with 6-7 sentences.
- If the input is insufficient or unclear, return empty lists for `similitudes_tecnicas` and `diferencias_sustanciales`, and note the issue in `advertencias` and `explicacion`.
"""

def get_theme_comparator_prompt(theme1: dict, theme2: dict) -> str:
    return f"""As an academic expert, compare these two course themes and rate their similarity (0-1):

Theme 1:
- Core Topic: {theme1.get('core_topic', 'Unknown')}
- Key Contents: {theme1.get('key_contents', 'Unknown')}
- Application Domain: {theme1.get('application_domain', 'Unknown')}

Theme 2:
- Core Topic: {theme2.get('core_topic', 'Unknown')}
- Key Contents: {theme2.get('key_contents', 'Unknown')}
- Application Domain: {theme2.get('application_domain', 'Unknown')}

Evaluation criteria:
1. Core topic alignment (e.g., "Introductory Programming" vs. "Introductory Programming" = high, "Physics" vs. "Biology" = low).
2. Key content overlap (e.g., "Data Structures" vs. "Algorithms" = high, "History" vs. "Mathematics" = low).
3. Application domain overlap (e.g., "Computer Engineering" vs. "Software Development" = high, "Physics" vs. "Economics" = low).

Special rules:
- If core topics are identical or nearly identical (e.g., "Introductory Programming" vs. "Introductory Programming"), assign a high similarity (0.85-0.95) unless other fields differ significantly.
- Penalize heavily if core topics are from different disciplines (e.g., "Introductory Programming" vs. "Economics", "Physics" vs. "Biology").

Return ONLY a number between 0 and 1 with two decimal places, where:
0.90-1.00 = Nearly identical themes
0.70-0.89 = Strong technical and contextual overlap
0.50-0.69 = Partial overlap in some components
0.30-0.49 = Weak, superficial similarity
0.00-0.29 = Essentially different or unrelated

Score:"""