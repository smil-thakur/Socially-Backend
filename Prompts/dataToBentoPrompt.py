from interfaces.resumeData import ResumeData
import json


class DataToBentoPrompt:
    def __init__(self, userData: ResumeData):
        self.prompt = f"""
        {{
            "instruction": "Create a comprehensive, visually stunning Bento-style portfolio website that transforms the user's professional data into an engaging digital story. Design 15-25+ diverse bento cards that showcase every aspect of their professional journey, skills, and personality. Each bento should serve a specific purpose and collectively create a holistic view of the user.",

            "bentoDesignPrinciples": {{
                "maximizeDataUsage": "Extract maximum value from every data point. Don't just list information - transform it into meaningful, contextual content that tells a story.",
                "diverseCardTypes": "Create varied bento types: hero cards, skill showcases, project spotlights, experience timelines, education highlights, personal insights, achievement galleries, and more.",
                "visualHierarchy": "Use bigBento strategically for important sections like hero intro, major projects, or comprehensive skill overviews. Balance large statement pieces with smaller focused cards.",
                "contentDepth": "Go beyond surface-level information. Analyze years of experience, project complexity, skill relationships, career progression patterns, and create insights."
            }},

            "mandatoryBentoTypes": {{
                "heroIntro": "A compelling introduction bento (bigBento: true) combining name, title, and a powerful summary that captures their professional essence.",
                "skillsShowcase": "Multiple skill bentos - don't just list skills, group them meaningfully (frontend, backend, tools, soft skills) with context about proficiency and experience.",
                "experienceTimeline": "Create a comprehensive timeline bento that groups work experiences using innerBentos, or create individual timeline bentos for major career milestones with rich summaries, key achievements, and growth insights.",
                "projectSpotlights": "Dedicated bentos for each project showcasing technology decisions, challenges overcome, and impact created.",
                "educationHighlights": "Educational journey bentos that connect learning to career growth and current expertise.",
                "personalityInsights": "Derive personality traits, work style, and professional values from the data provided.",
                "careerProgression": "A bento analyzing career growth trajectory, years of experience, and professional evolution.",
                "techStackExpertise": "Deep dive into technology preferences, showing specializations and breadth of knowledge."
            }},

            "contentCreationGuidelines": {{
                "analyzeAndInfer": "Read between the lines. If someone has 5 years of React experience across multiple projects, highlight their expertise level. If they've worked at startups and enterprises, discuss adaptability.",
                "contextualizeSkills": "Don't just list 'Python, JavaScript'. Explain 'Polyglot developer with 4+ years in Python for backend systems and JavaScript for interactive frontends, demonstrating versatility across the full stack.'",
                "projectInsights": "Transform project data into stories. Analyze tech stack choices, project years to show evolution, and create narratives about problem-solving approaches.",
                "professionalNarrative": "Create a cohesive story arc from education through current role, highlighting growth, learning, and achievements.",
                "futureOriented": "Infer career aspirations and growth areas based on project choices, skill development, and experience progression."
            }},

            "innerBentoUsage": {{
                "skillBreakdowns": "Use innerBentos to categorize skills (Frontend: React, Vue | Backend: Node.js, Python | Tools: Docker, AWS)",
                "projectFeatures": "Break down complex projects into feature highlights or technical achievements",
                "experienceHighlights": "Key accomplishments, technologies used, or team collaboration aspects",
                "educationDetails": "Coursework, honors, relevant projects, or skills gained",
                "personalAttributes": "Leadership qualities, communication skills, problem-solving approach",
                "timelineGrouping": "For timeline bentos, use innerBentos to group related experiences (e.g., 'Current Role' with multiple positions, 'Previous Experience' with past roles, 'Education & Internships' with academic and training history)"
            }},

            "qualityStandards": {{
                "comprehensiveContent": "Aim for 15-25+ bentos minimum. Every piece of user data should appear in multiple contexts throughout the portfolio.",
                "professionalTone": "Maintain a confident, professional voice that sells the user's capabilities without being boastful.",
                "specificDetails": "Use exact years, specific technologies, concrete achievements. Avoid generic phrases.",
                "interconnectedNarrative": "Each bento should feel connected to the overall story while standing alone as valuable content."
            }},

            "userData": {json.dumps(userData.model_dump(mode="json"))},

            "creativeChallenge": "Transform this resume data into a digital experience that would impress hiring managers, clients, and peers. Create bentos that not only inform but inspire confidence in this professional's abilities and potential."
        }}
        """