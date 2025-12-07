#!/usr/bin/env python3
"""
Maths Worksheet Generator for Primary School Children (Year 2 & 3)
Generates printable worksheets with addition, subtraction, multiplication, or division problems.
Creates both a worksheet and an answer key as PDF files using LaTeX.
"""

import random
import subprocess
import os
import sys
from datetime import datetime


def get_user_input():
    """Gather worksheet parameters from the user."""
    print("\n" + "=" * 50)
    print("    MATHS WORKSHEET GENERATOR")
    print("    For Primary School (Year 2 & 3)")
    print("=" * 50 + "\n")

    # Get operation type
    print("Select operation type:")
    print("  1. Addition (+)")
    print("  2. Subtraction (-)")
    print("  3. Multiplication (×)")
    print("  4. Division (÷)")

    while True:
        try:
            op_choice = int(input("\nEnter choice (1-4): "))
            if 1 <= op_choice <= 4:
                break
            print("Please enter a number between 1 and 4.")
        except ValueError:
            print("Please enter a valid number.")

    operations = {1: 'addition', 2: 'subtraction', 3: 'multiplication', 4: 'division'}
    operation = operations[op_choice]

    # Get number range
    print(f"\nEnter the range of numbers to use:")
    while True:
        try:
            min_num = int(input("  Minimum number (e.g., 0): "))
            max_num = int(input("  Maximum number (e.g., 20): "))
            if min_num < max_num:
                if operation == 'division' and min_num < 1:
                    print("  Note: For division, minimum will be set to 1 to avoid division by zero.")
                    min_num = 1
                break
            print("  Maximum must be greater than minimum.")
        except ValueError:
            print("  Please enter valid numbers.")

    # Get number of questions
    print(f"\nHow many questions would you like?")
    while True:
        try:
            num_questions = int(input("  Number of questions (e.g., 20): "))
            if num_questions > 0:
                break
            print("  Please enter a positive number.")
        except ValueError:
            print("  Please enter a valid number.")

    # Get student name (optional)
    student_name = input("\nStudent name (optional, press Enter to skip): ").strip()

    return {
        'operation': operation,
        'min_num': min_num,
        'max_num': max_num,
        'num_questions': num_questions,
        'student_name': student_name
    }


def generate_problem(operation, min_num, max_num):
    """Generate a single math problem and its answer."""
    if operation == 'addition':
        a = random.randint(min_num, max_num)
        b = random.randint(min_num, max_num)
        answer = a + b
        problem = f"{a} + {b}"

    elif operation == 'subtraction':
        # Ensure result is non-negative for young children
        a = random.randint(min_num, max_num)
        b = random.randint(min_num, a)  # b <= a to avoid negative answers
        answer = a - b
        problem = f"{a} - {b}"

    elif operation == 'multiplication':
        a = random.randint(min_num, max_num)
        b = random.randint(min_num, max_num)
        answer = a * b
        problem = f"{a} \\times {b}"

    elif operation == 'division':
        # Generate problems with whole number answers
        b = random.randint(max(1, min_num), max_num)  # Divisor (avoid 0)
        answer = random.randint(min_num, max_num)  # The answer we want
        a = b * answer  # Dividend
        problem = f"{a} \\div {b}"

    return problem, answer


def generate_problems(operation, min_num, max_num, num_questions):
    """Generate all problems for the worksheet."""
    problems = []
    for _ in range(num_questions):
        problem, answer = generate_problem(operation, min_num, max_num)
        problems.append((problem, answer))
    return problems


def get_operation_symbol(operation):
    """Get the display name for the operation."""
    symbols = {
        'addition': 'Addition (+)',
        'subtraction': 'Subtraction (-)',
        'multiplication': 'Multiplication (×)',
        'division': 'Division (÷)'
    }
    return symbols.get(operation, operation)


def generate_latex(problems, params, show_answers=False):
    """Generate LaTeX document content."""
    operation = params['operation']
    min_num = params['min_num']
    max_num = params['max_num']
    student_name = params['student_name']

    # Calculate columns based on number of problems
    num_problems = len(problems)
    if num_problems <= 12:
        columns = 3
    elif num_problems <= 24:
        columns = 4
    else:
        columns = 5

    # LaTeX document header
    latex = r"""\documentclass[12pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[margin=2cm]{geometry}
\usepackage{amsmath}
\usepackage{array}
\usepackage{multicol}
\usepackage{fancyhdr}
\usepackage{lastpage}

\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\footrulewidth}{0.4pt}
"""

    # Title based on whether it's worksheet or answers
    if show_answers:
        title = "ANSWER KEY"
        latex += r"\fancyhead[C]{\textbf{ANSWER KEY}}" + "\n"
    else:
        title = "MATHS WORKSHEET"
        latex += r"\fancyhead[C]{\textbf{MATHS WORKSHEET}}" + "\n"

    latex += r"\fancyfoot[C]{Page \thepage\ of \pageref{LastPage}}" + "\n"
    latex += r"\fancyfoot[R]{\small Generated: " + datetime.now().strftime("%d/%m/%Y") + "}\n"

    latex += r"""
\begin{document}

\begin{center}
{\LARGE \textbf{""" + title + r"""}}
\vspace{0.5cm}

{\large """ + get_operation_symbol(operation) + r"""}

{\normalsize Range: """ + str(min_num) + r""" -- """ + str(max_num) + r"""}
\end{center}

\vspace{0.3cm}
"""

    # Add student name field
    if student_name:
        latex += r"\noindent\textbf{Name:} " + student_name + r" \hfill \textbf{Date:} \rule{4cm}{0.4pt}" + "\n\n"
    else:
        latex += r"\noindent\textbf{Name:} \rule{6cm}{0.4pt} \hfill \textbf{Date:} \rule{4cm}{0.4pt}" + "\n\n"

    latex += r"\vspace{0.5cm}" + "\n\n"

    # Create problems in a tabular format
    latex += r"\begin{center}" + "\n"
    latex += r"\renewcommand{\arraystretch}{2.5}" + "\n"

    # Build the table
    col_spec = "|" + "r@{\\hspace{0.3cm}}l|" * columns
    latex += r"\begin{tabular}{" + col_spec + "}\n"
    latex += r"\hline" + "\n"

    # Fill in the problems
    row = []
    for i, (problem, answer) in enumerate(problems):
        q_num = i + 1
        if show_answers:
            cell = f"\\textbf{{{q_num}.}} ${problem}$ & $= {answer}$"
        else:
            cell = f"\\textbf{{{q_num}.}} ${problem}$ & $=$ \\rule{{1.5cm}}{{0.4pt}}"
        row.append(cell)

        # When we have enough for a row, or it's the last problem
        if len(row) == columns or i == len(problems) - 1:
            # Pad the row if needed
            while len(row) < columns:
                row.append(" & ")
            latex += " & ".join(row) + r" \\" + "\n"
            latex += r"\hline" + "\n"
            row = []

    latex += r"\end{tabular}" + "\n"
    latex += r"\end{center}" + "\n\n"

    # Add footer with instructions (only for worksheet, not answer key)
    if not show_answers:
        latex += r"""
\vfill
\begin{center}
\small\textit{Show your working out in the space provided. Good luck!}
\end{center}
"""

    latex += r"\end{document}" + "\n"

    return latex


def compile_latex(latex_content, output_filename):
    """Compile LaTeX content to PDF."""
    # Create temporary .tex file
    tex_filename = output_filename.replace('.pdf', '.tex')

    with open(tex_filename, 'w') as f:
        f.write(latex_content)

    # Compile with pdflatex (run twice for proper page references)
    try:
        for _ in range(2):
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', tex_filename],
                capture_output=True,
                text=True
            )

        if os.path.exists(output_filename):
            # Clean up auxiliary files
            base = output_filename.replace('.pdf', '')
            for ext in ['.aux', '.log', '.out']:
                aux_file = base + ext
                if os.path.exists(aux_file):
                    os.remove(aux_file)
            return True
        else:
            print(f"Error: PDF was not created. Check {tex_filename} for errors.")
            print(result.stdout)
            print(result.stderr)
            return False

    except FileNotFoundError:
        print("\nError: pdflatex not found. Please install a LaTeX distribution.")
        print("  On Ubuntu/Debian: sudo apt-get install texlive-latex-base texlive-latex-extra")
        print("  On Fedora: sudo dnf install texlive-scheme-basic texlive-lastpage")
        print("  On macOS: brew install --cask mactex")
        print(f"\nLaTeX source saved to: {tex_filename}")
        return False


def main():
    """Main program flow."""
    # Get user input
    params = get_user_input()

    # Generate problems
    print("\nGenerating problems...")
    problems = generate_problems(
        params['operation'],
        params['min_num'],
        params['max_num'],
        params['num_questions']
    )

    # Generate timestamp for unique filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"worksheet_{params['operation']}_{timestamp}"

    # Generate worksheet (without answers)
    print("Creating worksheet...")
    worksheet_latex = generate_latex(problems, params, show_answers=False)
    worksheet_pdf = f"{base_filename}.pdf"

    # Generate answer key
    print("Creating answer key...")
    answers_latex = generate_latex(problems, params, show_answers=True)
    answers_pdf = f"{base_filename}_answers.pdf"

    # Compile to PDF
    print("\nCompiling PDFs...")
    worksheet_success = compile_latex(worksheet_latex, worksheet_pdf)
    answers_success = compile_latex(answers_latex, answers_pdf)

    # Summary
    print("\n" + "=" * 50)
    print("GENERATION COMPLETE")
    print("=" * 50)
    print(f"Operation: {get_operation_symbol(params['operation'])}")
    print(f"Range: {params['min_num']} - {params['max_num']}")
    print(f"Questions: {params['num_questions']}")
    print()

    if worksheet_success:
        print(f"Worksheet: {worksheet_pdf}")
    else:
        print(f"Worksheet LaTeX: {base_filename}.tex")

    if answers_success:
        print(f"Answer Key: {answers_pdf}")
    else:
        print(f"Answer Key LaTeX: {base_filename}_answers.tex")

    print()


if __name__ == "__main__":
    main()
