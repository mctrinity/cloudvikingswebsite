import sass # type: ignore

# Define the input and output directories
scss_input = 'static/scss/custom-bootstrap.scss'  # Adjusted for root-level static folder
css_output = 'static/css/custom-bootstrap.css'    # Adjusted for root-level static folder

# Compile SCSS to CSS
compiled_css = sass.compile(filename=scss_input)

# Write the compiled CSS to the output file
with open(css_output, 'w') as f:
    f.write(compiled_css)

print(f"SCSS compiled to {css_output}")
