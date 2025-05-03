document.addEventListener("DOMContentLoaded", () => {
    const courseSubjects = {
        "Python Full Stack": ["Python Programming", "Frontend", "SQL"],
        "Java Full Stack": ["Java Programming", "Frontend", "SQL"],
        "Data Science": ["Data Science", "Excel", "SQL", "Python Programming", "Machine Learning"],
        "Data Analytics": ["Excel", "Power BI", "SQL", "Statistics"],
        "DevOps cum AWS": ["Linux", "Docker", "Kubernetes", "AWS Services"],
        "Cyber Security": ["Networking", "Firewalls", "Ethical Hacking"],
        "Communication": ["Spoken English", "Soft Skills", "Presentation"],
        "Aptitude": ["Quantitative", "Logical Reasoning", "Verbal Ability"]
    };

    const courseSelect = document.getElementById("courses");
    const subjectCheckboxes = document.getElementById("subjectCheckboxes");

    if (courseSelect && subjectCheckboxes) {
        courseSelect.addEventListener("change", () => {
            const selectedCourse = courseSelect.value;
            subjectCheckboxes.innerHTML = "";

            if (courseSubjects[selectedCourse]) {
                courseSubjects[selectedCourse].forEach(subject => {
                    const label = document.createElement("label");
                    label.className = "checkbox-label";

                    const checkbox = document.createElement("input");
                    checkbox.type = "checkbox";
                    checkbox.name = "subjects";
                    checkbox.value = subject;
                    label.appendChild(checkbox);
                    label.append(" " + subject);
                    subjectCheckboxes.appendChild(label);
                    subjectCheckboxes.appendChild(document.createElement("br"));
                });
            }
        });
    }
});