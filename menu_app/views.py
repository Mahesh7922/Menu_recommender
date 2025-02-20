from django.shortcuts import render

# Create your views here.
import google.generativeai as genai
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, MenuUploadForm
from .models import Menu, Recommendation
import os
import time
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
from google.api_core import exceptions as google_exceptions
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# # Configure Gemini API


# Configure Gemini API
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Create the model
generation_config = {
  "temperature": 0.7,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 65536,
  "response_mime_type": "text/plain",
}
model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
)

def signup(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully!')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'signup.html', {'form': form})

# @login_required
# def home(request):
#     context = {
#         'form': MenuUploadForm(),
#         'recommendation': None  # Initialize recommendation as None
#     }
    
#     if request.method == 'POST':
#         form = MenuUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             try:
#                 # Save the menu
#                 menu = form.save(commit=False)
#                 menu.user = request.user
#                 menu.save()
                
#                 # Process the uploaded file
#                 file_path = menu.menu_file.path
#                 try:
#                     if file_path.endswith('.pdf'):
#                         images = convert_from_path(file_path)
#                         text = ''
#                         for image in images:
#                             text += pytesseract.image_to_string(image)
#                     else:
#                         text = pytesseract.image_to_string(Image.open(file_path))
                    
#                     menu.processed_text = text
#                     menu.save()
#                 except Exception as e:
#                     messages.error(request, f"Error processing file: {str(e)}")
#                     menu.delete()
#                     context['form'] = form
#                     return render(request, 'home.html', context)

#                 # Generate recommendations using Gemini
#                 prompt = f"""
#                 Based on this menu:
#                 {text}
                
#                 Budget: ${form.cleaned_data['budget']}
#                 Preferences: {form.cleaned_data['preferences']}
                
#                 Please suggest a list of items that:
#                 1. Fit within the budget
#                 2. Match the given preferences
#                 3. Provide a balanced meal
                
#                 Format the response as a clear list with prices and brief explanations.
#                 """
                
#                 try:
#                     response = model.generate_content(prompt)
                    
#                     # Save recommendation
#                     recommendation = Recommendation.objects.create(
#                         user=request.user,
#                         menu=menu,
#                         recommendations=response.text
#                     )
                    
#                     messages.success(request, "Menu processed successfully!")
#                     context.update({
#                         'form': MenuUploadForm(),  # Fresh form
#                         'recommendation': recommendation,
#                         'menu': menu
#                     })
                    
#                 except google_exceptions.ResourceExhausted:
#                     messages.error(request, 
#                         "The AI service is currently at capacity. Please try again in a few minutes."
#                     )
#                     menu.delete()
                    
#                 except google_exceptions.InvalidArgument:
#                     messages.error(request, 
#                         "Invalid input. Please check your menu file and try again."
#                     )
#                     menu.delete()
                    
#                 except Exception as e:
#                     messages.error(request, f"An unexpected error occurred: {str(e)}")
#                     menu.delete()
                    
#             except Exception as e:
#                 messages.error(request, f"Error saving menu: {str(e)}")
#         else:
#             messages.error(request, "Please correct the errors in the form.")
#             context['form'] = form
    
#     return render(request, 'home.html', context)

@login_required
def recommendations(request):
    user_recommendations = Recommendation.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'recommendations.html', {'recommendations': user_recommendations})






def upload_to_gemini(path, mime_type=None):
  """Uploads the given file to Gemini."""
  file = genai.upload_file(path, mime_type=mime_type)
  print(f"Uploaded file '{file.display_name}' as: {file.uri}")
  return file

def wait_for_files_active(files):
  """Waits for the given files to be active."""
  print("Waiting for file processing...")
  for name in (file.name for file in files):
    file = genai.get_file(name)
    while file.state.name == "PROCESSING":
      print(".", end="", flush=True)
      time.sleep(10)
      file = genai.get_file(name)
    if file.state.name != "ACTIVE":
      raise Exception(f"File {file.name} failed to process")
  print("...all files ready")
  print()

@login_required
def home(request):
    context = {
        'form': MenuUploadForm(),
        'recommendation': None  # Initialize recommendation as None
    }

    if request.method == 'POST':
        form = MenuUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Save the menu
                menu = form.save(commit=False)
                menu.user = request.user
                menu.save()

                # Upload the menu to Gemini
                if menu.menu_file.path.endswith('.pdf'):
                    uploaded_file = upload_to_gemini(menu.menu_file.path, mime_type="application/pdf")
                else:
                    uploaded_file = upload_to_gemini(menu.menu_file.path)

                # Some files have a processing delay on Gemini. Wait for it to be ready.
                wait_for_files_active([uploaded_file])

                # Generate recommendations using Gemini
                chat_session = model.start_chat(
                    history=[
                        {
                            "role": "user",
                            "parts": [
                                "from a given menu, create a list of items as per your taste and budget",
                            ],
                        },
                        # ... (rest of your chat history - optional, but recommended for context)
                        {
                            "role": "user",
                            "parts": [
                                uploaded_file,
                                f"taste: {form.cleaned_data['preferences']}, budget: {form.cleaned_data['budget']}",
                            ],
                        },
                    ]
                )
                response = chat_session.send_message("Give the menu recommendation based on the user's taste and budget.")
                
                print(response.text)

                # Save recommendation
                recommendation = Recommendation.objects.create(
                    user=request.user,
                    menu=menu,
                    recommendations=response.text
                )

                messages.success(request, "Menu processed successfully!")
                context.update({
                    'form': MenuUploadForm(),  # Fresh form
                    'recommendation': recommendation,
                    'menu': menu
                })

            except google_exceptions.ResourceExhausted:
                messages.error(request,
                                "The AI service is currently at capacity. Please try again in a few minutes."
                                )
                # Handle cleanup, potentially delete menu if needed

            except google_exceptions.InvalidArgument:
                messages.error(request,
                                "Invalid input. Please check your menu file and try again."
                                )
                # Handle cleanup, potentially delete menu if needed

            except Exception as e:
                messages.error(request, f"An unexpected error occurred: {str(e)}")
                # Handle cleanup, potentially delete menu if needed
        else:
            messages.error(request, "Please correct the errors in the form.")
            context['form'] = form

    return render(request, 'home.html', context)