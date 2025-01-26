from typing import Annotated
from fastapi import FastAPI, Depends
from pydantic import BaseModel
import uvicorn
import random 
from enum import Enum

from oci.generative_ai_inference import GenerativeAiInferenceClient
from oci.generative_ai_inference.models import OnDemandServingMode, CohereChatRequest, ChatDetails
import oci

LLM_MODEL = "cohere.command-r-16k" 

compartmentId= "ocid1.compartment.oc1..aaaaaaaac3cxhzoka75zaaysugzmvhm3ni3keqvikawjxvwpz26mud622owa"
llm_service_endpoint= "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"


app = FastAPI(root_path="/ash")


# oci key enabled for api access
config = oci.config.from_file('~/.oci/config')

llm_client = GenerativeAiInferenceClient(
                config=config,
                service_endpoint=llm_service_endpoint,
                retry_strategy=oci.retry.NoneRetryStrategy(),
                timeout=(10,240))

class GenderEnum(str, Enum):
    Male = 'M'
    Female = 'F'

class TopEnum(str, Enum):
    Tshirt = 'tShirt'
    Shirt = 'shirt'
    Salvar = 'salvar'

class BottomEnum(str, Enum):
    Shorts = 'shorts'
    Pants = 'pants'
    Skirts = 'Skirt'
    Suit = 'suit'

class AccEnum(str, Enum):
    Hat = 'Hat'
    Sunglasses = 'Sun Glasses'
    Jacket = 'jacket'
    Umbrella = 'umberella'

low_temp = {
	"Austin" : 50,
	"Delhi"	 : 40,
	"Hyderabad" : 60,
	"Bengulru" : 50
}

high_temp = {
	"Austin" : 90,
	"Delhi"	 : 80,
	"Hyderabad" : 70,
	"Bengulru" : 70
}

def get_chat_request():
        llm_chat_request = CohereChatRequest()
        
        llm_chat_request.is_stream = False 
        llm_chat_request.max_tokens = 500 # max token to generate, can lead to incomplete responses
        llm_chat_request.temperature = 1.0 # higer value menas more randon, defaul = 0.3
        
        return llm_chat_request


def get_chat_detail (llm_request):
        chat_detail = ChatDetails()
        chat_detail.serving_mode = OnDemandServingMode(model_id=LLM_MODEL)
        chat_detail.compartment_id = compartmentId
        chat_detail.chat_request = llm_request

        return chat_detail


async def recommed_clothes(gender: GenderEnum , temp: int, rain: bool = False):
	top = TopEnum.Tshirt 
	bottom = BottomEnum.Shorts
	acc = []
 
	if gender == 'M':
		if (temp < 65):
			top = TopEnum.Shirt
			bottom = BottomEnum.Pants
			acc.append(AccEnum.Hat)
			acc.append(AccEnum.Jacket)
		else:
			top = TopEnum.Tshirt
			bottom = BottomEnum.Shorts
			acc.append(AccEnum.Sunglasses)
	else:
		if (temp < 65):
			top = TopEnum.Salvar
			bottom = BottomEnum.Suit
			acc.append(AccEnum.Hat)
			acc.append(AccEnum.Jacket)
		else:
			top = TopEnum.Tshirt
			bottom = BottomEnum.Skirts
			acc.append(AccEnum.Sunglasses)
     
	if rain == True :
		acc.append(AccEnum.Umbrella)

	print (f"top: {top}, bottom: {bottom} acc:[acc]")
  
	return { "Top":top, "Bottom":bottom, "accessories":acc }
	
 
async def guess_weather (city: str, days :int) :
	low =0
	high = 100
	rain = random.choice([True,False])
     
	if city in low_temp :
		low = low_temp[city]
	else:
		low = random.randrange(30,70)
		       
	if city in high_temp :
		high = high_temp[city]
	else:
		high = random.randrange(40,120)

	if high > low :
		low,high = high,low 
		
         
	print (f"low: {low}, high: {high}, rain:{rain}")
	return { "Low" : low, "High": high,"rain": rain}     
         
async def recommed_clothes(gender: GenderEnum , temp: int, rain: bool = False):
	top = TopEnum.Tshirt 
	bottom = BottomEnum.Shorts
	acc = []
 
	if gender == 'M':
		if (temp < 65):
			top = TopEnum.Shirt
			bottom = BottomEnum.Pants
			acc.append(AccEnum.Hat)
			acc.append(AccEnum.Jacket)
		else:
			top = TopEnum.Tshirt
			bottom = BottomEnum.Shorts
			acc.append(AccEnum.Sunglasses)
	else:
		if (temp < 65):
			top = TopEnum.Salvar
			bottom = BottomEnum.Suit
			acc.append(AccEnum.Hat)
			acc.append(AccEnum.Jacket)
		else:
			top = TopEnum.Tshirt
			bottom = BottomEnum.Skirts
			acc.append(AccEnum.Sunglasses)
     
	if rain == True :
		acc.append(AccEnum.Umbrella)
  
	return { "Top":top, "Bottom":bottom, "accessories":acc }




@app.get("/clothes")
async def getClothes(clothes: Annotated[dict, Depends(recommed_clothes)]):
	print ("Clothes Query ")
	return clothes

@app.get("/wether")
async def predict_Weather(guess_weather: Annotated[dict, Depends(guess_weather)]):
	print ("Weather Query ")
	return guess_weather

@app.get("/city")
async def lookup_city(criteria : str) -> str:
	chat_request = get_chat_request();
	chat_request.preamble_override='Answer with teh name of city as json eg { "city" : "denver"}'
	chat_request.message = criteria
	
	llm_payload =get_chat_detail(chat_request)
	llm_response = llm_client.chat(llm_payload)

	return llm_response.data.chat_response.text





if __name__ == "__main__":
	print("running)")
	uvicorn.run("workshop_apis:app", host='127.0.0.1', port=3001, reload=True)

