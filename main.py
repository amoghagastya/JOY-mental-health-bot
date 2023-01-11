from fastapi import FastAPI
import os
# import openai
# import json
from fastapi import Request
import requests
import sys
# from datetime import datetime, timedelta
import uvicorn

def query_gpt(prompt):
    body = {
        "model": "davinci:ft-goodeed-technologies-2022-11-29-09-14-10",
        "prompt": prompt,
        "max_tokens": 150,
        "temperature": 0.7,
        # "top_p": 1,
        "n": 1,
        "frequency_penalty":0,
        "presence_penalty":0.6,
        "stop":["User:", "JOY:"]
    }
    header = {"Authorization": "Bearer " + os.getenv("OPENAI_API_KEY")}

    res = requests.post('https://api.openai.com/v1/completions',
    json = body, headers = header)
    print('time elapsed',res.elapsed.total_seconds())
    # print('\nmodel API response', str(res.json()))
    return res.json()

app = FastAPI()

# openai.api_key = os.getenv("OPENAI_API_KEY")
convo = []
@app.post('/fulfillment')
async def webhook(request: Request):
    try:
        req = await request.json()
        # print('request data', req)
        fulfillmentText = 'you said'
        query_result = req.get('queryResult')
        query = query_result.get('queryText')

        # start_sequence = "\nSAM:"
        # restart_sequence = "\nUser:"

        if query_result.get('action') == 'input.unknown':
            convo.append('User:' + query)
            # print('dialog ', convo)
            # result = 'hi there from webhook'
            convo.append("JOY:")
            prompt = ("\n").join(convo)
            # print('prompt so far', convo)
            response = query_gpt(prompt)

            # print('gpt resp', response)
            result = response.get('choices')[0].get('text')
            result = result.strip('\n')
            # print('result', result)
            convo.append(result)
            print('convo so far', '\n'.join(convo))

            return {
            "fulfillmentText": result,
            "source":
            "webhookdata"
        }
          
        if query_result.get('action') == 'welcome':
          print('prompt initialized')
          # convo = []
          convo.append('''The following is a conversation between a user and an AI Virtual Assistant - JOY. JOY is a Mental Performance Coach, utilizing mental skills, techniques, and theories to help improve performance and overcome mental barriers. Skilled in Psychological Assessment, Applied Behavior Analysis, Counseling Psychology, and Cognitive Behavioral Therapy (CBT), JOY is helpful, creative, clever, and very friendly. JOY's objective is to empathize with the user, listen intently to them and be their helpful companion. With each response, JOY encourages openness and continues the conversation in a natural, human way.
          
JOY: Hi there! I'm JOY, your Mental Performance Coach and friend. What's on your mind today?''')

    except Exception as e:
        print('error',e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print('oops',exc_type, fname, exc_tb.tb_lineno)
        return 400

@app.get('/')
def hello(request: Request):
    print('server is live')
    return {200: "API Running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=800)
