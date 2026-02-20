"""
LaTeX Handler - Generates LaTeX code (no local compilation needed)
"""
from agentstate import AgentState
from langchain_core.messages import HumanMessage


def escape_latex(text):
    """Escape special LaTeX characters in user input ONLY."""
    if not text:
        return ""
    
    text = str(text)
    
    replacements = [
        ('\\', r'\textbackslash{}'),
        ('%', r'\%'),
        ('#', r'\#'),
        ('_', r'\_'),
        ('{', r'\{'),
        ('}', r'\}'),
        ('~', r'\textasciitilde{}'),
        ('^', r'\textasciicircum{}'),
    ]
    
    for old, new in replacements:
        text = text.replace(old, new)
    
    if '\\&' not in text:
        text = text.replace('&', r'\&')
    
    return text


def generate_latex(state: AgentState) -> AgentState:
    """Generate LaTeX resume code from metadata"""
    
    metadata = state['resume_metadata']
    latex_template = get_latex_template()
    latex_code = latex_template
    
    # Basic info
    latex_code = latex_code.replace("{{NAME}}", escape_latex(metadata.name))
    latex_code = latex_code.replace("{{EMAIL}}", escape_latex(metadata.email))
    latex_code = latex_code.replace("{{PHONE}}", escape_latex(metadata.phone or "+91 1234567890"))
    latex_code = latex_code.replace("{{LINKEDIN}}", escape_latex(metadata.linkedin or "linkedin.com/in/yourprofile"))
    
    # ==================== EXPERIENCE ====================
    experience_latex = ""
    if metadata.experiences and len(metadata.experiences) > 0:
        for exp in metadata.experiences:
            company = escape_latex(exp.get('company', 'Company'))
            duration = escape_latex(exp.get('duration', 'Date'))
            role = escape_latex(exp.get('role', 'Role'))
            
            experience_latex += f"    \\resumeSubheading{{{company}}}{{{duration}}}{{{role}}}{{}}\\resumeItemListStart\n"
            
            for achievement in exp.get('achievements', []):
                experience_latex += f"        \\resumeItem{{{escape_latex(achievement)}}}\n"
            
            experience_latex += "    \\resumeItemListEnd\n\n"
    else:
        experience_latex = "    \\resumeSubheading{Add Your Experience Here}{Jan 2024 - Present}{Role}{}\\resumeItemListStart\n        \\resumeItem{Description of your work experience}\n    \\resumeItemListEnd\n\n"
    
    latex_code = latex_code.replace("{{EXPERIENCE}}", experience_latex)

    # ==================== EDUCATION ====================
    education_latex = ""
    if metadata.education and len(metadata.education) > 0:
        for edu in metadata.education:
            institution = escape_latex(edu.get('institution', 'Institution'))
            duration = escape_latex(edu.get('duration', 'Date'))
            degree = escape_latex(edu.get('degree', 'Degree'))
            
            education_latex += f"    \\resumeSubheading{{{institution}}}{{{duration}}}{{{degree}}}{{}}\\vspace{{-7pt}}\n"
    else:
        education_latex = "    \\resumeSubheading{Your University}{2020 - 2024}{Your Degree}{}\\vspace{-7pt}\n"
    
    latex_code = latex_code.replace("{{EDUCATION}}", education_latex)

    # ==================== PROJECTS ====================
    projects_latex = ""
    if metadata.projects and len(metadata.projects) > 0:
        for proj in metadata.projects:
            project_name = escape_latex(proj.get('name', 'Project'))
            tech_stack = ", ".join([escape_latex(str(t)) for t in proj.get('technologies', [])])
            date = escape_latex(proj.get('date', 'Date'))
            
            projects_latex += f"    \\resumeProjectHeading{{\\textbf{{{project_name}}} $|$ {tech_stack}}}{{{date}}}\\resumeItemListStart\n"
            
            for achievement in proj.get('achievements', []):
                projects_latex += f"      \\resumeItem{{{escape_latex(achievement)}}}\n"
            
            projects_latex += "    \\resumeItemListEnd\n"
    
    latex_code = latex_code.replace("{{PROJECTS}}", projects_latex)

    # ==================== TECHNICAL SKILLS ====================
    technical_skills_latex = ""
    if hasattr(metadata, 'technical_skills') and metadata.technical_skills:
        skills_list = []
        for category, skills in metadata.technical_skills.items():
            if skills:
                skills_str = ", ".join([escape_latex(str(s)) for s in skills])
                skills_list.append(f"\\textbf{{{escape_latex(category)}}}: {skills_str}")
        technical_skills_latex = " \\\\\n     ".join(skills_list)
    else:
        technical_skills_latex = "\\textbf{Languages}: Python, Java, C++ \\\\\n     \\textbf{Technologies}: React, Node.js, Docker"
    
    latex_code = latex_code.replace("{{TECHNICAL_SKILLS}}", technical_skills_latex)

    # ==================== POSITIONS OF RESPONSIBILITY ====================
    por_latex = ""
    if metadata.positions_of_responsibility and len(metadata.positions_of_responsibility) > 0:
        for por in metadata.positions_of_responsibility:
            organization = escape_latex(por.get('organization', 'Organization'))
            duration = escape_latex(por.get('duration', 'Date'))
            role = escape_latex(por.get('role', 'Role'))
            location = escape_latex(por.get('location', ''))
            description = escape_latex(por.get('description', ''))
            
            por_latex += f"        \\resumeSubheading{{{organization}}}{{{duration}}}{{{role}}}{{{location}}}\\resumeItemListStart\n"
            por_latex += f"            \\resumeItem{{{description}}}\n"
            por_latex += "        \\resumeItemListEnd\n\n"
    else:
        por_latex = "        \\resumeSubheading{Organization Name}{2022 - 2024}{Your Role}{}\\resumeItemListStart\n            \\resumeItem{Description of your responsibilities}\n        \\resumeItemListEnd\n\n"
    
    latex_code = latex_code.replace("{{POSITIONS}}", por_latex)
    
    return {
        **state,
        "latex_code": latex_code,
        "messages": [HumanMessage(content="Generated LaTeX code")]
    }


def get_latex_template():
    """Overleaf-compatible template - no double braces in static LaTeX"""
    return r"""%-------------------------
% Resume in Latex
%------------------------

\documentclass[letterpaper,11pt]{article}

\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage[english]{babel}
\usepackage{tabularx}
\usepackage{fontawesome5}
\usepackage{multicol}
\setlength{\multicolsep}{-3.0pt}
\setlength{\columnsep}{-1pt}
\input{glyphtounicode}

\pagestyle{fancy}
\fancyhf{}
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

% Adjust margins
\addtolength{\oddsidemargin}{-0.6in}
\addtolength{\evensidemargin}{-0.5in}
\addtolength{\textwidth}{1.19in}
\addtolength{\topmargin}{-.7in}
\addtolength{\textheight}{1.4in}

\urlstyle{same}

\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

% Sections formatting
\titleformat{\section}{\vspace{-4pt}\scshape\raggedright\large\bfseries}{}{0em}{}[\color{black}\titlerule\vspace{-5pt}]

% Ensure that generate pdf is machine readable/ATS parsable
\pdfgentounicode=1

%-------------------------
% Custom commands
\newcommand{\resumeItem}[1]{
  \item\small{
    {#1 \vspace{-2pt}}
  }
}

\newcommand{\resumeSubheading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{1.0\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & \textbf{\small #2} \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeProjectHeading}[2]{
    \item
    \begin{tabular*}{1.001\textwidth}{l@{\extracolsep{\fill}}r}
      \small#1 & \textbf{\small #2}\\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSubItem}[1]{\resumeItem{#1}\vspace{-4pt}}

\renewcommand\labelitemi{$\vcenter{\hbox{\tiny$\bullet$}}$}
\renewcommand\labelitemii{$\vcenter{\hbox{\tiny$\bullet$}}$}

\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.0in, label={}]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{\begin{itemize}}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}

%-------------------------------------------
%%%%%%  RESUME STARTS HERE  %%%%%%%%%%%%%%%%%%%%%%%%%%%%

\begin{document}

%----------HEADING----------
\begin{center}
    {\Huge \scshape {{NAME}}} \\ \vspace{2pt}
    \small \raisebox{-0.1\height}\faPhone\ {{PHONE}} ~ \href{mailto:{{EMAIL}}}{\raisebox{-0.2\height}\faEnvelope\ {{EMAIL}}} ~ 
    \href{https://{{LINKEDIN}}}{\raisebox{-0.2\height}\faLinkedin\ LinkedIn}
\end{center}

%-----------EXPERIENCE-----------
\section{Experience}
  \resumeSubHeadingListStart
{{EXPERIENCE}}  \resumeSubHeadingListEnd
\vspace{-16pt}

%-----------EDUCATION-----------
\section{Education}
  \resumeSubHeadingListStart
{{EDUCATION}}  \resumeSubHeadingListEnd

%-----------PROJECTS-----------
\section{Projects}
    \resumeSubHeadingListStart
{{PROJECTS}}    \resumeSubHeadingListEnd
\vspace{-16pt}

%-----------TECHNICAL SKILLS-----------
\section{Technical Skills}
 \begin{itemize}[leftmargin=0.15in, label={}]
    \item{
     {{TECHNICAL_SKILLS}}
    }
 \end{itemize}
 \vspace{-16pt}

%-----------INVOLVEMENT---------------
\section{Position of Responsibility}
    \resumeSubHeadingListStart
{{POSITIONS}}    \resumeSubHeadingListEnd

\end{document}
"""