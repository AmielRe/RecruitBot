from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from Enums.QuestionType import QuestionType
from Models.Question import Question
from Models.Answer import Answer
import requests
import json

BASE_URL = 'http://ec2-54-175-34-191.compute-1.amazonaws.com:8000/conversation_builder'
app = FastAPI()

@app.get("/conversation/{id}", response_description="Get conversation data for a specific ID")
async def get_conversation(id: str):
  """
  Retrieve conversation data for a specific chat ID.

  Parameters:
      - id (str): The ID of the chat.

  Returns:
      - JSONResponse: The JSON response containing conversation data.

  Raises:
      - HTTPException(500): If there is an issue fetching data from external APIs.
  """
  chat_data = get_chat_data(id)
  questions = []
  for question in chat_data["questions"]:
    question_data = get_question_data(question['qid'])
    question_type = QuestionType(question_data['type'])
    question_text = question_data['text']
    question_order = question['order']
    answer = Answer(options=[], range={})
    if question_type in [QuestionType.MULTIPLE_CHOICE, QuestionType.NUMERIC]:
        answer = get_answer_for_question(question['qid'])
    questions.append(Question(type=question_type, text=question_text, order=question_order, answer=answer))

  # Serialize the data to JSON using the custom serialization function for Answer and Question
  json_data = json.dumps({"id": id, "questions": questions}, ensure_ascii=False, separators=(',', ': '), default=serialize_question)
  return JSONResponse(content=json.loads(json_data))

def get_chat_data(id: str):
    """
    Get chat data for a specific ID from an external API.

    Parameters:
        - id (str): The ID of the chat.

    Returns:
        - chat_data (dict): The chat data as a dictionary.

    Raises:
        - HTTPException(500): If there is an issue fetching data from external APIs.
    """
    try:
        chat_response_API = requests.get(f"{BASE_URL}/chat/{id}")
        chat_response_API.raise_for_status()
        chat_data = chat_response_API.json()
        if "questions" not in chat_data:
            raise HTTPException(status_code=500, detail="Invalid chat data")
        return chat_data
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail="Error fetching chat data") from e

def get_question_data(qid: str):
    """
    Get question data for a specific ID from an external API.

    Parameters:
        - qid (str): The ID of the question.

    Returns:
        - dict: The question data as a dictionary.

    Raises:
        - HTTPException(500): If there is an issue fetching data from external APIs.
    """
    try:
        question_response_API = requests.get(f"{BASE_URL}/question/{qid}")
        question_response_API.raise_for_status()
        return question_response_API.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail="Error fetching question data") from e

def get_answer_for_question(qid: str):
    """
    Get answer data for a specific ID from an external API.

    Parameters:
        - qid (str): The ID of the answer.

    Returns:
        - Answer: An instance of the Answer model.

    Raises:
        - HTTPException(500): If there is an issue fetching data from external APIs.
    """
    try:
        answer_response_API = requests.get(f"{BASE_URL}/answer")
        answer_response_API.raise_for_status()
        answer_data = answer_response_API.json()
        answer_to_return = Answer(options=[], range={})

        for answer in answer_data:
            if qid in answer['qids']:
                if 'range' in answer and not answer_to_return.range:
                   answer_to_return.range = answer['range']
                elif 'text' in answer:
                    answer_to_return.options.append(answer['text'])

        return answer_to_return
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail="Error fetching answer data") from e

def serialize_question(question):
    if question is None:
        return None

    serialized = {"type": int(question.type), "text": question.text, "order": question.order}
    answer = question.answer
    if answer and ((answer.options and len(answer.options) > 0) or (answer.range and bool(answer.range))):
        serialized["answer"] = serialize_answer(answer)

    return serialized

def serialize_answer(answer):
    if answer is None:
        return None

    serialized = {}
    if answer.options and len(answer.options) > 0:
        serialized["options"] = answer.options
    if answer.range and bool(answer.range):
        serialized["range"] = answer.range

    return serialized
