def run_recipe(prediction_index):
    # Map model prediction indices to steps in a pasta cooking recipe
    recipe_steps = {
        0: 'Step 4: Your pasta is ready with Alfredo sauce.',
        1: 'Step 1: Start with an empty pan.',
        2: 'Step 2: Add pasta to the pan.',
        3: 'Step 3: Boil the pasta until it is cooked to your liking.',
    }

    # Look up the step corresponding to the model's prediction index
    instruction = recipe_steps.get(prediction_index, "Invalid prediction index.")

    return instruction
