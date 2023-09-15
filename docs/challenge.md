
# Workflow
1. Install make in the server/local machine
2. Install git in the server/local machine
3. Clone the repository
4. Push all project files into `main` branch
5. Create `dev` branch from `main` branch
6. Git fetch and checkout `dev` branch
7. Execute `make venv` to create a virtual environment
8. activate the virtual environment
9. Execute `make install` to install all dependencies
10. Test all imports in `exploration.ipynb` file
11. Add `workflow` section and `fixes` section to challenge.md file
12. Git add, commit and push all changes to `dev` branch

# Fixes
* Add `xgboost` library to `requirements.txt` file