from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from Enums.QuestionType import QuestionType
from Models.Question import Question
from Models.Answer import Answer
import requests
import json
import os
import openai
import error_messages
import logging

BASE_URL = 'http://ec2-54-175-34-191.compute-1.amazonaws.com:8000/conversation_builder'
OPENAI_API_KEY_ENV = 'OPENAI_API_KEY'
MODEL = 'gpt-4-0613'
LLM_POSITION_QUERY_FILE = 'Queries\llm_position.txt'
SYSTEM_ROLE = 'system'
USER_ROLE = 'user'
ASSISTANT_INTRODUCTION = 'You are a helpful assistant.'

# NOTE: here i used a quick guide to refresh my memory on FastAPI - https://fastapi.tiangolo.com/tutorial/first-steps/
app = FastAPI()

# NOTE: here i used a quick guide to refresh my memory on python logging - "https://realpython.com/python-logging/"
logging.basicConfig(level=logging.INFO, filename='app.log', filemode='w', format="%(asctime)s | %(levelname)s | %(message)s")

@app.get("/conversation/{id}", response_description="Get conversation data for a specific chat ID")
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

  logging.info(f"New get_conversation with chat id '{id}'")

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

    logging.debug(f"Finished fetching question - type = {question_type}, text = {question_text}, order = {question_order}")
    questions.append(Question(type=question_type, text=question_text, order=question_order, answer=answer))

  # Serialize the data to JSON using the custom serialization function for Answer and Question
  json_data = json.dumps({"id": id, "questions": questions}, ensure_ascii=False, separators=(',', ': '), default=serialize_question)
  return JSONResponse(content=json.loads(json_data))

@app.get("/conversation_llm/{position}", response_description="Get conversation data created by LLM for a specific position")
async def get_conversation_llm(position: str):
    """
    Fetches conversation data created by the Language Model (LLM) for a specific position.

    This endpoint sends a user query, containing the provided 'position' parameter, to the OpenAI Language Model.
    The model then generates a helpful assistant response based on the query.

    Parameters:
        position (str): The specific position for which the conversation data is requested.

    Returns:
        JSONResponse: A JSON response containing the generated conversation data.

    Raises:
        HTTPException:
            - 500: If the 'Queries\llm_position.txt' file is not found or an error occurs during the API call.

    Notes:
        - Before using this endpoint, ensure that you have set the 'OPENAI_API_KEY' environment variable
          with your OpenAI API key.

    Example Usage:
        Assuming the application is running locally on 'http://localhost:8000', you can make a GET request to:
        http://localhost:8000/conversation_llm/developer

        The response will contain the generated conversation data for the 'developer' position.
    """

    logging.info(f"New get_conversation_llm for position '{position}'")

    # NOTE: here i did a quick search in Stack Overflow to see how to access environment variables - https://stackoverflow.com/questions/4906977/how-can-i-access-environment-variables-in-python
    api_key = os.environ.get(OPENAI_API_KEY_ENV)
    if api_key is None:
        logging.error(error_messages.MISSING_OPENAI_API_KEY_ENV, exc_info=True)
        raise HTTPException(status_code=500, detail=error_messages.MISSING_OPENAI_API_KEY_ENV)
    
    openai.api_key = api_key

    logging.debug("OpenAI API key loaded")

    try:
        # Read query and insert position
        with open(LLM_POSITION_QUERY_FILE, mode='r') as file:
            query_text = file.read().replace("{POSITION}", position)
    
        logging.info("Finished reading query file, sending API request to OpenAI")

        response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": SYSTEM_ROLE, "content": ASSISTANT_INTRODUCTION},
            {"role": USER_ROLE, "content": query_text}
        ],
        temperature=0)
    
        logging.info("Finish sending API request to OpenAI, returning response")

        return JSONResponse(content=json.loads(response.choices[0].message.content))
    except FileNotFoundError:
        logging.error(error_messages.QUERY_FILE_NOT_FOUND, exc_info=True)
        raise HTTPException(status_code=500, detail=error_messages.QUERY_FILE_NOT_FOUND)
    except Exception as e:
        # Handle other potential exceptions gracefully
        logging.error(error_messages.REQUEST_PROCESSING_ERROR, exc_info=True)
        raise HTTPException(status_code=500, detail=error_messages.REQUEST_PROCESSING_ERROR)

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
        logging.info(f"Getting chat data for chat id '{id}'")
        chat_response_API = requests.get(f"{BASE_URL}/chat/{id}")
        chat_response_API.raise_for_status()
        chat_data = chat_response_API.json()
        if "questions" not in chat_data:
            logging.error(error_messages.INVALID_CHAT_DATA, exc_info=True)
            raise HTTPException(status_code=500, detail=error_messages.INVALID_CHAT_DATA)
        return chat_data
    except requests.exceptions.RequestException as e:
        logging.error(error_messages.ERROR_FETCHING_CHAT_DATA, exc_info=True)
        raise HTTPException(status_code=500, detail=error_messages.ERROR_FETCHING_CHAT_DATA) from e

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
        logging.info(f"Getting question data for question id '{qid}'")
        question_response_API = requests.get(f"{BASE_URL}/question/{qid}")
        question_response_API.raise_for_status()
        return question_response_API.json()
    except requests.exceptions.RequestException as e:
        logging.error(error_messages.ERROR_FETCHING_QUESTION_DATA, exc_info=True)
        raise HTTPException(status_code=500, detail=error_messages.ERROR_FETCHING_QUESTION_DATA) from e

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
        logging.info(f"Getting answer data for question id '{qid}'")
        answer_response_API = requests.get(f"{BASE_URL}/answer")
        answer_response_API.raise_for_status()
        answer_data = answer_response_API.json()
        answer_to_return = Answer(options=[], range={})

        # Iterate over each answer and search for matching qid
        for answer in answer_data:
            if qid in answer['qids']:
                if 'range' in answer and not answer_to_return.range:
                   answer_to_return.range = answer['range']
                elif 'text' in answer:
                    answer_to_return.options.append(answer['text'])

        return answer_to_return
    except requests.exceptions.RequestException as e:
        logging.error(error_messages.ERROR_FETCHING_ANSWER_DATA, exc_info=True)
        raise HTTPException(status_code=500, detail=error_messages.ERROR_FETCHING_ANSWER_DATA) from e

def serialize_question(question):
    if question is None:
        return None

    answer = question.answer
    serialized = {
        "type": int(question.type),
        "text": question.text,
        "order": question.order,
        "answer": serialize_answer(answer) if answer and (answer.options or answer.range) else None
    }

    return serialized

def serialize_answer(answer):
    if answer is None:
        return None

    serialized = {
        "options": answer.options if answer.options else None,
        "range": answer.range if answer.range else None
    }

    return {key: value for key, value in serialized.items() if value is not None}
