# LLMCodeOptimizer

A Python tool that uses local Large Language Models (LLMs) to automatically optimize code performance while maintaining functional correctness.

## Overview

LLMCodeOptimizer is a tool that leverages LLMs to iteratively improve the performance of Python functions. It takes an initial implementation, tests it for correctness, and then uses an LLM to generate potentially faster versions while ensuring the output remains correct.

## Features

- Automated code optimization using LLM suggestions
- Performance benchmarking and verification
- Automatic correctness testing
- Save/load functionality for best implementations
- Progressive improvement through multiple iterations
- Configurable timeout and iteration limits
- Clean code validation and formatting

## Requirements

- Python 3.x
- `requests` library
- A local LLM server running on port 1234 (default)

## Installation

1. Clone the repository
2. Install required dependencies:

```
pip install requests
```

## Usage

Basic usage example:

``` python
from llm_code_optimizer import LLMCodeOptimizer

# Define your initial code
initial_code = """
def calculate_sum(n):
   total = 0
   for i in range(n):
       total += i
   return total
"""

# Define your optimization problem
problem_prompt = """
Write efficient Python code for calculating the sum of the first n prime numbers.
Requirements:
1. Include all necessary imports (math)
2. Include an optimized isprime() function
3. Main function must be named calculate_sum(n)
4. For n=10000, must output exactly 496165411
5. Code must be complete and runnable
"""

# Create optimizer instance
optimizer = LLMCodeOptimizer()

# Run optimization
best_code, best_time = optimizer.optimize_function(
   initial_code=initial_code,
   problem_prompt=problem_prompt,
   test_n=10000,
   expected_output="496165411",
   max_iterations=20
)
```

## Configuration

The tool can be configured by modifying these parameters:

- `api_url`: URL of your local LLM server (default: "http://localhost:1234/v1/chat/completions")
- `max_iterations`: Maximum number of optimization attempts (default: 5)
- `timeout`: Maximum execution time for testing implementations (default: 30 seconds)

## How It Works

1. Takes an initial implementation and problem specification
2. Runs the code to establish a baseline performance
3. Queries the LLM with the current best implementation and asks for optimizations
4. Tests new implementations for correctness and performance
5. Keeps track of the best performing version
6. Saves the optimized implementation to a file

## Example Applications

- Optimizing mathematical computations
- Improving algorithm efficiency
- Enhancing data processing functions
- Optimizing resource-intensive calculations

## Limitations

- Requires a local LLM server
- Optimization quality depends on the LLM's capabilities
- May not find global optimal solutions
- Limited to Python code optimization

## Contributing

Contributions are welcome! Please feel free to submit pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- This tool was inspired by the need for automated code optimization
- Thanks to the open-source community for various optimization techniques and patterns
