from langgraph.graph import StateGraph,START,END
from typing import TypedDict,List,Any
from rag import resume_rag_chain,resume_rag_embed
from pprint import pprint


class InterviewState(TypedDict,total=False):
    messages:List[dict]
    turns:int
    last_msg:str
    retriever:Any
    next_interviewer:str
    report:str
    job_role:str
    company:str
    job_details:str
    
def start_node(state:InterviewState):
    state["messages"]=[]
    state["turns"]=0
    
    chain = resume_rag_chain(state['retriever'])
    
    result = chain.invoke(f"""
                          <ROLE>
                        You are a professional Interview Coordinator conducting the initial phase of an interview for {state.get('job_role', 'a position')} at {state.get('company', 'our company')}.
                        </ROLE>

                        <CONTEXT>
                        - Position: {state.get('job_role', 'Not specified')}
                        - Company: {state.get('company', 'Not specified')}
                        - Job Details: {state.get('job_details', 'Not specified')}
                        - Interview Stage: Opening/Welcome
                        </CONTEXT>

                        <TASK>
                        Create a warm, professional opening that:
                        1. Welcomes the candidate warmly and professionally
                        2. Briefly mentions the role they're interviewing for
                        3. Sets a positive, encouraging tone for the interview
                        4. Asks them to give a brief introduction about themselves
                        5. Makes them feel comfortable and valued
                        </TASK>

                        <STYLE_GUIDELINES>
                        - Tone: Warm, professional, encouraging
                        - Length: 2-3 sentences maximum
                        - Be personable but maintain professionalism
                        - Show genuine interest in the candidate
                        </STYLE_GUIDELINES>

                        <OUTPUT_FORMAT>
                        Respond with ONLY your opening dialogue. No explanations, no meta-commentary.
                        </OUTPUT_FORMAT>

                        <EXAMPLE>
                        "Hello! Welcome to [Company], and thank you for your interest in the [Role] position. I'm excited to learn more about you today. Could you start by telling us a bit about yourself and what drew you to this opportunity?"
                        </EXAMPLE>
                          """)
    state['messages'].append(({"role":"interviewer","text": result.content }))
    
    
    return state


def end_node(state:InterviewState):
   
    
    chain = resume_rag_chain(state['retriever'])
    
    result = chain.invoke(F"""
        <ROLE>
You are the Interview Coordinator concluding the interview for the {state.get('job_role', 'position')} role at {state.get('company', 'our company')}.
</ROLE>

<CONTEXT>
- Interview is concluding after {state['turns']} exchanges
- Candidate has completed all assessment rounds
- Time to provide closure and next steps
</CONTEXT>

<TASK>
Create a professional, warm closing that:
1. Thanks the candidate for their time and engagement
2. Acknowledges their interest in the company/role
3. Sets clear expectations about next steps and timeline
4. Leaves them with a positive impression
5. Maintains professionalism while being personable
</TASK>

<STYLE_GUIDELINES>
- Tone: Appreciative, professional, encouraging
- Length: 2-3 sentences maximum
- Be specific about next steps without over-promising
- Show genuine appreciation for their participation
</STYLE_GUIDELINES>

<OUTPUT_FORMAT>
Respond with ONLY your closing statement. No explanations or meta-commentary.
</OUTPUT_FORMAT>

<EXAMPLE>
"Thank you so much for taking the time to speak with us today about the [Role] position. We really enjoyed learning about your experience and background. We'll be in touch within the next few days to let you know about next steps. Have a great rest of your day!"
</EXAMPLE>
    """)
    state['messages'].append(({"role":"interviewer","text": result.content }))
    
    
    
    return state

def hr_node(state:InterviewState):
    
    chain = resume_rag_chain(state['retriever'])
    
    result = chain.invoke(f"""
                          <ROLE>
                        You are a Senior HR Business Partner conducting the HR portion of an interview for the {state.get('job_role', 'position')} role at {state.get('company', 'the company')}.
                        </ROLE>

                        <CONTEXT>
                        - Position: {state.get('job_role', 'Not specified')}
                        - Company: {state.get('company', 'Not specified')}  
                        - Job Requirements: {state.get('job_details', 'Not specified')}
                        - Recent Conversation: {state.get("messages","no messages till now.")}
                        - Interview Focus: Cultural fit, soft skills, motivation, team dynamics
                        </CONTEXT>

                        <TASK>
                        Ask ONE thoughtful HR question that:
                        1. Assesses cultural fit for this specific company/role
                        2. Evaluates soft skills relevant to the position
                        3. Explores their motivation and career goals
                        4. Flows naturally from the previous conversation
                        5. Helps determine if they align with company values

                        Choose from these HR focus areas based on what hasn't been covered:
                        - Communication style and teamwork approach
                        - Handling challenges, conflict resolution, adaptability
                        - Career motivations and long-term goals
                        - Company culture alignment and values
                        - Leadership potential and growth mindset
                        - Work-life balance and stress management
                        </TASK>

                        <BEHAVIORAL_QUESTION_EXAMPLES>
                        - "Tell me about a time when you had to adapt to significant change in a previous role..."
                        - "Describe a situation where you had to work with a difficult team member..."
                        - "What motivates you most in your work, and how does that align with this role?"
                        - "Give me an example of when you took initiative to solve a problem..."
                        </BEHAVIORAL_QUESTION_EXAMPLES>

                        <STYLE_GUIDELINES>
                        - Ask ONE clear, specific question
                        - Use behavioral interview techniques (STAR method)
                        - Be conversational and engaging
                        - Reference their background when relevant
                        - Show genuine curiosity about their experiences
                        </STYLE_GUIDELINES>

                        <OUTPUT_FORMAT>
                        Respond with ONLY your question or statement. No explanations or meta-commentary.
                        </OUTPUT_FORMAT>
                          """)
    state['messages'].append({"role":"hr interviewer","text": result.content })
    state["turns"]+=1
    
    return state

def tech_node(state:InterviewState):
    
    chain = resume_rag_chain(state['retriever'])
    
    result = chain.invoke(f"""
                          <ROLE>
You are a Senior Technical Lead/Architect conducting the technical assessment for the {state.get('job_role', 'technical position')} role.
</ROLE>

<CONTEXT>
- Position: {state.get('job_role', 'Not specified')}
- Company: {state.get('company', 'Not specified')}
- Technical Requirements: {state.get('job_details', 'Not specified')}
- Recent Conversation: {state.get("messages","no messages till now.")}
- Interview Focus: Technical competency, problem-solving, system design
</CONTEXT>

<TASK>
Ask ONE technical question that:
1. Directly relates to the skills needed for this specific role
2. Assesses their practical experience with relevant technologies
3. Evaluates problem-solving approach and technical depth
4. Allows them to showcase their expertise
5. Tests both theoretical knowledge and practical application

Technical Question Categories (choose most relevant):
- System Design: "How would you design/architect..."
- Problem Solving: "Walk me through how you'd approach..."
- Experience Deep-Dive: "Tell me about a challenging technical problem you solved..."
- Code Quality: "How do you ensure code quality and maintainability..."
- Technology Choice: "When would you choose X over Y and why..."
- Performance/Scalability: "How would you optimize..."
</TASK>

<TECHNICAL_DEPTH_LEVELS>
- Surface Level: Basic concepts and definitions
- Applied Level: Real-world usage and best practices  
- Expert Level: Trade-offs, edge cases, system implications
- Architect Level: Cross-system impact, scalability, design patterns
</TECHNICAL_DEPTH_LEVELS>

<STYLE_GUIDELINES>
- Ask ONE clear, specific technical question
- Reference their resume/experience when possible
- Allow for different solution approaches
- Focus on thought process, not just correct answers
- Be encouraging while maintaining technical rigor
</STYLE_GUIDELINES>

<OUTPUT_FORMAT>
Respond with ONLY your technical question. No explanations or meta-commentary.
</OUTPUT_FORMAT>

<EXAMPLE>
"I see you have experience with microservices. Can you walk me through how you'd design a system to handle 10,000 concurrent users for an e-commerce platform, focusing on the key architectural decisions you'd make?"
</EXAMPLE>
                          """)
    state['messages'].append({"role":"tech interviewer","text": result.content })
    state["turns"]+=1
    
    return state

def manager_node(state:InterviewState):
    
    chain = resume_rag_chain(state['retriever'])
    
    result = chain.invoke(f"""
                          <ROLE>
You are a Department Manager/Director evaluating the candidate for the {state.get('job_role', 'position')} role from a leadership and business perspective.
</ROLE>

<CONTEXT>
- Position: {state.get('job_role', 'Not specified')}
- Company: {state.get('company', 'Not specified')}
- Role Requirements: {state.get('job_details', 'Not specified')}
- Recent Conversation: {state.get("messages","no messages till now.")}
- Interview Focus: Leadership potential, project management, strategic thinking, business impact
</CONTEXT>

<TASK>
Ask ONE management/leadership question that:
1. Assesses their ability to handle responsibility and ownership
2. Evaluates project management and organizational skills
3. Tests strategic thinking and business acumen
4. Explores their potential for growth and leadership
5. Determines how they handle pressure and deadlines

Management Focus Areas (choose most relevant):
- Project Leadership: "Describe a project you led from start to finish..."
- Problem Resolution: "Tell me about a time when a project was failing..."
- Team Dynamics: "How do you handle competing priorities with limited resources..."
- Strategic Thinking: "How would you approach improving [specific business area]..."
- Stakeholder Management: "Describe how you've managed expectations..."
- Decision Making: "Walk me through a difficult decision you had to make..."
</TASK>

<LEADERSHIP_COMPETENCIES>
- Ownership and Accountability
- Strategic Vision and Planning
- Influencing and Persuasion
- Change Management
- Resource Optimization
- Cross-functional Collaboration
</LEADERSHIP_COMPETENCIES>

<STYLE_GUIDELINES>
- Ask ONE behavioral/situational question
- Focus on leadership potential even for individual contributor roles
- Probe for business impact and results
- Look for evidence of growth mindset
- Be direct but encouraging
</STYLE_GUIDELINES>

<OUTPUT_FORMAT>
Respond with ONLY your question. No explanations or meta-commentary.
</OUTPUT_FORMAT>

<EXAMPLE>
"Tell me about a time when you had to manage a project with tight deadlines and limited resources. How did you prioritize and what was the outcome?"
</EXAMPLE>
                          """)
    state['messages'].append({"role":"manager interviewer","text": result.content })
    state["turns"]+=1
    
    return state

def decider_node(state: InterviewState):
    chain = resume_rag_chain(state["retriever"])

    result = chain.invoke(f"""
                            <ROLE>
You are an Interview Flow Coordinator managing a structured interview process.
</ROLE>

<CONTEXT>
- Current Turn: {state['turns']}
- Recent Conversation: {state.get("messages","no messages till now.")}
- Available Interviewers: HR, TECH, MANAGER
- Interview Goal: Comprehensive assessment across all dimensions
</CONTEXT>

<DECISION_CRITERIA>
1. Interview Progression Logic:
   - Turns 1-3: Focus on HR (rapport, cultural fit)
   - Turns 4-7: Emphasize TECH (technical competency)
   - Turns 8-10: Include MANAGER (leadership, strategy)
   - Turn 11+: Consider ending with END

2. Content Gap Analysis:
   - HR: Have we assessed cultural fit, communication, motivation?
   - TECH: Have we evaluated technical skills relevant to the role?
   - MANAGER: Have we explored leadership potential and business acumen?

3. Flow Balance:
   - Avoid 3+ consecutive questions from same interviewer
   - Ensure all three perspectives are represented
   - End when comprehensive coverage is achieved
</DECISION_CRITERIA>

<DECISION_RULES>
- If turns < 6: Continue with appropriate interviewer
- If turns 6-10: Ensure all three types have participated
- If turns > 10: Consider END if all areas covered
- If any interviewer hasn't spoken in 4+ turns: Prioritize them
- If candidate seems fatigued or interview feels complete: END
</DECISION_RULES>

<TASK>
Analyze the conversation flow and decide who should speak next.
Return EXACTLY one word: HR, TECH, MANAGER, or END
</TASK>

<OUTPUT_FORMAT>
Return only one word with no punctuation or explanation: HR, TECH, MANAGER, or END
</OUTPUT_FORMAT>
                            """)


    state["next_interviewer"] = result.content.strip().upper()
    print(state["next_interviewer"])
    return state

def analysis_node(state: InterviewState):
    chain = resume_rag_chain(state["retriever"])

    result = chain.invoke(f"""
    <ROLE>
You are a Senior Talent Assessment Specialist providing a comprehensive interview evaluation.
</ROLE>

<CONTEXT>
- Position: {state.get('job_role', 'Not specified')}
- Company: {state.get('company', 'Not specified')}
- Job Requirements: {state.get('job_details', 'Not specified')}
- Interview Duration: {state['turns']} exchanges
- Full Interview Transcript: {state.get("messages","no messages till now.")}
</CONTEXT>

<EVALUATION_FRAMEWORK>
Assess the candidate across these key dimensions:

1. **Technical Competency** (if applicable)
   - Relevant technical skills and knowledge
   - Problem-solving approach and methodology
   - Code quality and best practices understanding
   - System design and architectural thinking

2. **Professional Skills**
   - Communication clarity and effectiveness
   - Leadership potential and initiative
   - Project management and organizational abilities
   - Adaptability and learning agility

3. **Cultural Alignment**
   - Company values alignment
   - Team collaboration style
   - Work ethic and professionalism
   - Growth mindset and ambition

4. **Role-Specific Fit**
   - Direct experience relevance
   - Skill gaps and training needs
   - Career trajectory alignment
   - Motivation for this specific role/company
</EVALUATION_FRAMEWORK>

<TASK>
Create a comprehensive, actionable interview assessment report using the following structure:
</TASK>

<OUTPUT_FORMAT>
## 🎯 Overall Recommendation
**[STRONG HIRE / HIRE / WEAK HIRE / NO HIRE]** - [One sentence rationale]

## 💪 Key Strengths
- [Specific strength with evidence from interview]
- [Specific strength with evidence from interview]  
- [Specific strength with evidence from interview]

## ⚠️ Areas of Concern
- [Specific concern with evidence]
- [Specific concern with evidence]

## 📈 Development Opportunities
- [Skill/area to develop with suggested approach]
- [Skill/area to develop with suggested approach]

## 🎯 Role-Specific Assessment
**Technical Fit**: [Rating: Excellent/Good/Adequate/Poor] - [Brief explanation]
**Cultural Fit**: [Rating: Excellent/Good/Adequate/Poor] - [Brief explanation]  
**Leadership Potential**: [Rating: High/Medium/Low] - [Brief explanation]

## 🚀 Next Steps Recommendation
- [Specific next step if moving forward]
- [Any additional assessments needed]
- [Onboarding considerations if hired]

## 📝 Interview Quality Notes
- Coverage: [What was well-covered vs. what needs follow-up]
- Candidate Engagement: [How well they participated]
- Question Quality: [Effectiveness of our assessment]
</OUTPUT_FORMAT>

<QUALITY_STANDARDS>
- Be specific and evidence-based
- Reference actual interview moments
- Provide actionable insights
- Balance positive and constructive feedback
- Consider role requirements and company context
- Maintain professional, objective tone
</QUALITY_STANDARDS>
    
    """)
    
    state["next_interviewer"]="CLOSED"

    print("\n📋 Interview Analysis Report:\n")
    print(result.content)
    state["report"]=result.content
    return state


def interview_graph():
    
    builder = StateGraph(InterviewState)
    
    builder.add_node("start",start_node)
    builder.add_node("HR",hr_node)
    builder.add_node("MANAGER",manager_node)
    builder.add_node("TECH",tech_node)
    builder.add_node("DECIDER",decider_node)
    builder.add_node("ANALYSIS",analysis_node)
    builder.add_node("END",end_node)
    
    builder.add_edge(START,"start")
    builder.add_edge("start","DECIDER")
    builder.add_edge("HR", "DECIDER")
    builder.add_edge("TECH", "DECIDER")
    builder.add_edge("MANAGER", "DECIDER")
    builder.add_conditional_edges(
    "DECIDER",
    lambda state: state["next_interviewer"],
    {
        "HR": "HR",
        "TECH": "TECH",
        "MANAGER": "MANAGER",
        "END": "END"
    }
)

    builder.add_edge("END","ANALYSIS")
    builder.add_edge("ANALYSIS",END)
    
    return builder.compile()

def run_interview():
    retriever = resume_rag_embed(
        r"C:\Users\gamin\Documents\projects\Mock_Interview_agents_using_Langchain\backend\assets\Anand-S-Resume.pdf"
    )

    graph = interview_graph()

    state = {
        "messages": [],
        "turns": 0,
        "last_msg": "",
        "retriever": retriever,
    }

    stream = graph.stream(state) 

    while True:
        try:
            step = next(stream)
            current_node, current_state = list(step.items())[0]
            state = current_state  

            if "messages" not in state or not state["messages"]:
                print("\n⚠️ No message returned. Skipping.")
                continue

            last_msg = state["messages"][-1]["text"]
            if current_node in {"HR", "TECH", "MANAGER","start","END"}:
                print(f"\n👤 {current_node} says: {last_msg}")

            if state.get("next_interviewer") == "CLOSED":
                break

            # Only take user input after interviewer nodes
            if current_node in {"HR", "TECH", "MANAGER","start"}:
                user_input = input("🧑 You: ")
                state["messages"].append({"role": "candidate", "text": user_input})
                state["last_msg"] = user_input

        except StopIteration:
            break

    print("\n✅ Interview ended.")






if __name__ == "__main__":
    
    run_interview()
    