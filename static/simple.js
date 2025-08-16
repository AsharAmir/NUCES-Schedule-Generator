// Simple Timetable App
class SimpleTimetableApp {
    constructor() {
        this.selectedSchool = 'computing'; // Default to computing since it's the only one available
        this.selectedCourses = [];
        this.courseSuggestions = [];
        this.highlightedIndex = -1;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.updateActiveTab();
        this.loadCourseSuggestions(); // Load after setting active tab
    }

    setupEventListeners() {
        // School tabs
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                if (e.target.classList.contains('disabled')) return;
                this.selectSchool(e.target.dataset.school);
            });
        });

        // Course input
        const courseInput = document.getElementById('courseInput');
        courseInput.addEventListener('input', (e) => this.handleInput(e));
        courseInput.addEventListener('keydown', (e) => this.handleKeyDown(e));
        courseInput.addEventListener('blur', () => {
            setTimeout(() => this.hideSuggestions(), 150);
        });

        // Form submission
        document.getElementById('timetableForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.generateTimetable();
        });

        // Click outside to hide suggestions
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.input-container')) {
                this.hideSuggestions();
            }
        });
    }

    selectSchool(school) {
        if (this.selectedSchool === school) return; // Don't reload if same school
        
        console.log(`Switching from ${this.selectedSchool} to ${school}`);
        this.selectedSchool = school;
        this.updateActiveTab();
        
        // Clear courses (use the method correctly)
        this.selectedCourses = [];
        this.renderSelectedCourses();
        document.getElementById('courseInput').value = '';
        
        // Clear existing suggestions and force reload
        this.courseSuggestions = [];
        this.hideSuggestions();
        
        // Force reload courses for new school
        this.loadCourseSuggestions();
    }

    updateActiveTab() {
        document.querySelectorAll('.tab').forEach(tab => {
            tab.classList.remove('active');
            if (tab.dataset.school === this.selectedSchool) {
                tab.classList.add('active');
            }
        });
    }

    async loadCourseSuggestions() {
        try {
            this.showLoading('Loading course suggestions...');
            // Add cache-busting parameter to force fresh data
            const response = await fetch(`/api/courses/${this.selectedSchool}?t=${Date.now()}`);
            const data = await response.json();
            
            if (response.ok) {
                this.courseSuggestions = data.courses;
                console.log(`Loaded ${data.count} courses for ${this.selectedSchool}:`, data.school);
                console.log('Sheet ID:', data.sheet_id);
                console.log('Sample courses:', data.courses.slice(0, 5));
            } else {
                console.error('Failed to load courses:', data.error);
            }
        } catch (error) {
            console.error('Error loading courses:', error);
        } finally {
            this.hideLoading();
        }
    }

    handleInput(e) {
        const query = e.target.value.trim();
        
        if (query.length < 1) {
            this.hideSuggestions();
            return;
        }

        // Find matching courses
        const matches = this.courseSuggestions.filter(course => {
            if (this.selectedCourses.includes(course)) return false;
            
            const courseLower = course.toLowerCase();
            const queryLower = query.toLowerCase();
            
            // Direct match
            if (courseLower.includes(queryLower)) return true;
            
            // Word-based matching
            const courseWords = course.split(/[\s\(\)\/\-]+/).filter(w => w.length > 0);
            return courseWords.some(word => word.toLowerCase().startsWith(queryLower));
        });

        // Sort by relevance
        matches.sort((a, b) => {
            const aLower = a.toLowerCase();
            const bLower = b.toLowerCase();
            const queryLower = query.toLowerCase();
            
            if (aLower.startsWith(queryLower) && !bLower.startsWith(queryLower)) return -1;
            if (!aLower.startsWith(queryLower) && bLower.startsWith(queryLower)) return 1;
            return a.length - b.length;
        });

        this.showSuggestions(matches.slice(0, 10)); // Show top 10 matches
    }

    handleKeyDown(e) {
        const suggestions = document.querySelectorAll('.suggestion-item');
        
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.highlightedIndex = Math.min(this.highlightedIndex + 1, suggestions.length - 1);
                this.updateHighlight();
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                this.highlightedIndex = Math.max(this.highlightedIndex - 1, -1);
                this.updateHighlight();
                break;
                
            case 'Enter':
                e.preventDefault();
                if (this.highlightedIndex >= 0 && suggestions[this.highlightedIndex]) {
                    this.selectCourse(suggestions[this.highlightedIndex].textContent);
                }
                break;
                
            case 'Escape':
                this.hideSuggestions();
                break;
        }
    }

    showSuggestions(suggestions) {
        const container = document.getElementById('suggestions');
        container.innerHTML = '';
        
        if (suggestions.length === 0) {
            container.innerHTML = '<div class="suggestion-item">No suggestions found</div>';
        } else {
            suggestions.forEach(suggestion => {
                const item = document.createElement('div');
                item.className = 'suggestion-item';
                item.textContent = suggestion;
                item.addEventListener('click', () => this.selectCourse(suggestion));
                container.appendChild(item);
            });
        }
        
        container.classList.add('show');
        this.highlightedIndex = -1;
    }

    hideSuggestions() {
        document.getElementById('suggestions').classList.remove('show');
        this.highlightedIndex = -1;
    }

    updateHighlight() {
        document.querySelectorAll('.suggestion-item').forEach((item, index) => {
            item.classList.toggle('highlighted', index === this.highlightedIndex);
        });
    }

    selectCourse(course) {
        if (!this.selectedCourses.includes(course)) {
            this.selectedCourses.push(course);
            this.renderSelectedCourses();
        }
        
        document.getElementById('courseInput').value = '';
        this.hideSuggestions();
    }

    removeCourse(course) {
        this.selectedCourses = this.selectedCourses.filter(c => c !== course);
        this.renderSelectedCourses();
    }

    renderSelectedCourses() {
        const container = document.getElementById('selectedCourses');
        container.innerHTML = '';

        this.selectedCourses.forEach(course => {
            const tag = document.createElement('div');
            tag.className = 'course-tag';
            tag.innerHTML = `
                <span>${course}</span>
                <button class="remove" onclick="app.removeCourse('${course.replace(/'/g, '\\\'')}')">&times;</button>
            `;
            container.appendChild(tag);
        });
    }

    async generateTimetable() {
        if (this.selectedCourses.length === 0) {
            alert('Please select at least one course');
            return;
        }

        try {
            this.showLoading('Generating your timetable...');
            
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    courses: this.selectedCourses,
                    school: this.selectedSchool
                })
            });

            const data = await response.json();

            if (response.ok) {
                this.renderTimetable(data);
                this.showTimetableSection();
            } else {
                alert('Error: ' + data.error);
            }
        } catch (error) {
            console.error('Failed to generate timetable:', error);
            alert('Failed to generate timetable: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }

    renderTimetable(data) {
        const { timetable, time_slots, days } = data;
        const table = document.getElementById('timetableTable');
        
        // Clear existing content
        table.innerHTML = '';

        // Create header row
        const headerRow = table.insertRow();
        headerRow.insertCell().outerHTML = '<th>Day / Time</th>';
        time_slots.forEach(time => {
            headerRow.insertCell().outerHTML = `<th>${time}</th>`;
        });

        // Create day rows
        days.forEach(day => {
            const row = table.insertRow();
            row.insertCell().outerHTML = `<td class="time-header">${day}</td>`;
            
            time_slots.forEach(time => {
                const cell = row.insertCell();
                const courses = timetable[day]?.[time] || '';
                
                if (courses) {
                    cell.className = 'course';
                    cell.innerHTML = courses.replace(/<br>/g, '<br>');
                } else {
                    cell.innerHTML = '';
                }
            });
        });
    }

    showTimetableSection() {
        const section = document.getElementById('timetableSection');
        section.style.display = 'block';
        section.scrollIntoView({ behavior: 'smooth' });
    }

    showLoading(message) {
        const loading = document.getElementById('loading');
        const text = loading.querySelector('.loading-text');
        text.textContent = message;
        loading.style.display = 'flex';
    }

    hideLoading() {
        document.getElementById('loading').style.display = 'none';
    }
}

// Global functions
function clearCourses() {
    app.selectedCourses = [];
    app.renderSelectedCourses();
    document.getElementById('courseInput').value = '';
    document.getElementById('courseInput').focus();
}

function editTimetable() {
    document.getElementById('courseInput').focus();
    document.getElementById('timetableSection').style.display = 'none';
}

function exportPNG() {
    const table = document.getElementById('timetableTable');
    html2canvas(table, {
        backgroundColor: '#222222',
        scale: 2
    }).then(canvas => {
        const link = document.createElement('a');
        link.download = `timetable_${new Date().getTime()}.png`;
        link.href = canvas.toDataURL();
        link.click();
    });
}

function exportPDF() {
    const table = document.getElementById('timetableTable');
    html2canvas(table, {
        backgroundColor: '#222222',
        scale: 2
    }).then(canvas => {
        const { jsPDF } = window.jspdf;
        const pdf = new jsPDF('landscape');
        const imgWidth = 280;
        const imgHeight = (canvas.height * imgWidth) / canvas.width;
        pdf.addImage(canvas.toDataURL('image/png'), 'PNG', 10, 10, imgWidth, imgHeight);
        pdf.save(`timetable_${new Date().getTime()}.pdf`);
    });
}

function printTimetable() {
    const printWindow = window.open('', '_blank');
    const table = document.getElementById('timetableTable').outerHTML;
    
    printWindow.document.write(`
        <html>
        <head>
            <title>FAST Timetable</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                table { width: 100%; border-collapse: collapse; }
                th, td { border: 1px solid #333; padding: 8px; text-align: center; }
                th { background: #f0f0f0; }
                .course { background: #f9f9f9; font-weight: bold; }
                .time-header { background: #e0e0e0; font-weight: bold; }
            </style>
        </head>
        <body>
            <h1>FAST Timetable (ISB CAMPUS)</h1>
            ${table}
        </body>
        </html>
    `);
    
    printWindow.document.close();
    printWindow.print();
}

function openEditModal() {
    document.getElementById('editModal').style.display = 'flex';
}

function closeEditModal() {
    document.getElementById('editModal').style.display = 'none';
}

// Initialize app
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new SimpleTimetableApp();
});