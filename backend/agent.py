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
    
    result = chain.invoke("Start the interview with a warm greeting and ask the candidate to introduce themselves. just output the dialouge text only")
    state['messages'].append(({"role":"interviewer","text": result.content }))
    state["turns"]+=1
    
    return state


def end_node(state:InterviewState):
    state["messages"]=[]
    state["turns"]=0
    
    chain = resume_rag_chain(state['retriever'])
    
    result = chain.invoke("end the interview with a ending message. just output the dialouge text only")
    state['messages'].append(({"role":"interviewer","text": result.content }))
    state["turns"]+=1
    
    return state

def hr_node(state:InterviewState):
    
    chain = resume_rag_chain(state['retriever'])
    
    result = chain.invoke(f"""
                          You are the HR of the company and you are in interview with him, based on the resume of the applicant and the previous messages that are
                          {state['messages']}
                          give should be the next question or the dialouge to the applicant from you as the hr of the company.
                          just output the dialouge text only
                          """)
    state['messages'].append({"role":"interviewer","text": result.content })
    state["turns"]+=1
    
    return state

def tech_node(state:InterviewState):
    
    chain = resume_rag_chain(state['retriever'])
    
    result = chain.invoke(f"""
                          You are the Technical role of the company and you are in interview with him, based on the resume of the applicant and the previous messages that are
                          {state['messages']}
                          give should be the next question or the dialouge to the applicant from you as the tech man of the company.
                          just output the dialouge text only
                          """)
    state['messages'].append({"role":"interviewer","text": result.content })
    state["turns"]+=1
    
    return state

def manager_node(state:InterviewState):
    
    chain = resume_rag_chain(state['retriever'])
    
    result = chain.invoke(f"""
                          You are the manager of the company and you are in interview with him, based on the resume of the applicant and the previous messages that are
                          {state['messages']}
                          give should be the next question or the dialouge to the applicant from you as the manager of the company.
                          just output the dialouge text only
                          """)
    state['messages'].append({"role":"interviewer","text": result.content })
    state["turns"]+=1
    
    return state

def decider_node(state:InterviewState):
    
    chain = resume_rag_chain(state["retriever"])
    
    result = chain.invoke(f"""
                          You are the decider who selects who should talk next the manager , hr or the techie, based on the previous messages that are
                          {state['messages']} \n \n
                          decide who should talk next.
                          just output the text as one word HR,MANAGER,TECH.
                          If the interview needs to be ended just output END.
                          """)
    
    state["next_interviewer"]=result.content.upper()
    
    return state



def interview_graph():
    
    builder = StateGraph(InterviewState)
    
    builder.add_node("start",start_node)
    builder.add_node("HR",hr_node)
    builder.add_node("MANAGER",manager_node)
    builder.add_node("TECH",tech_node)
    builder.add_node("DECIDER",decider_node)
    builder.add_node("END",end_node)
    
    builder.add_edge(START,"start")
    builder.add_edge("start","DECIDER")
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

    builder.add_edge("END",END)
    
    return builder.compile()

def run_interview():
    
    
    retriver  = resume_rag_embed(r"C:\Users\gamin\Documents\projects\Mock_Interview_agents_using_Langchain\backend\assets\Anand-S-Resume.pdf")
    
    graph = interview_graph()
    
    input_state={
        "messages":[],
        "turns":0,
        "last_msg":"",
        "retriever":retriver
    }
    
    state = graph.invoke(input_state)
    
    pprint(state)


if __name__ == "__main__":
    
    run_interview()
    