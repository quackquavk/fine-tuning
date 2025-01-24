import json

def convert_format():
    # Read the JSONL file
    with open('updated_instruction_dataset.jsonl', 'r') as file:
        # Open output file in write mode
        with open('fine_tuning_dataset.jsonl', 'w') as outfile:
            for line in file:
                entry = json.loads(line)
                
                # Create a more detailed assistant response that includes metadata
                metadata = entry["metadata"]
                assistant_response = f"""Question Details:
Chapter: {metadata['chapter']}
Marks: {metadata['marks']}
Question Type: {metadata['question_type']}
Complexity Level: {metadata['complexity_level']}
Pattern Frequency: {metadata['pattern_frequency']}
Previous Year: {metadata['previous_years']}

Question:
{entry['output']}"""
                
                # Create the conversation format for fine-tuning
                fine_tuning_entry = {
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert Digital Logic and Computer Design question generator."
                        },
                        {
                            "role": "user",
                            "content": entry["instruction"]
                        },
                        {
                            "role": "assistant",
                            "content": assistant_response
                        }
                    ]
                }
                
                # Write each conversation as a separate line
                outfile.write(json.dumps(fine_tuning_entry) + '\n')

if __name__ == "__main__":
    convert_format() 