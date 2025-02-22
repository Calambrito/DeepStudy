from PyPDF2 import PdfWriter

def parse_schedule(schedule_file):
    with open(schedule_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    schedule = {}
    current_week = ""
    for line in lines:
        line = line.strip()
        if line.startswith("Week"):
            current_week = line
            schedule[current_week] = []
        elif "$" in line:
            parts = line.split("$", 1)
            course_code = parts[0].strip()
            topics = parts[1].replace("[", "").replace("]", "").split(",")
            topics = [t.strip() for t in topics]
            schedule[current_week].append((course_code, topics))
    return schedule

def get_sieve_courses(sieve_file):
    with open(sieve_file, 'r', encoding='utf-8') as file:
        return set(file.read().strip().split(","))

def filter_schedule(schedule, courses):
    filtered = {}
    for week, entries in schedule.items():
        filtered_entries = [(course, topics) for course, topics in entries if course in courses]
        if filtered_entries:
            filtered[week] = filtered_entries
    return filtered

def build_pdf(schedule, output_file):
    from fpdf import FPDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for week, entries in schedule.items():
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 8, "@", ln=True, align='L')
        pdf.set_font("Arial", style='B', size=14)
        pdf.cell(200, 8, week, ln=True, align='L')
        pdf.set_font("Arial", size=12)
        for course, topics in entries:
            content_line = f"{course}: {', '.join(topics)}"
            pdf.cell(200, 6, content_line, ln=True, align='L')
        pdf.cell(200, 8, "@", ln=True, align='L')
        pdf.ln(3)
    pdf.output(output_file)

if __name__ == "__main__":
    schedule = parse_schedule("rawdata/schedule.txt")
    sieve_courses = get_sieve_courses("rawdata/sieve.txt")
    filtered_schedule = filter_schedule(schedule, sieve_courses)
    build_pdf(filtered_schedule, "data/filtered_schedule.pdf")
    print("PDF generated successfully as data/filtered_schedule.pdf")