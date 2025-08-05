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
    
def start_node(state:InterviewState):
    state["messages"]=[]
    state["turns"]=0
    
    chain = resume_rag_chain(state['retriever'])
    
    result = chain.invoke("""
                          You are an interview coordinator.
        Start the interview with a warm greeting.
        Then, ask the candidate to briefly introduce themselves.
        Respond only with your dialogue.
                          """)
    state['messages'].append(({"role":"interviewer","text": result.content }))
    state["turns"]+=1
    
    return state


def end_node(state:InterviewState):
   
    
    chain = resume_rag_chain(state['retriever'])
    
    result = chain.invoke("""
        The interview is complete. End the conversation politely.
        Respond only with your closing statement.
    """)
    state['messages'].append(({"role":"interviewer","text": result.content }))
    state["turns"]+=1
    
    
    return state

def hr_node(state:InterviewState):
    
    chain = resume_rag_chain(state['retriever'])
    
    result = chain.invoke(f"""
                          You are the HR interviewer.
        Resume: Consider the applicant's resume.
        Context: {state['messages']}

        Ask a question relevant to HR topics such as communication skills, cultural fit,
        teamwork, or the candidate's motivation for applying.
        Keep it professional and relevant to the current conversation.

        Respond only with your next question or message.
                          """)
    state['messages'].append({"role":"hr interviewer","text": result.content })
    state["turns"]+=1
    
    return state

def tech_node(state:InterviewState):
    
    chain = resume_rag_chain(state['retriever'])
    
    result = chain.invoke(f"""
                          You are the technical interviewer.
        Resume: Refer to the candidate's resume.
        Context: {state['messages']}

        Ask a technical question based on the candidate's skills, projects, or past experiences.
        Keep your response clear and focused.

        Respond only with your next technical question or message.
                          """)
    state['messages'].append({"role":"tech interviewer","text": result.content })
    state["turns"]+=1
    
    return state

def manager_node(state:InterviewState):
    
    chain = resume_rag_chain(state['retriever'])
    
    result = chain.invoke(f"""
                          You are the manager interviewer.
        Resume: Consider the applicant's profile.
        Context: {state['messages']}

        Ask a question related to team leadership, project management, or how the candidate
        handles responsibility and deadlines.

        Respond only with your next question or message.
                          """)
    state['messages'].append({"role":"manager interviewer","text": result.content })
    state["turns"]+=1
    
    return state

def decider_node(state: InterviewState):
    chain = resume_rag_chain(state["retriever"])

    result = chain.invoke(f"""
                            You are the interview coordinator. Based on the previous messages:

                            {state['messages']}

                            Decide who should speak next: HR, TECH, or MANAGER.
                            
                            Return END to conclude the interview.

                            ONLY return exactly one of these words: HR, TECH, MANAGER.
                            No punctuation, no explanations, just the word.
                            """)


    state["next_interviewer"] = result.content.strip().upper()
    print(state["next_interviewer"])
    return state

def analysis_node(state: InterviewState):
    chain = resume_rag_chain(state["retriever"])

    result = chain.invoke(f"""
    You are an interview evaluator. Based on the full interview transcript below:
    
    {state['messages']}
    
    Provide a brief analysis of the candidate's performance including:
    - Strengths
    - Weaknesses
    - Areas of improvement
    - Overall impression

    Just output the report directly without any extra formatting or greetings.
    
    """)
    
    state["next_interviewer"]="CLOSED"

    print("\n📋 Interview Analysis Report:\n")
    print(result.content)
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
    