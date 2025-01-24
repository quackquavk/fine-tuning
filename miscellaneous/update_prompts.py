import json

def update_file(input_file, output_file):
    new_lines = []
    new_system_prompt = "You are an expert Digital Logic and Computer Design AI that can both generate questions and predict examination trends. You analyze patterns in past questions to predict future trends and generate high-quality questions."
    
    with open(input_file, 'r') as f:
        for line in f:
            try:
                data = json.loads(line.strip())
                # Update the system prompt
                data['messages'][0]['content'] = new_system_prompt
                # Add trend analysis if it's not already there
                if 'Pattern Analysis' not in data['messages'][-1]['content']:
                    question_content = data['messages'][-1]['content']
                    # Add trend analysis section
                    trend_analysis = "\n\nPattern Analysis:\n1. Similar Questions Likely to Appear:\n- Questions on similar concepts with different variations\n- Questions combining this topic with related concepts\n\n2. Future Trends:\n- Increasing focus on practical applications\n- Integration with modern digital systems\n- Questions combining multiple concepts\n\nJustification:\n- Based on past year patterns\n- Industry relevance\n- Current examination trends"
                    data['messages'][-1]['content'] = question_content + trend_analysis
                new_lines.append(json.dumps(data))
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON line: {line.strip()}")
    
    with open(output_file, 'w') as f:
        for line in new_lines:
            f.write(line + '\n')

# Update both files
update_file('fine_tuning_dataset.jsonl', 'updated_fine_tuning_dataset.jsonl')
update_file('combined_fine_tuning_dataset.jsonl', 'updated_combined_dataset.jsonl') 