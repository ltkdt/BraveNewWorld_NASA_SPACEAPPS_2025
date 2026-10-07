from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


#Text generation example 
'''
def generate_product_description(product_name, features, target_audience):
   response = client.responses.create(
       model="gpt-4o",
       instructions="You are a professional copywriter specialized in creating concise, compelling product descriptions. Focus on benefits rather than just features.",
       input=f"""
       Create a product description for {product_name}.
       Key features:
       - {features[0]}
       - {features[1]}
       - {features[2]}
       Target audience: {target_audience}
       Keep it under 150 words.
       """,
       temperature=0.7,
       max_output_tokens=200
   )
  
   return response.output_text

# Example usage
headphones_desc = generate_product_description(
   "NoiseGuard Pro Headphones",
   ["Active noise cancellation", "40-hour battery life", "Memory foam ear cushions"],
   "Business travelers and remote workers"
)

print(headphones_desc)
'''

def chatbot_answer(question):
   print("InSAR technique")
  
   stream = client.responses.create(
       model="gpt-4o",
       instructions="""You are an expert in satellite remote sensing and geospatial analysis, especially InSAR technique and its application on tracking land subsidence and erosion.
         Answer the question of the user about this topic and refuse to answer if the question is not related to this topic.
         """,
       input=question,
       stream=True,
       temperature=0.3,
       max_output_tokens=500
   )
  
   full_response = ""
   print("\nAnalysis results:")
   for event in stream:
       if event.type == "response.output_text.delta":
           print(event.delta, end="")
           full_response += event.delta
       elif event.type == "response.error":
           print(f"\nError occurred: {event.error}")
  
   return full_response

# Example with a complex customer review
feedback = """
I've been using the SmartHome Hub for about 3 months now. The voice recognition is fantastic
and the integration with my existing devices was mostly seamless. However, the app crashes
at least once a day, and the night mode feature often gets stuck until I restart the system.
Customer support was helpful but couldn't fully resolve the app stability issues.
"""

# analysis_result = analyze_customer_feedback(feedback)

def chatbot_analyze_image(image_path_or_url, question, is_url=False):
   """
   Analyze an image with the Responses API.

   Parameters
   - image_path_or_url: local file path or URL to the image
   - question: text question about the image
   - is_url: if True, treat the first argument as a remote URL and send the URL to the API

   Notes
   - If you pass a URL, the function sends the URL (no local file needed).
   - If you pass a local path (is_url=False), the function opens the file and streams it as before.
   """
   stream = None
   full_response = ""

   if is_url:
       # Send the image URL directly in the input payload. Many SDKs accept a field like
       # "image_url" or a structured input; this sends a simple dict with the URL and question.
       # If your specific client or model requires a different shape (e.g. explicit
       # content blocks), adapt accordingly.
       stream = client.responses.create(
           model="gpt-4o-vision",
           instructions="""You are an expert in satellite remote sensing and geospatial analysis, especially InSAR technique and its application on tracking land subsidence and erosion.
         Answer the question of the user about this topic and refuse to answer if the question is not related to this topic.
         """,
           input={
               "image_url": image_path_or_url,
               "question": question
           },
           stream=True,
           temperature=0.3,
           max_output_tokens=500
       )
   else:
       # Local file path: open and send the file-like object (original behavior)
       with open(image_path_or_url, "rb") as image_file:
           stream = client.responses.create(
               model="gpt-4o-vision",
               instructions="""You are an expert in satellite remote sensing and geospatial analysis, especially InSAR technique and its application on tracking land subsidence and erosion.
         Answer the question of the user about this topic and refuse to answer if the question is not related to this topic.
         """,
               input={
                   "image": image_file,
                   "question": question
               },
               stream=True,
               temperature=0.3,
               max_output_tokens=500
           )

   print("\nAnalysis results:")
   for event in stream:
       if event.type == "response.output_text.delta":
           print(event.delta, end="")
           full_response += event.delta
       elif event.type == "response.error":
           print(f"\nError occurred: {event.error}")

   return full_response