# Talk's Development Process / Workflow

As of the 13th of September 2025, `Talk` was launched to the International Network as a **monolith application**, with the intention of scaling until there is an actual need to transform it into a **microservice architecture**.  

This document serves as a guide for all engineers & developers on the **development and deployment workflow** for `Talk`.  
It ensures that our processes remain **organized, consistent, and clear**.  

> **N.B.** Every process outlined here must be followed accordingly.


### Development Workflow (Push → Pull Requests)

- After each **sprint planning session**, tasks will be assigned on the **ClickUp board**.  
- Each task will have a **ticket ID** (e.g. `TD-01`).  
- Once you are done working on a task, you **must test locally** to ensure functionality and stability.  
- With a clear conscience after successful testing, create a **branch** named after your ticket ID and push your code.
- Raise a pull request from your **branch** (e.g. `TD-01`) to the test branch **develop**.
- Assign a developer in your niche(`Backend-Backend`/`Frontend-Frontend`) to review and merge.
- Change the status of your task on Clickup to **`IN TEST`**.
- Approved works are merged to the production branch **main** where it is made available to users.

### Git Flow
```bash
# Initialize repository (first time only)
git init

# Add remote repository
git remote add origin <repository-url>

# Create and switch to a new branch named after your ClickUp task ID
git checkout -b TD-01

# Stage changes
git add .

# Commit with a clear, descriptive message
git commit -m "TD-01: A summary of your code..."

# Push to remote repository
git push -u origin TD-01
```

### Deployment Workflow (development → production)

- All new features and fixes are merged into the **develop** branch after code review.

- The **develop** branch environment is for QA, testing, and validation.

- Once changes have been tested and approved on **develop**, they are merged into the main (or production) branch.

- The production branch is automatically deployed to the live environment for end users.

- Hotfixes (critical bug fixes) can be branched directly from production, tested, and merged back into both production and develop to keep branches in sync.

> Workflow Summary:
feature/task branch → Pull Request → develop tests → main/production → live deployment
How do I handle google sso on my django backend and React.Js frontend that interract via API calls