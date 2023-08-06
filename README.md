# RecruitBot

Chat conversations API for recruiters!

## Getting Started

These instructions will cover run and usage information

### Prerequisities

In order to run this code you'll need to install python and the used packages.
See the [Python website](https://www.python.org/downloads/) for installation instructions.

#### Environment Variables

- `OPENAI_API_KEY_ENV` - The OpenAI Access Key used in code during API calls

## Usage

Install all required packages with the following command:

```shell
pip install -r requirements.txt
```

Run the code using the following command (from the project root directory):

```shell
uvicorn main:app --reload
```

Once everything has started up, you should be able to access the API via [http://localhost:8000/](http://localhost:8000/) on your host machine and start sending API requests.

```shell
open http://localhost:8000/
```

## Example API requests:

## Get built-in conversation of id

### Request

`GET /conversation/{id}`

    curl -i -H 'Accept:application/json' http://localhost:8000/conversation/QZ8M559

### Response

    HTTP/1.1 200 OK
    date: Sun, 06 Aug 2023 17:10:47 GMT
    server: uvicorn
    content-length: 708
    content-type: application/json

    {"id":"QZ8M559","questions":[{"type":1,"text":"Hi! I'm Olivia, your personal Paradox job assistant. Thank you for your interest. We are looking for great talent for many types of jobs. To get started, can you please provide me with your first and last name?","order":1,"answer":null},{"type":2,"text":"From 1 to 10, how would you rate the process so far?","order":5,"answer":{"range":{"min":1,"max":10}}},{"type":1,"text":"Why do you want to work at Paradox?","order":4,"answer":null},{"type":2,"text":"How many years of Truck Driving experience do you have?","order":2,"answer":{"range":{"min":0,"max":30}}},{"type":3,"text":"Have you heard of Paradox before?","order":3,"answer":{"options":["Yes","No"]}}]}

## Get conversation for position using LLM

### Request

`GET /conversation_llm/{position}`

    curl -i -H 'Accept:application/json' http://localhost:8000/conversation_llm/software_enginner

### Response

    HTTP/1.1 200 OK
    date: Sun, 06 Aug 2023 17:14:18 GMT
    server: uvicorn
    content-length: 1036
    content-type: application/json

    {"questions":[{"type":1,"text":"Hello! I'm Alex, your personal job assistant. We appreciate your interest in our Software Engineer position. To begin, could you please provide me with your first and last name?","order":1},{"type":1,"text":"Could you tell me why you are interested in this Software Engineer position?","order":2},{"type":2,"text":"How many years of experience do you have in Software Engineering?","order":3,"answer":{"range":{"min":0,"max":30}}},{"type":3,"text":"Are you familiar with the following programming languages: Java, Python, C++?","order":4,"answer":{"options":["Yes","No"]}},{"type":1,"text":"Could you describe a challenging software development project you've worked on and how you overcame the challenges?","order":5},{"type":2,"text":"On a scale of 1 to 10, how would you rate your proficiency in data structures and algorithms?","order":6,"answer":{"range":{"min":1,"max":10}}},{"type":3,"text":"Have you ever worked in an Agile development environment?","order":7,"answer":{"options":["Yes","No"]}}]}

## Authors

- **Amiel Refaeli** - [Github](https://github.com/AmielRe)
