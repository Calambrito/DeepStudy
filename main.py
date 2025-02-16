import pygame
import pygame_gui
import threading

from langchain_ollama import OllamaLLM
from rag import RAG
from interaction import Interaction

pygame.init()

# --- Window Setup ---
window_width = 1280
window_height = 720
window_surface = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Chatbot GUI")
background_color = pygame.Color(41, 41, 41)

manager = pygame_gui.UIManager((window_width, window_height), 'theme.json')

# --- Font Setup ---
font_size = 30
font = pygame.font.SysFont(None, font_size)

# --- UI Elements ---
chat_box_height_percent = 0.80
input_box_height = 100
margin = 20

chat_box_rect = pygame.Rect(margin, margin, window_width - 2 * margin, window_height * chat_box_height_percent - margin)
input_box_rect = pygame.Rect(margin, chat_box_rect.bottom + margin, window_width - 2 * margin, input_box_height)

chat_log_text_box = pygame_gui.elements.UITextBox(
    relative_rect=chat_box_rect,
    html_text="",
    manager=manager,
    object_id="#chat_log_text_box"
)
chat_log_text_box.scrollable = True

input_text_entry = pygame_gui.elements.UITextEntryLine(
    relative_rect=input_box_rect,
    manager=manager,
    object_id="#input_text_entry"
)

# --- Conversation History ---
conversation_history = []

# --- Ollama and RAG Setup ---
model = OllamaLLM(model="llama3.2")

# --- Custom Event for LLM Response ---
LLM_RESPONSE_EVENT = pygame.event.custom_type()

# --- Function to Process Query in a Thread ---
def process_query_threaded(query, interaction_obj):
    response = RAG(query, model)
    pygame.event.post(pygame.event.Event(LLM_RESPONSE_EVENT, interaction=interaction_obj, message=response))

# --- Function to update chat log ---
def update_chat_log():
    chat_log_html = ""
    for interaction in conversation_history:
        user_str = interaction.getUserStr()
        llm_str = interaction.getLLMStr()

        if user_str:
            chat_log_html += f"<font color=#ADD8E6>User:</font> {user_str}<br>"
        if llm_str:
            chat_log_html += f"<font color=#90EE90>Llama:</font> {llm_str}<br>"

    chat_log_text_box.set_text(chat_log_html)

# --- Game Loop ---
is_running = True
clock = pygame.time.Clock()

while is_running:
    time_delta = clock.tick(60)/1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False

        if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            if event.ui_element == input_text_entry:
                query_text = input_text_entry.get_text()
                input_text_entry.set_text("")
                if query_text.lower() == "bye":
                    is_running = False
                else:
                    interaction = Interaction(user=query_text)
                    conversation_history.append(interaction)
                    update_chat_log() # Updates chat log, but no auto-scroll

                    thread = threading.Thread(target=process_query_threaded, args=(query_text, interaction))
                    thread.start()

        if event.type == LLM_RESPONSE_EVENT:
            llama_response = event.message
            interaction_obj = event.interaction
            interaction_obj.llm = llama_response
            update_chat_log() # Updates chat log, but no auto-scroll

        manager.process_events(event)
        manager.update(time_delta)

    window_surface.fill(background_color)
    manager.draw_ui(window_surface)
    pygame.display.update()

pygame.quit()