import json
import random
from collections import defaultdict

def read_questions(file_path):
    questions = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            questions.append(json.loads(line))
    return questions

def analyze_patterns(questions):
    chapter_stats = defaultdict(lambda: {'count': 0, 'marks': [], 'types': set(), 'frequency': set()})
    
    for q in questions:
        meta = q['metadata']
        chapter = meta['chapter']
        chapter_stats[chapter]['count'] += 1
        try:
            marks = int(meta['marks'])
            chapter_stats[chapter]['marks'].append(marks)
        except (ValueError, KeyError):
            # Skip marks that are 'N/A' or missing
            pass
        chapter_stats[chapter]['types'].add(meta['question_type'])
        chapter_stats[chapter]['frequency'].add(meta['pattern_frequency'])
    
    return chapter_stats

def generate_system_message():
    return {
        "role": "system",
        "content": "You are an expert Digital Logic and Computer Design AI that can both generate questions and predict examination trends. You analyze patterns in past questions to predict future trends and generate high-quality questions."
    }

def generate_interactive_prompt(question, chapter_stats):
    meta = question['metadata']
    chapter = meta['chapter']
    stats = chapter_stats[chapter]
    
    # Create context-aware prompts
    prompts = [
        f"Based on the {meta['pattern_frequency']} occurrence of {meta['question_type']} questions in {chapter}, analyze this question: {question['question']}",
        f"This {meta.get('marks', 'N/A')}-mark question from {meta['previous_years']} tests {chapter} concepts. How might similar questions appear in future exams?",
        f"Given the {meta['complexity_level']} complexity of this {chapter} question, what variations could we expect in upcoming exams?",
        "Predict potential variations of this question that could appear in future exams, considering recent technological trends.",
        "How can we connect this theoretical concept to modern digital design applications?",
        "What practical examples would help understand this concept better?",
        "How has this type of question evolved over the years, and what future trends might we see?"
    ]
    
    # Create an enhanced question entry
    enhanced_question = {
        "messages": [
            generate_system_message(),
            {
                "role": "user",
                "content": random.choice(prompts)
            }
        ],
        "original_question": question,
        "metadata": {
            "chapter": chapter,
            "question_type": meta['question_type'],
            "marks": meta.get('marks', 'N/A'),
            "pattern_frequency": meta['pattern_frequency'],
            "complexity_level": meta['complexity_level'],
            "chapter_statistics": {
                "total_questions": stats['count'],
                "average_marks": sum(stats['marks']) / len(stats['marks']) if stats['marks'] else 'N/A',
                "question_types": list(stats['types']),
                "frequency_patterns": list(stats['frequency'])
            }
        }
    }
    
    return enhanced_question

def main():
    # Read original questions
    questions = read_questions('questions.jsonl')
    
    # Analyze patterns
    chapter_stats = analyze_patterns(questions)
    
    # Generate enhanced dataset
    enhanced_questions = []
    for question in questions:
        enhanced_question = generate_interactive_prompt(question, chapter_stats)
        enhanced_questions.append(enhanced_question)
    
    # Save enhanced dataset
    with open('enhanced_questions.jsonl', 'w', encoding='utf-8') as f:
        for q in enhanced_questions:
            f.write(json.dumps(q, ensure_ascii=False) + '\n')
    
    print(f"Enhanced {len(enhanced_questions)} questions with interactive prompts")
    print("Dataset saved to enhanced_questions.jsonl")

if __name__ == "__main__":
    main() 