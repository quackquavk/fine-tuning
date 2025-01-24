import json
import re
from typing import List, Dict, Optional, Tuple
import random
from difflib import get_close_matches

# Define the valid categories
VALID_CHAPTERS = {
    "Binary System",
    "Boolean Algebra and Logic Gates",
    "Simplification of Boolean Functions",
    "Combinational Logic", 
    "Sequential Logic",
    "Digital Integrated Circuit"
}

# Define common variations and abbreviations
CHAPTER_ALIASES = {
    "boolean": "Boolean Algebra and Logic Gates",
    "boolean algebra": "Boolean Algebra and Logic Gates",
    "logic gates": "Boolean Algebra and Logic Gates",
    "binary": "Binary System",
    "simplification": "Simplification of Boolean Functions",
    "boolean functions": "Simplification of Boolean Functions",
    "combinational": "Combinational Logic",
    "sequential": "Sequential Logic",
    "digital": "Digital Integrated Circuit",
    "integrated circuit": "Digital Integrated Circuit",
    "digital circuit": "Digital Integrated Circuit"
}

VALID_DIFFICULTIES = {"low", "medium", "high"}
VALID_FREQUENCIES = {"yearly", "frequent", "occasional"}

# Conversation context
class ConversationContext:
    def __init__(self):
        self.last_chapter = None
        self.last_responses = []
        self.current_response_index = 0
    
    def update_context(self, chapter: str, responses: List[Dict]):
        self.last_chapter = chapter
        self.last_responses = responses
        self.current_response_index = 1  # Start from 1 since we've shown the first response
    
    def clear_context(self):
        self.last_chapter = None
        self.last_responses = []
        self.current_response_index = 0

# Create a global context
context = ConversationContext()

def load_dataset(file_path: str) -> List[Dict]:
    """Load and parse the JSONL dataset."""
    dataset = []
    with open(file_path, 'r') as f:
        for line in f:
            dataset.append(json.loads(line.strip()))
    return dataset

def detect_chapter(user_input: str) -> Optional[str]:
    """Detect which chapter the user is asking about using flexible matching."""
    user_input_lower = user_input.lower()
    
    # First try exact matches
    for chapter in VALID_CHAPTERS:
        if chapter.lower() in user_input_lower:
            return chapter
    
    # Then try aliases
    for alias, chapter in CHAPTER_ALIASES.items():
        if alias in user_input_lower:
            return chapter
    
    # If no exact match or alias found, try fuzzy matching
    # Create a list of all possible matches (chapter names and aliases)
    all_possible_matches = list(VALID_CHAPTERS) + list(CHAPTER_ALIASES.keys())
    
    # Get words from user input
    user_words = user_input_lower.split()
    
    # Try to match each word from user input
    for word in user_words:
        if len(word) < 4:  # Skip very short words
            continue
        
        # Get close matches for this word
        matches = get_close_matches(word, all_possible_matches, n=1, cutoff=0.8)
        if matches:
            matched_term = matches[0]
            # If matched an alias, return its chapter
            if matched_term in CHAPTER_ALIASES:
                return CHAPTER_ALIASES[matched_term]
            # If matched a chapter name, return the exact chapter name from VALID_CHAPTERS
            for chapter in VALID_CHAPTERS:
                if chapter.lower() == matched_term.lower():
                    return chapter
    
    return None

def detect_difficulty(user_input: str) -> Optional[str]:
    """Detect difficulty level from user input."""
    user_input_lower = user_input.lower()
    for difficulty in VALID_DIFFICULTIES:
        if difficulty in user_input_lower:
            return difficulty
    return None

def detect_frequency(user_input: str) -> Optional[str]:
    """Detect frequency pattern from user input."""
    user_input_lower = user_input.lower()
    for frequency in VALID_FREQUENCIES:
        if frequency in user_input_lower:
            return frequency
    # Add common synonyms
    if "regular" in user_input_lower:
        return "frequent"
    if "annual" in user_input_lower:
        return "yearly"
    return None

def detect_marks(user_input: str) -> Optional[int]:
    """Detect marks from user input."""
    marks_pattern = r'(\d+)\s*marks?'
    match = re.search(marks_pattern, user_input.lower())
    if match:
        return int(match.group(1))
    return None

def detect_year(user_input: str) -> Optional[str]:
    """Detect year mentioned in the user input."""
    # Match both 4-digit years and 2-digit years
    year_patterns = [
        r'\b20[0-2]\d\b',  # Matches years 2000-2029
        r"'?\b\d{2}\b"     # Matches two-digit years with optional apostrophe
    ]
    
    for pattern in year_patterns:
        match = re.search(pattern, user_input)
        if match:
            year = match.group()
            # Convert 2-digit year to 4-digit year
            if len(year) == 2 or (len(year) == 3 and year[0] == "'"):  # Handle '23 format
                year = year.strip("'")
                return f"20{year}"
            return year
    return None

def find_relevant_responses(dataset: List[Dict], chapter: str, user_input: str) -> List[Dict]:
    """Find relevant responses from the dataset based on various filters."""
    difficulty = detect_difficulty(user_input)
    frequency = detect_frequency(user_input)
    marks = detect_marks(user_input)
    year = detect_year(user_input)
    
    relevant_responses = []
    
    for item in dataset:
        metadata = item["metadata"]
        
        # Always check chapter match if specified
        if chapter and metadata["chapter"] != chapter:
            continue
            
        # Check year if specified
        if year and metadata["previous_years"] != year:
            continue
            
        # Only check other filters if they were specified in the query
        if difficulty and metadata["complexity_level"].lower() != difficulty:
            continue
            
        if frequency and metadata["pattern_frequency"].lower() != frequency:
            continue
            
        if marks and int(metadata["marks"]) != marks:
            continue
            
        relevant_responses.append(item)
    
    # Shuffle the responses to get random ones each time
    random.shuffle(relevant_responses)
    return relevant_responses

def is_affirmative(user_input: str) -> bool:
    """Check if the user's response is affirmative."""
    affirmative_responses = {'yes', 'yeah', 'sure', 'okay', 'ok', 'y', 'yep', 'show', 'next'}
    return user_input.lower() in affirmative_responses

def handle_followup(user_input: str) -> Optional[str]:
    """Handle follow-up responses like 'yes', 'show me more', etc."""
    if not context.last_chapter or not context.last_responses:
        return None
        
    if not is_affirmative(user_input):
        return None
    
    if context.current_response_index >= len(context.last_responses):
        return f"I've shown you all the questions I have from {context.last_chapter}. Would you like to try questions from a different chapter?"
    
    # Get the next response
    metadata = context.last_responses[context.current_response_index]["metadata"]
    question = context.last_responses[context.current_response_index]["output"]
    
    # Increment the index for next time
    context.current_response_index += 1
    
    # Choose a template for showing another question
    templates = [
        f"Here's another question from {context.last_chapter}:",
        f"Sure! Here's the next question:",
        f"Here's one more question for you:",
        f"I've got another question from {context.last_chapter}:"
    ]
    
    response = random.choice(templates) + f"\n\n{question} [{metadata['marks']} marks]\n\n"
    
    # Add follow-up prompt if there are more questions
    if context.current_response_index < len(context.last_responses):
        followup_templates = [
            "Would you like to see another one?",
            "Should I show you another question?",
            "Would you like to continue with more questions?",
            "Shall I show you another question from this chapter?"
        ]
        response += random.choice(followup_templates)
    else:
        response += "That's all the questions I have from this chapter. Would you like to try questions from a different chapter?"
    
    return response

def get_introduction_response(user_input: str) -> Optional[str]:
    """Handle introductory and informational prompts."""
    user_input_lower = user_input.lower().strip('?!. ')
    
    # Greetings
    greetings = {'hello', 'hi', 'hey', 'greetings', 'hola'}
    if user_input_lower in greetings:
        greeting_templates = [
            "Hello! I'm your Digital Electronics study assistant. I can help you practice questions from various chapters. What would you like to study?",
            "Hi there! I'm here to help you with Digital Electronics questions. Which chapter would you like to practice?",
            "Hello! I can provide you with practice questions from Digital Electronics. Would you like to see the available chapters?"
        ]
        return random.choice(greeting_templates)
    
    # Identity/capability questions
    identity_patterns = {
        'what are you': "I'm a Digital Electronics study assistant designed to help you practice questions from various chapters. I can provide questions based on difficulty level, marks, and frequency of appearance.",
        'who are you': "I'm your Digital Electronics practice companion. I can help you with questions from different chapters, with various difficulty levels and marks.",
        'what can you do': f"I can help you practice Digital Electronics by providing questions from these chapters:\n\n{', '.join(VALID_CHAPTERS)}\n\nYou can specify:\n- Difficulty level (low/medium/high)\n- Marks (e.g., '5 marks')\n- Frequency (yearly/frequent/occasional)",
        'what model': "I'm a specialized Digital Electronics practice assistant, designed to help you study with questions from previous years and various topics.",
        'help': f"I can help you practice Digital Electronics questions. You can:\n1. Ask for questions from specific chapters\n2. Specify difficulty (low/medium/high)\n3. Request questions with specific marks\n4. Ask for frequently appearing questions\n\nFor example, try: 'Give me a medium difficulty question from Binary System'"
    }
    
    for pattern, response in identity_patterns.items():
        if pattern in user_input_lower:
            return response
            
    return None

def generate_response(user_input: str, dataset_path: str = "updated_instruction_dataset.jsonl") -> str:
    """Generate a response based on user input."""
    # First check for introductory/informational prompts
    intro_response = get_introduction_response(user_input)
    if intro_response:
        return intro_response
        
    # Then check if this is a follow-up response
    followup_response = handle_followup(user_input)
    if followup_response:
        return followup_response
        
    # If not a follow-up, clear the context and process as new query
    context.clear_context()
    
    dataset = load_dataset(dataset_path)
    
    # Check if this is a year-based query without specific chapter
    year = detect_year(user_input)
    chapter = detect_chapter(user_input)
    
    if year and not chapter:
        # Find questions from any chapter for that year
        relevant_responses = find_relevant_responses(dataset, None, user_input)
        if not relevant_responses:
            return f"I couldn't find any questions from the {year} exam. Would you like to try a different year or specify a chapter?"
            
        # Update conversation context
        context.update_context("all chapters", relevant_responses)
        
        # Create year-specific response
        opening_templates = [
            f"Here's a question from the {year} exam:",
            f"I found this question from {year}:",
            f"This question appeared in {year}:",
        ]
        
        response = random.choice(opening_templates) + "\n\n"
        metadata = relevant_responses[0]["metadata"]
        question = relevant_responses[0]["output"]
        
        # Include chapter information since it's a year-based query
        response += f"Chapter: {metadata['chapter']}\n"
        response += f"Question: {question} [{metadata['marks']} marks]\n\n"
        
        if len(relevant_responses) > 1:
            followup_templates = [
                f"Would you like to see another question from {year}?",
                f"I have more questions from the {year} exam. Would you like to see them?",
                f"Should I show you another question from {year}?"
            ]
            response += random.choice(followup_templates)
        
        return response
    
    # Process normal chapter-based query
    if not chapter:
        return "I'd be happy to help you with a question. Which chapter would you like to practice? You can choose from: " + ", ".join(VALID_CHAPTERS)
    
    # Find relevant responses
    relevant_responses = find_relevant_responses(dataset, chapter, user_input)
    
    if not relevant_responses:
        response_parts = []
        difficulty = detect_difficulty(user_input)
        frequency = detect_frequency(user_input)
        marks = detect_marks(user_input)
        
        if difficulty:
            response_parts.append(f"difficulty level '{difficulty}'")
        if frequency:
            response_parts.append(f"frequency '{frequency}'")
        if marks:
            response_parts.append(f"{marks} marks")
        if year:
            response_parts.append(f"year {year}")
            
        if response_parts:
            filters_str = ", ".join(response_parts)
            return f"I couldn't find any questions from {chapter} matching {filters_str}. Would you like me to show you other questions from this chapter?"
        return f"I don't have any questions from {chapter} at the moment. Would you like to try a different chapter?"

    # Update conversation context
    context.update_context(chapter, relevant_responses)
    
    # Choose a random template for the initial response
    opening_templates = [
        f"Here's a question from {chapter}:",
        f"I've found this question from {chapter} for you:",
        f"Let me share this question from {chapter}:",
        f"Here's a relevant question from {chapter}:",
    ]
    
    response = random.choice(opening_templates) + "\n\n"
    
    # Add the first relevant response
    metadata = relevant_responses[0]["metadata"]
    question = relevant_responses[0]["output"]
    
    # Format the question with marks and year
    response += f"{question} [{metadata['marks']} marks"
    if year or "year" in user_input.lower():
        response += f", appeared in {metadata['previous_years']}"
    response += "]\n\n"
    
    # Add follow-up prompt if there are more questions
    if len(relevant_responses) > 1:
        followup_templates = [
            "Would you like to see another question?",
            "Should I show you another question?",
            "Would you like to try another question?",
            "Shall I show you more questions from this chapter?"
        ]
        response += random.choice(followup_templates)
    
    return response

def main():
    """Main function to test the chat response system."""
    print("Welcome to the Digital Electronics Chat Assistant!")
    print("Ask me anything about these chapters:")
    print("\n".join(VALID_CHAPTERS))
    print("\nYou can specify:")
    print("- Difficulty (low, medium, high)")
    print("- Frequency (yearly, frequent, occasional)")
    print("- Marks (e.g., '5 marks')")
    print("\nExample: 'Give me a medium difficulty question from Binary System that appears frequently'")
    print("\nType 'quit' to exit")
    
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() == 'quit':
            break
            
        response = generate_response(user_input)
        print("\nAssistant:", response)

if __name__ == "__main__":
    main() 