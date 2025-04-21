from fpdf import FPDF
import sqlite3

conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

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

def update_sieve_courses(username, sieve_file):
    cursor.execute(f"SELECT course from USERCOURSES WHERE username='{username}'")
    rows = cursor.fetchall()
    courses = [r[0] for r in rows]
    courses_text = ",".join(courses)
    print(courses_text)
    with open(sieve_file, 'w', encoding='utf-8') as file:
        file.write(courses_text)

def filter_schedule(schedule, courses):
    filtered = {}
    for week, entries in schedule.items():
        filtered_entries = [(course, topics) for course, topics in entries if course in courses]
        if filtered_entries:
            filtered[week] = filtered_entries
    return filtered

def build_pdf(schedule, output_file):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()
    pdf.add_font('DejaVu', '', "DejaVuSans.ttf", uni=True)
    pdf.add_font('DejaVu', 'B', "DejaVuSans.ttf", uni=True)
    pdf.set_font("DejaVu", size=12)
    for week, entries in schedule.items():
        pdf.set_font("DejaVu", size=12)
        pdf.cell(200, 8, "@", ln=True, align='L')
        pdf.set_font("DejaVu", style='B', size=14)
        pdf.cell(200, 8, week, ln=True, align='L')
        pdf.set_font("DejaVu", size=12)
        for course, topics in entries:
            content_line = f"{course}: {', '.join(topics)}"
            pdf.cell(200, 6, content_line, ln=True, align='L')
        pdf.cell(200, 8, "@", ln=True, align='L')
        pdf.ln(3)
    pdf.output(output_file)


# testing
if __name__ == "__main__":
    schedule = parse_schedule("rawdata/schedule.txt")
    update_sieve_courses("nosef", "rawdata/sieve.txt")
    sieve_courses = get_sieve_courses("rawdata/sieve.txt")
    filtered_schedule = filter_schedule(schedule, sieve_courses)
    print(sieve_courses)
    build_pdf(filtered_schedule, "data/filtered_schedule.pdf")
    print("PDF generated successfully as data/filtered_schedule.pdf")