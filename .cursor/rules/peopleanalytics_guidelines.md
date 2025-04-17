# People Analytics Project Guidelines

This document serves as the central source of truth for development guidelines on the People Analytics project, based on accumulated learnings. All changes to the project should conform to these guidelines.

## DO NOT

- **DO NOT add new CLI arguments**: The CLI interface should maintain its existing argument structure. Avoid adding new flags, options, or parameters to command-line interfaces.
  
- **DO NOT introduce new libraries or dependencies** without clear justification and alignment with existing codebase patterns.

- **DO NOT create test scripts or additional entry points** outside the established entry points (cli.py).

- **DO NOT duplicate functionality** that exists elsewhere in the codebase.

- **DO NOT modify core interfaces** in ways that would break backward compatibility.

- **DO NOT refactor working code** unless specifically requested or there is a critical performance/maintenance reason.

- **DO NOT add comments to code** unless the code is complex and requires additional context, or it's specifically requested.

## DO

- **DO follow existing code structure and patterns**: When adding new functionality, study and mimic the existing patterns in the codebase.

- **DO integrate new features directly into existing modules** rather than creating new standalone modules.

- **DO match the existing naming conventions** for classes, methods, variables, and files.

- **DO leverage existing utility functions and classes** instead of reimplementing similar functionality.

- **DO ensure proper error handling** follows existing patterns in the codebase.

- **DO maintain the existing flow of data processing** while extending functionality.

- **DO make the sync command the primary point of interaction** with the system.

- **DO implement peer group analysis and year-over-year comparison** within existing framework without adding new command arguments.

- **DO use weighted scoring for skills by category** within the existing logic flows.

## Code Organization

- Base functionality in the `peopleanalytics` package
- CLI functionality in `peopleanalytics/cli.py` and `peopleanalytics/cli_commands/`
- Domain logic in `peopleanalytics/domain/`
- Talent development modules in `peopleanalytics/talent_development/`

## Data Processing Flow

1. Collect data from structured directories
2. Process data per person/year
3. Generate reports and visualizations
4. Generate talent development reports (9-box, career simulation, influence network)
5. Generate analysis reports (peer comparison, year-over-year)

## Enhancement Guidelines

When adding new features:
1. First understand the existing code structure thoroughly
2. Identify the appropriate location for new code (usually extending existing classes)
3. Follow established patterns in similar functionality
4. Reuse existing utility functions and classes
5. Ensure proper error handling and logging
6. Test with existing command-line parameters

## Guidelines Maintenance

This document should be updated whenever:
1. New lessons are learned about project requirements and constraints
2. New patterns or conventions are established
3. Significant changes to the architecture are approved
4. New "do's and don'ts" are identified during development

**Note**: This is a living document and should be updated with new learnings as the project evolves. 