# TraceQL

Structured query DSL engine for JSON and log analysis.

## Features

- field search
- nested JSON search
- aggregate query
- regex query
- similarity search
- AST based query parsing

## Example

level:ERROR cpu

context.cpu_percent >= 80

(level:ERROR OR level:WARNING) cpu_percent >= 80
