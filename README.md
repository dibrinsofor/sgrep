## SGrep

SGrep is a python syntax-oriented search tool that recursively searches directories for our regex-like query language.

![Quick example of Sgrep](/static/sgrep%20landing.png)

Inspired by [Andy Friesen](https://andyfriesen.com/)'s work. 

<!-- Another interesting projects is [Semantic Grep](https://github.com/arunsupe/semantic-grep). -->

#### (Install and) Use
```zsh
>>> pip install -r requirements.txt
>>> python -m src.main [PATTERN] [FILEPATH]
```

#### Sgrep vs grep-like tools

| Feature | Sgrep | grep/rg | Advantage |
|---------|------------|---------|-----------|
| Syntax Awareness | Yes - understands code structure | No - line-based only | Our syntax provides accurate matches for nested structures |
| Performance | See performance analysis below | Generally very fast | Depends on specific use case |


#### Performance
Running `rg` (rg '`def`') and and `sgrep`(sgrep '`def`') against this project results in these times on average.

```python
rg "def"  0.00s user 0.02s system 65% cpu 0.032 total

python -m src.main 'def'  0.85s user 0.24s system 339% cpu 0.321 total
```

#### Sgrep Syntax

##### Compound Statement Keywords
```python
# Supports all python 3.8+ keywords including a special case "call"

def          # Matches function definitions
call         # Matches function applications
class        # Matches class definitions
import      # Matches import statements
lambda      # Matches lambda expressions
...
```

##### Identifier Patterns
```python
$some_name  # Matches specific identifier 'some_name'
$*          # Matches all identifiers
$some*      # Matches identifiers starting with "some"
$*some      # Matches identifiers ending with "some"
```

##### Function Patterns
```python
# Function Calls
call             # Matches all function calls
call (args=5)       # Match calls with 5 arguments
call (^$some_arg)  # Match calls whose first argument is 'some_arg'
call (args=3, $some_arg, ...)  # Match function calls with three arguments where one is 'some_arg'

# Function Definitions
def              # Matches all function definitions
def (args=5)     # Function with 5 parameters
def (^$self)     # Match function definitions whose first parameter is 'self'
```

#### TODO
- [ ] Fix failing cases
- [ ] Type Directed Queries
- [ ] Cache scan results
- [ ] Better context for ident queries