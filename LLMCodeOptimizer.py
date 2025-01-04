import subprocess
import requests
import time
import re

class LLMCodeOptimizer:
    def __init__(self, api_url="http://localhost:1234/v1/chat/completions"):
        self.api_url = api_url
        self.best_execution_time = float('inf')
        self.champion_code = None

    def run_code(self, code_to_test):
        if "<userStyle>" in code_to_test:
            return False, None, "Invalid response"

        # Ensure necessary imports
        if 'math' in code_to_test and 'import math' not in code_to_test:
            code_to_test = "import math\n" + code_to_test

        try:
            with open('test_implementation.py', 'w') as f:
                f.write(code_to_test)

            start_time = time.time()
            result = subprocess.run(['python', 'test_implementation.py'],
                                    capture_output=True, text=True, timeout=30)
            execution_time = time.time() - start_time

            print(f"Debug - Raw output: '{result.stdout}'")
            print(f"Debug - Expected: '{self.expected_output}'")

            if result.returncode == 0:
                try:
                    output = result.stdout.strip()
                    # Convert both to strings, strip whitespace and compare
                    if str(output).strip() == str(self.expected_output).strip():
                        return True, execution_time, output
                    return False, None, f"Incorrect output: {output}"
                except ValueError:
                    # Clean the output before giving up
                    cleaned_output = result.stdout.strip()
                    if cleaned_output == str(self.expected_output).strip():
                        return True, execution_time, cleaned_output
                    return False, None, f"Invalid output format: {result.stdout}"
            return False, None, f"Execution error: {result.stderr}"

        except subprocess.TimeoutExpired:
            return False, None, "Timeout: Code took too long to execute"
        except Exception as e:
            return False, None, f"Error running code: {e}"

    def clean_code(self, code):
        """Clean and validate the code structure."""
        lines = code.split('\n')
        cleaned_lines = []
        in_function = False
        
        for line in lines:
            # Skip markdown code blocks and empty lines
            if line.strip().startswith('```') or not line.strip():
                continue
            
            # Skip any existing print statements
            if 'print(result)' in line or 'print(' in line:
                continue
                
            if line.startswith('def '):
                in_function = True
            elif in_function and not line.startswith(' '):
                in_function = False
                
            cleaned_lines.append(line)
        
        # Add test code at the correct indentation level
        test_code = f"""
n = {self.test_n}
result = calculate_sum(n)
print(result)"""
        
        return '\n'.join(cleaned_lines) + test_code

    def query_llm(self, prompt):
        headers = {"Content-Type": "application/json"}
        data = {
            "messages": [{"role": "user", "content": prompt}],
            "model": "local-model",
            "temperature": 0.1
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            content = response.json()['choices'][0]['message']['content'].strip()
            
            code_match = re.search(r'```python\n(.*?)\n```', content, re.DOTALL)
            if code_match:
                code = code_match.group(1)
            else:
                code = content
                
            return self.clean_code(code)
            
        except Exception as e:
            print(f"Error querying LLM: {e}")
            return None

    def optimize_function(self, initial_code, problem_prompt, test_n, expected_output, max_iterations=5):
        print("Starting optimization process...")
        self.test_n = test_n
        self.expected_output = expected_output
        self.champion_code = initial_code
        
        # Split into two different prompt templates
        base_prompt = f"""
{problem_prompt}

Return clean, runnable Python code with proper indentation.
"""

        improvement_prompt = f"""
{problem_prompt}

Here is the current best implementation:

{{current_code}}

This code runs in {{current_time:.4f}} seconds.

Please optimize this code for better performance while maintaining correctness.
Return clean, runnable Python code with proper indentation.
"""

        # Initial run to establish baseline
        success, execution_time, output = self.run_code(initial_code)
        if success:
            print(f"Initial implementation time: {execution_time:.4f}s")
            print(f"Initial output: {output}")
            self.best_execution_time = execution_time
            self.champion_code = initial_code
            has_working_solution = True
        else:
            has_working_solution = False
            self.best_execution_time = float('inf')

        for iteration in range(max_iterations):
            print(f"\nIteration {iteration + 1}/{max_iterations}")

            # Choose prompt based on whether we have a working solution
            if has_working_solution:
                prompt = improvement_prompt.format(
                    current_code=self.champion_code,
                    current_time=self.best_execution_time
                )
            else:
                prompt = base_prompt

            new_code = self.query_llm(prompt)
            
            if not new_code:
                print("Failed to generate valid code")
                continue

            print("Testing new implementation...")
            success, execution_time, output = self.run_code(new_code)

            if success:
                print(f"Execution time: {execution_time:.4f}s")
                print(f"Output: {output}")
                has_working_solution = True

                if execution_time < self.best_execution_time:
                    print(f"New champion found! Time: {execution_time:.4f}s")
                    print("\nChampion code:")
                    print(new_code)  # Added this line
                    self.best_execution_time = execution_time
                    self.champion_code = new_code
            else:
                print(f"Implementation failed: {output}")

        return self.champion_code, self.best_execution_time

if __name__ == "__main__":
    # Try to load previous best implementation
    try:
        with open('final_implementation.py', 'r') as f:
            lines = f.readlines()
            if lines and lines[0].startswith('# Test runtime:'):
                # Extract previous best runtime
                runtime_str = lines[0].strip()
                prev_best_time = float(runtime_str.split(':')[1].replace('seconds', '').strip())
                print(f"Found previous implementation with runtime: {prev_best_time:.4f}s")
                
                # Use the rest of the file as initial code
                initial_code = ''.join(lines[1:])
            else:
                raise FileNotFoundError  # Handle like file doesn't exist if format is wrong
    except (FileNotFoundError, IndexError):
        # Use default initial implementation if no valid previous implementation exists
        initial_code = """
def calculate_sum(n):
    total = 0
    for i in range(n):
        total += i
    return total

n = 5
result = calculate_sum(n)
print(result)
"""
        print("Starting with default initial implementation")

    # Problem definition for prime number sum
    problem_prompt = """
Write efficient Python code for calculating the sum of the first n prime numbers.

Requirements:
1. Include all necessary imports (math)
2. Include an optimized isprime() function
3. Main function must be named calculate_sum(n)
4. For n=10000, must output exactly 496165411
5. Code must be complete and runnable"""

    optimizer = LocalLLMOptimizer()
    best_code, best_time = optimizer.optimize_function(
        initial_code=initial_code,
        problem_prompt=problem_prompt,
        test_n=10000,
        expected_output="496165411",
        max_iterations=20
    )

    print("\nFinal Results:")
    print("Best implementation found:")
    print(best_code)
    print(f"Best execution time: {best_time:.4f}s")

    # Save the best implementation with runtime comment
    with open('final_implementation.py', 'w') as f:
        f.write(f'# Test runtime: {best_time:.4f} seconds\n')
        f.write(best_code)
    print("\nBest implementation saved to 'final_implementation.py'")
    print("You can test it with different values of n by modifying the n value in the file")